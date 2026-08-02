# tests/test_drivers.py
# Unit tests for Pluggable Driver Architecture in StepWright

import pytest
from stepwright import (
    BaseDriver,
    PlaywrightDriver,
    get_driver,
    TabTemplate,
    BaseStep,
    RunOptions,
    validate_template_format,
    run_scraper,
)


class MockDriver(BaseDriver):
    """Mock driver implementation for testing interface contract"""

    async def launch(self, options=None): pass
    async def new_context(self, options=None): pass
    async def new_page(self, context=None): pass
    async def close_page(self, page): pass
    async def close_context(self, context): pass
    async def close_browser(self, browser=None): pass
    async def shutdown(self): pass
    async def goto(self, page, url, wait_until="networkidle", timeout=None): pass
    async def reload(self, page, options=None): pass
    async def get_title(self, page): return "Mock Title"
    async def get_url(self, page): return "https://mock.local"
    async def wait_for_timeout(self, page, milliseconds): pass
    async def wait_for_load_state(self, page, state="load", timeout=None): pass
    async def locator(self, context, selector): return None
    async def click(self, locator, options=None): pass
    async def dblclick(self, locator, options=None): pass
    async def check(self, locator, options=None): pass
    async def fill(self, locator, value, options=None): pass
    async def type(self, locator, text, delay=0): pass
    async def clear(self, locator, options=None): pass
    async def hover(self, locator, options=None): pass
    async def select_option(self, locator, values, options=None): pass
    async def drag_to(self, source_locator, target_locator, options=None): pass
    async def set_input_files(self, locator, files, options=None): pass
    async def text_content(self, locator): return "mock content"
    async def inner_html(self, locator): return "<span>mock</span>"
    async def inner_text(self, locator): return "mock"
    async def input_value(self, locator): return ""
    async def get_attribute(self, locator, name): return None
    async def count(self, locator): return 0
    async def nth(self, locator, index): return None
    async def first(self, locator): return None
    async def scroll_into_view(self, locator): pass
    async def is_visible(self, locator): return True
    async def is_enabled(self, locator): return True
    async def evaluate(self, context, expression, arg=None): return True
    async def screenshot(self, page_or_locator, options=None): return b"mock_png"
    async def wait_for_selector(self, context, selector, options=None): return None
    async def frame_locator(self, context, selector): return None


def test_driver_resolver():
    """Test get_driver resolver factory"""
    d1 = get_driver("playwright")
    assert isinstance(d1, PlaywrightDriver)

    mock = MockDriver()
    d2 = get_driver(mock)
    assert d2 is mock

    with pytest.raises(ValueError, match="Unsupported driver"):
        get_driver("invalid_driver_name")


