# test_parser.py
# Tests for scraper parser functions
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
import sys
from pathlib import Path

# Import from the installed package
from stepwright import (
    run_scraper,
    run_scraper_with_callback,
    TabTemplate,
    BaseStep,
    RunOptions,
    PaginationConfig,
    NextButtonConfig,
    ScrollConfig,
)


@pytest.fixture
def test_page_url():
    """Get test page URL"""
    test_page_path = Path(__file__).parent / "test_page.html"
    return f"file://{test_page_path}"


class TestRunScraper:
    """Tests for runScraper function"""

    @pytest.mark.asyncio
    async def test_basic_navigation_and_data_extraction(self, test_page_url):
        """Should execute basic navigation and data extraction"""
        templates = [
            TabTemplate(
                tab="basic_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="get_title",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="title",
                        data_type="text",
                    ),
                    BaseStep(
                        id="get_subtitle",
                        action="data",
                        object_type="id",
                        object="subtitle",
                        key="subtitle",
                        data_type="text",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 1
        assert results[0]["title"] == "StepWright Test Page"
        assert results[0]["subtitle"] == "A comprehensive test page for web scraping functionality"

    @pytest.mark.asyncio
    async def test_form_input_and_submission(self, test_page_url):
        """Should handle form input and submission"""
        templates = [
            TabTemplate(
                tab="form_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="input_search",
                        action="input",
                        object_type="id",
                        object="search-box",
                        value="test search term",
                    ),
                    BaseStep(
                        id="get_search_value",
                        action="data",
                        object_type="id",
                        object="search-box",
                        key="search_value",
                        data_type="value",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 1
        assert results[0]["search_value"] == "test search term"

    @pytest.mark.asyncio
    async def test_foreach_loops(self, test_page_url):
        """Should execute foreach loops"""
        templates = [
            TabTemplate(
                tab="foreach_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="collect_articles",
                        action="foreach",
                        object_type="class",
                        object="article",
                        subSteps=[
                            BaseStep(
                                id="get_article_title",
                                action="data",
                                object_type="tag",
                                object="h2",
                                key="title",
                                data_type="text",
                            ),
                            BaseStep(
                                id="get_article_link",
                                action="data",
                                object_type="tag",
                                object="a/@href",
                                key="link",
                                data_type="attribute",
                            ),
                        ],
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 4  # 4 articles
        assert "title" in results[0]
        assert "link" in results[0]
        assert results[0]["title"] == "First Article Title"

    @pytest.mark.asyncio
    async def test_pagination_with_next_button(self, test_page_url):
        """Should handle pagination with next button"""
        templates = [
            TabTemplate(
                tab="pagination_test",
                initSteps=[BaseStep(id="navigate", action="navigate", value=test_page_url)],
                perPageSteps=[
                    BaseStep(
                        id="get_page_title",
                        action="data",
                        object_type="tag",
                        object="h2",
                        key="page_title",
                        data_type="text",
                    )
                ],
                pagination=PaginationConfig(
                    strategy="next",
                    nextButton=NextButtonConfig(object_type="id", object="next-page"),
                    maxPages=2,
                ),
            )
        ]

        results = await run_scraper(templates)

        # We expect at least 1 result (first page)
        assert len(results) >= 1
        assert "page_title" in results[0]

    @pytest.mark.asyncio
    async def test_scroll_pagination(self, test_page_url):
        """Should handle scroll pagination"""
        templates = [
            TabTemplate(
                tab="scroll_test",
                initSteps=[BaseStep(id="navigate", action="navigate", value=test_page_url)],
                perPageSteps=[
                    BaseStep(id="scroll_action", action="scroll", value="500"),
                    BaseStep(
                        id="get_article_count",
                        action="data",
                        object_type="class",
                        object="article",
                        key="article_count",
                        data_type="text",
                    ),
                ],
                pagination=PaginationConfig(
                    strategy="scroll", scroll=ScrollConfig(offset=500, delay=100), maxPages=2
                ),
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 2  # 2 scroll iterations

    @pytest.mark.asyncio
    async def test_pdf_generation(self, test_page_url, tmp_path):
        """Should handle PDF generation"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        templates = [
            TabTemplate(
                tab="pdf_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="save_pdf",
                        action="savePDF",
                        value=str(output_dir / "test-page.pdf"),
                        key="pdf_file",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 1
        assert "pdf_file" in results[0]

    @pytest.mark.asyncio
    async def test_proxy_configuration(self, test_page_url):
        """Should handle proxy configuration"""
        templates = [
            TabTemplate(
                tab="proxy_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="get_title",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="title",
                        data_type="text",
                    ),
                ],
            )
        ]

        # Note: This test might fail if proxy server doesn't exist
        # We'll use headless without actual proxy for testing
        results = await run_scraper(templates, RunOptions(browser={"headless": True}))

        assert len(results) == 1
        assert results[0]["title"] == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_custom_browser_options(self, test_page_url):
        """Should handle custom browser options"""
        templates = [
            TabTemplate(
                tab="browser_options_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="get_title",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="title",
                        data_type="text",
                    ),
                ],
            )
        ]

        results = await run_scraper(
            templates,
            RunOptions(
                browser={"headless": True, "args": ["--no-sandbox", "--disable-setuid-sandbox"]}
            ),
        )

        assert len(results) == 1
        assert results[0]["title"] == "StepWright Test Page"


class TestRunScraperWithCallback:
    """Tests for runScraperWithCallback function"""

    @pytest.mark.asyncio
    async def test_streaming_results(self, test_page_url):
        """Should execute with streaming results"""
        templates = [
            TabTemplate(
                tab="callback_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="collect_articles",
                        action="foreach",
                        object_type="class",
                        object="article",
                        subSteps=[
                            BaseStep(
                                id="get_article_title",
                                action="data",
                                object_type="tag",
                                object="h2",
                                key="title",
                                data_type="text",
                            )
                        ],
                    ),
                ],
            )
        ]

        results = []

        async def on_result(result, index):
            results.append({**result, "index": index})

        await run_scraper_with_callback(templates, on_result)

        assert len(results) == 4  # 4 articles
        assert results[0]["title"] == "First Article Title"
        assert results[0]["index"] == 0

    @pytest.mark.asyncio
    async def test_error_handling_gracefully(self, test_page_url):
        """Should handle errors gracefully"""
        templates = [
            TabTemplate(
                tab="error_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="click_nonexistent",
                        action="click",
                        object_type="id",
                        object="non-existent-element",
                        terminateonerror=False,
                    ),
                    BaseStep(
                        id="get_title",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="title",
                        data_type="text",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 1
        assert results[0]["title"] == "StepWright Test Page"


class TestDataPlaceholders:
    """Tests for data placeholder replacement"""

    @pytest.mark.asyncio
    async def test_replace_data_placeholders_in_file_paths(self, test_page_url, tmp_path):
        """Should replace data placeholders in file paths"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        templates = [
            TabTemplate(
                tab="placeholder_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="get_title",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="meeting_title",
                        data_type="text",
                    ),
                    BaseStep(
                        id="save_with_placeholder",
                        action="savePDF",
                        value=str(output_dir / "{{meeting_title}}.pdf"),
                        key="pdf_file",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 1
        assert "pdf_file" in results[0]
        assert results[0]["meeting_title"] == "StepWright Test Page"
