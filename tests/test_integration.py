# test_integration.py
# Integration tests for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
import sys
from pathlib import Path

# Import from the installed package
from stepwright import run_scraper, run_scraper_with_callback, TabTemplate, BaseStep, PaginationConfig, NextButtonConfig


@pytest.fixture
def test_page_url():
    """Get test page URL"""
    test_page_path = Path(__file__).parent / "test_page.html"
    return f"file://{test_page_path}"


class TestCompleteNewsScrapingScenario:
    """Complete news scraping scenario tests"""

    @pytest.mark.asyncio
    async def test_scrape_news_articles_with_pagination(self, test_page_url, tmp_path):
        """Should scrape news articles with pagination and save results"""
        output_dir = tmp_path / "integration-output"
        output_dir.mkdir()

        templates = [
            TabTemplate(
                tab="news_scraper",
                initSteps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="search_news",
                        action="input",
                        object_type="id",
                        object="search-box",
                        value="technology",
                    ),
                ],
                perPageSteps=[
                    BaseStep(
                        id="collect_articles",
                        action="foreach",
                        object_type="class",
                        object="article",
                        subSteps=[
                            BaseStep(
                                id="get_title",
                                action="data",
                                object_type="tag",
                                object="h2",
                                key="title",
                                data_type="text",
                            ),
                            BaseStep(
                                id="get_content",
                                action="data",
                                object_type="tag",
                                object="p",
                                key="content",
                                data_type="text",
                            ),
                            BaseStep(
                                id="get_link",
                                action="data",
                                object_type="tag",
                                object="a/@href",
                                key="link",
                                data_type="attribute",
                            ),
                            BaseStep(
                                id="get_nested_content",
                                action="data",
                                object_type="class",
                                object="nested-item",
                                key="nested_content",
                                data_type="text",
                            ),
                        ],
                    ),
                    BaseStep(
                        id="save_page_pdf",
                        action="savePDF",
                        value=str(output_dir / "page_{{i}}.pdf"),
                        key="page_pdf",
                    ),
                ],
                pagination=PaginationConfig(
                    strategy="next",
                    nextButton=NextButtonConfig(object_type="id", object="next-page"),
                    maxPages=2,
                ),
            )
        ]

        results = await run_scraper(templates)

        # We expect at least 4 results (first page)
        assert len(results) >= 4

        # Check first article
        assert "title" in results[0]
        assert "content" in results[0]
        assert "link" in results[0]
        assert "nested_content" in results[0]

        # Check that we have articles from the first page
        assert results[0]["title"] == "First Article Title"

    @pytest.mark.asyncio
    async def test_streaming_results_with_real_time_processing(self, test_page_url):
        """Should handle streaming results with real-time processing"""
        templates = [
            TabTemplate(
                tab="streaming_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="collect_articles",
                        action="foreach",
                        object_type="class",
                        object="article",
                        subSteps=[
                            BaseStep(
                                id="get_title",
                                action="data",
                                object_type="tag",
                                object="h2",
                                key="title",
                                data_type="text",
                            ),
                            BaseStep(
                                id="get_content",
                                action="data",
                                object_type="tag",
                                object="p",
                                key="content",
                                data_type="text",
                            ),
                        ],
                    ),
                ],
            )
        ]

        processed_results = []

        async def on_result(result, index):
            # Simulate real-time processing
            from datetime import datetime

            processed = {
                **result,
                "processed_at": datetime.now().isoformat(),
                "index": index,
                "word_count": (
                    len(result.get("content", "").split()) if result.get("content") else 0
                ),
            }
            processed_results.append(processed)

        await run_scraper_with_callback(templates, on_result)

        assert len(processed_results) == 4
        assert "processed_at" in processed_results[0]
        assert "word_count" in processed_results[0]
        assert processed_results[0]["index"] == 0

    @pytest.mark.asyncio
    async def test_complex_form_interactions_and_data_extraction(self, test_page_url):
        """Should handle complex form interactions and data extraction"""
        templates = [
            TabTemplate(
                tab="form_interaction_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="fill_search",
                        action="input",
                        object_type="id",
                        object="search-box",
                        value="automation testing",
                    ),
                    BaseStep(
                        id="select_category",
                        action="click",
                        object_type="id",
                        object="category-select",
                    ),
                    BaseStep(
                        id="wait_for_dynamic_content",
                        action="data",
                        object_type="class",
                        object="dynamic-content",
                        key="dynamic_content",
                        data_type="text",
                        wait=1500,
                    ),
                    BaseStep(
                        id="show_hidden_content",
                        action="click",
                        object_type="id",
                        object="show-hidden",
                    ),
                    BaseStep(
                        id="get_hidden_content",
                        action="data",
                        object_type="id",
                        object="hidden-content",
                        key="hidden_content",
                        data_type="text",
                    ),
                    BaseStep(
                        id="get_form_data",
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
        assert results[0]["search_value"] == "automation testing"
        assert "hidden_content" in results[0]
        assert "Hidden Content" in results[0]["hidden_content"]

    @pytest.mark.asyncio
    async def test_file_operations_and_downloads(self, test_page_url, tmp_path):
        """Should handle file operations and downloads"""
        download_dir = tmp_path / "integration-downloads"
        output_dir = tmp_path / "integration-output"

        download_dir.mkdir()
        output_dir.mkdir()

        templates = [
            TabTemplate(
                tab="file_operations_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=test_page_url),
                    BaseStep(
                        id="get_page_title",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="page_title",
                        data_type="text",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)

        assert len(results) == 1
        assert results[0]["page_title"] == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_proxy_and_custom_browser_configurations(self, test_page_url):
        """Should handle proxy and custom browser configurations"""
        templates = [
            TabTemplate(
                tab="proxy_config_test",
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
                        id="get_user_agent",
                        action="data",
                        object_type="tag",
                        object="title",
                        key="page_title",
                        data_type="text",
                    ),
                ],
            )
        ]

        from stepwright import RunOptions

        results = await run_scraper(
            templates,
            RunOptions(
                browser={
                    "headless": True,
                    "args": [
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-accelerated-2d-canvas",
                        "--no-first-run",
                        "--no-zygote",
                        "--disable-gpu",
                    ],
                }
            ),
        )

        assert len(results) == 1
        assert results[0]["title"] == "StepWright Test Page"
        assert results[0]["page_title"] == "StepWright Test Page"
