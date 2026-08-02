# test_parser.py
# Tests for scraper parser functions
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
import sys
import json
from unittest.mock import AsyncMock, MagicMock

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
import stepwright.parser as parser_module


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

    def test_template_serialization_and_invalid_sources(self, tmp_path):
        step = BaseStep(id="plain", action="navigate", value="https://example.com")
        plain_path = tmp_path / "plain.json"
        saved = parser_module.save_template({"raw": True}, plain_path)
        assert json.loads(saved) == {"raw": True}
        assert json.loads(parser_module.template_to_json([step, {"raw": True}]))[1] == {"raw": True}
        assert parser_module.load_template(json.dumps({"type": "tab", "tab": "raw", "steps": []})).tab == "raw"
        with pytest.raises(ValueError):
            parser_module.load_template(42)

    @pytest.mark.asyncio
    async def test_parameterized_template_injects_all_step_groups(self, monkeypatch):
        calls = []

        async def fake_execute(page, tmpl, *args, **kwargs):
            calls.append(tmpl)
            return [{"ok": True}]

        browser = MagicMock()
        browser.close = AsyncMock()
        context = MagicMock()
        page = MagicMock()
        browser.new_context = AsyncMock(return_value=context)
        context.new_page = AsyncMock(return_value=page)
        page.close = AsyncMock()
        context.close = AsyncMock()
        monkeypatch.setattr(parser_module, "get_browser", AsyncMock(return_value=browser))
        monkeypatch.setattr(parser_module, "execute_tab", fake_execute)
        monkeypatch.setattr(parser_module, "_shutdown_playwright", AsyncMock())

        template = TabTemplate(
            tab="tab-{{value}}",
            steps=[BaseStep(id="s", action="input", value="{{value}}")],
            initSteps=[BaseStep(id="i", action="input", value="{{value}}")],
            perPageSteps=[BaseStep(id="p", action="input", value="{{value}}")],
        )
        wrapped = parser_module.ParameterizedTemplate(template=template, parameter_key="value", values=["x"], max_concurrency=1)
        result = await parser_module.run_scraper([wrapped], options=RunOptions())
        assert result == [{"ok": True}]
        assert calls[0].tab == "tab-x"
        assert calls[0].steps[0].value == "x"
        assert calls[0].initSteps[0].value == "x"
        assert calls[0].perPageSteps[0].value == "x"

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


class TestBuildContextArgs:
    """Tests for _build_context_args helper in parser.py"""

    @pytest.mark.asyncio
    async def test_build_context_args_options_and_tmpl(self):
        from stepwright.parser import _build_context_args

        options = RunOptions(
            user_agent="AgentX",
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            geolocation={"latitude": 48.8566, "longitude": 2.3522},
            permissions=["geolocation"],
            is_mobile=True,
            device="iPhone 12"
        )
        tmpl = TabTemplate(
            tab="test_ctx",
            user_agent="AgentY",
            is_mobile=False
        )

        ctx = await _build_context_args(options, tmpl)
        assert ctx["user_agent"] == "AgentY"
        assert ctx["viewport"] == {"width": 1920, "height": 1080}
        assert ctx["locale"] == "fr-FR"
        assert ctx["timezone_id"] == "Europe/Paris"
        assert ctx["geolocation"] == {"latitude": 48.8566, "longitude": 2.3522}
        assert ctx["permissions"] == ["geolocation"]
        assert ctx["is_mobile"] is False

    @pytest.mark.asyncio
    async def test_build_context_args_proxy_config(self):
        from stepwright.parser import _build_context_args
        from stepwright.step_types import ProxyConfig

        p_cfg = ProxyConfig(server="http://proxy.example.com:8080", username="user", password="pass", bypass=".example.com")
        options = RunOptions(proxy=p_cfg)
        ctx = await _build_context_args(options, None)
        assert "proxy" in ctx
        assert ctx["proxy"]["server"] == "http://proxy.example.com:8080"
        assert ctx["proxy"]["username"] == "user"
        assert ctx["proxy"]["password"] == "pass"
        assert ctx["proxy"]["bypass"] == ".example.com"

    @pytest.mark.asyncio
    async def test_build_context_args_proxy_pool_and_extra_headers(self):
        from stepwright.parser import _build_context_args
        from stepwright.proxy_pool import ProxyPool

        pool = ProxyPool(proxies=["http://p1.com:8080", "http://p2.com:8080"])
        options = RunOptions(
            proxy_pool=pool,
            extra_http_headers={"X-Test": "HeaderVal"},
            has_touch=True
        )
        tmpl = TabTemplate(tab="tab_pool", proxy_pool=["http://p3.com:8080"])

        ctx = await _build_context_args(options, tmpl)
        assert "proxy" in ctx
        assert ctx["proxy"]["server"] == "http://p3.com:8080"
        assert ctx["extra_http_headers"] == {"X-Test": "HeaderVal"}
        assert ctx["has_touch"] is True

