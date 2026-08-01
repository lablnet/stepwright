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