def test_validator_driver_check():
    """Test validator verification for custom drivers"""
    mock = MockDriver()

    t_valid = TabTemplate(
        tab="valid_driver",
        driver=mock,
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    assert validate_template_format(t_valid).is_valid is True

    t_invalid = TabTemplate(
        tab="invalid_driver",
        driver=12345,  # invalid (not str or BaseDriver)
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    res = validate_template_format(t_invalid)
    assert res.is_valid is False
    assert any(e.code == "INVALID_DRIVER" for e in res.errors)


@pytest.mark.asyncio
async def test_custom_driver_execution(test_page_html_path):
    """Test execution with PlaywrightDriver subclass"""
    file_url = f"file://{test_page_html_path}"

    class TestPlaywrightDriver(PlaywrightDriver):
        def __init__(self):
            super().__init__()
            self.goto_count = 0

        async def goto(self, page, url, wait_until="networkidle", timeout=None):
            self.goto_count += 1
            await super().goto(page, url, wait_until=wait_until, timeout=timeout)

    drv = TestPlaywrightDriver()
    template = TabTemplate(
        tab="driver_exec_test",
        driver=drv,
        steps=[
            BaseStep(id="s1", action="navigate", value=file_url),
            BaseStep(id="s2", action="getTitle", key="page_title"),
        ],
    )

    results = await run_scraper([template], RunOptions(browser={"headless": True}))
    assert len(results) > 0
    assert drv.goto_count == 1


class DummyBaseDriver(BaseDriver):
    async def launch(self, options=None): return await super().launch(options)
    async def new_context(self, options=None): return await super().new_context(options)
    async def new_page(self, context=None): return await super().new_page(context)
    async def close_page(self, page): return await super().close_page(page)
    async def close_context(self, context): return await super().close_context(context)
    async def close_browser(self, browser=None): return await super().close_browser(browser)
    async def shutdown(self): return await super().shutdown()
    async def goto(self, page, url, wait_until="networkidle", timeout=None): return await super().goto(page, url, wait_until, timeout)
    async def reload(self, page, options=None): return await super().reload(page, options)
    async def get_title(self, page): return await super().get_title(page)
    async def get_url(self, page): return await super().get_url(page)
    async def wait_for_timeout(self, page, milliseconds): return await super().wait_for_timeout(page, milliseconds)
    async def wait_for_load_state(self, page, state="load", timeout=None): return await super().wait_for_load_state(page, state, timeout)
    async def locator(self, context, selector): return await super().locator(context, selector)
    async def click(self, locator, options=None): return await super().click(locator, options)
    async def dblclick(self, locator, options=None): return await super().dblclick(locator, options)
    async def check(self, locator, options=None): return await super().check(locator, options)
    async def fill(self, locator, value, options=None): return await super().fill(locator, value, options)
    async def type(self, locator, text, delay=0): return await super().type(locator, text, delay)
    async def clear(self, locator, options=None): return await super().clear(locator, options)
    async def hover(self, locator, options=None): return await super().hover(locator, options)
    async def select_option(self, locator, values, options=None): return await super().select_option(locator, values, options)
    async def drag_to(self, source_locator, target_locator, options=None): return await super().drag_to(source_locator, target_locator, options)
    async def set_input_files(self, locator, files, options=None): return await super().set_input_files(locator, files, options)
    async def text_content(self, locator): return await super().text_content(locator)
    async def inner_html(self, locator): return await super().inner_html(locator)
    async def inner_text(self, locator): return await super().inner_text(locator)
    async def input_value(self, locator): return await super().input_value(locator)
    async def get_attribute(self, locator, name): return await super().get_attribute(locator, name)
    async def count(self, locator): return await super().count(locator)
    async def nth(self, locator, index): return await super().nth(locator, index)
    async def first(self, locator): return await super().first(locator)
    async def scroll_into_view(self, locator): return await super().scroll_into_view(locator)
    async def is_visible(self, locator): return await super().is_visible(locator)
    async def is_enabled(self, locator): return await super().is_enabled(locator)
    async def evaluate(self, context, expression, arg=None): return await super().evaluate(context, expression, arg)
    async def screenshot(self, page_or_locator, options=None): return await super().screenshot(page_or_locator, options)
    async def wait_for_selector(self, context, selector, options=None): return await super().wait_for_selector(context, selector, options)
    async def frame_locator(self, context, selector): return await super().frame_locator(context, selector)


@pytest.mark.asyncio
async def test_base_driver_abstract_methods():
    driver = DummyBaseDriver()
    await driver.launch()
    await driver.new_context()
    await driver.new_page()
    await driver.close_page(None)
    await driver.close_context(None)
    await driver.close_browser(None)
    await driver.shutdown()
    await driver.goto(None, "http://example.com")
    await driver.reload(None)
    await driver.get_title(None)
    await driver.get_url(None)
    await driver.wait_for_timeout(None, 100)
    await driver.wait_for_load_state(None)
    await driver.locator(None, "div")
    await driver.click(None)
    await driver.fill(None, "test")
    await driver.dblclick(None)
    await driver.check(None)
    await driver.hover(None)
    await driver.select_option(None, "val")
    await driver.count(None)
    await driver.is_visible(None)
    await driver.is_enabled(None)
    await driver.evaluate(None, "1+1")
    await driver.screenshot(None)
    await driver.wait_for_selector(None, "div")
    await driver.type(None, "abc")
    await driver.clear(None)
    await driver.drag_to(None, None)
    await driver.set_input_files(None, "file.txt")
    await driver.text_content(None)
    await driver.inner_html(None)
    await driver.inner_text(None)
    await driver.input_value(None)
    await driver.get_attribute(None, "id")
    await driver.nth(None, 0)
    await driver.first(None)
    await driver.scroll_into_view(None)
    await driver.frame_locator(None, "iframe")


@pytest.mark.asyncio
async def test_playwright_driver_mock_calls():
    from stepwright.drivers.playwright_driver import PlaywrightDriver
    from unittest.mock import AsyncMock, MagicMock

    pw_drv = PlaywrightDriver()

    mock_pg = AsyncMock()
    mock_loc = AsyncMock()
    mock_ctx = AsyncMock()
    mock_browser = AsyncMock()

    # Browser & Page management with mock browser
    pw_drv._browser = mock_browser
    assert await pw_drv.new_context() == await mock_browser.new_context()
    await pw_drv.close_page(mock_pg)
    mock_pg.close.assert_called_once()

    await pw_drv.close_context(mock_ctx)
    mock_ctx.close.assert_called_once()

    await pw_drv.close_browser(mock_browser)
    mock_browser.close.assert_called_once()
    assert pw_drv._browser is None

    # Navigation & Actions
    with pytest.raises(ValueError):
        await pw_drv.goto(mock_pg, "")

    await pw_drv.goto(mock_pg, "https://example.com", timeout=5000)
    mock_pg.goto.assert_called_with("https://example.com", wait_until="networkidle", timeout=5000)

    await pw_drv.reload(mock_pg)
    mock_pg.reload.assert_called_once()

    await pw_drv.get_title(mock_pg)
    mock_pg.title.assert_called_once()

    mock_pg.url = "https://example.com"
    assert await pw_drv.get_url(mock_pg) == "https://example.com"

    await pw_drv.wait_for_timeout(mock_pg, 100)
    mock_pg.wait_for_timeout.assert_called_with(100)

    await pw_drv.wait_for_load_state(mock_pg, "domcontentloaded", timeout=1000)
    mock_pg.wait_for_load_state.assert_called_with("domcontentloaded", timeout=1000)

    # Locators & Element operations
    mock_pg.locator = MagicMock(return_value=mock_loc)
    assert await pw_drv.locator(mock_pg, "#btn") == mock_loc

    await pw_drv.click(mock_loc)
    mock_loc.click.assert_called_once()

    await pw_drv.dblclick(mock_loc)
    mock_loc.dblclick.assert_called_once()

    await pw_drv.check(mock_loc)
    mock_loc.check.assert_called_once()

    await pw_drv.fill(mock_loc, "text")
    mock_loc.fill.assert_called_with("text")

    await pw_drv.type(mock_loc, "text", delay=10)
    mock_loc.type.assert_called_with("text", delay=10)

    await pw_drv.clear(mock_loc)
    await pw_drv.hover(mock_loc)
    await pw_drv.select_option(mock_loc, "opt")
    await pw_drv.drag_to(mock_loc, mock_loc)
    await pw_drv.set_input_files(mock_loc, "file.txt")

    await pw_drv.text_content(mock_loc)
    await pw_drv.inner_html(mock_loc)
    await pw_drv.inner_text(mock_loc)
    await pw_drv.input_value(mock_loc)
    await pw_drv.get_attribute(mock_loc, "href")
    mock_loc.nth = MagicMock()
    mock_pg.frame_locator = MagicMock()
    await pw_drv.nth(mock_loc, 0)
    await pw_drv.first(mock_loc)
    await pw_drv.scroll_into_view(mock_loc)
    await pw_drv.is_visible(mock_loc)
    await pw_drv.is_enabled(mock_loc)

    await pw_drv.evaluate(mock_pg, "() => window.innerWidth", "arg")
    mock_pg.evaluate.assert_called_with("() => window.innerWidth", "arg")

    await pw_drv.screenshot(mock_pg)
    await pw_drv.wait_for_selector(mock_pg, ".sel")
    await pw_drv.frame_locator(mock_pg, "iframe")
    await pw_drv.shutdown()


