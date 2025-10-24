# test_scraper.py
# Tests for core scraper functions
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
import sys
from pathlib import Path

# Import from the installed package
from stepwright import (
    get_browser,
    navigate,
    elem,
    input as input_action,
    click,
    double_click,
    click_check_box,
    get_data,
    _shutdown_playwright,
)


@pytest.fixture
async def browser():
    """Create browser instance for tests"""
    browser = await get_browser({"headless": True})
    yield browser
    await browser.close()
    await _shutdown_playwright()


@pytest.fixture
async def page(browser):
    """Create page instance for each test"""
    page = await browser.new_page()
    yield page
    await page.close()


@pytest.fixture
def test_page_url():
    """Get test page URL"""
    test_page_path = Path(__file__).parent / "test_page.html"
    return f"file://{test_page_path}"


class TestGetBrowser:
    """Tests for getBrowser function"""

    @pytest.mark.asyncio
    async def test_create_browser_instance(self):
        """Should create a browser instance"""
        test_browser = await get_browser({"headless": True})
        assert test_browser is not None
        await test_browser.close()
        await _shutdown_playwright()

    @pytest.mark.asyncio
    async def test_custom_launch_options(self):
        """Should accept custom launch options"""
        test_browser = await get_browser({"headless": True, "args": ["--no-sandbox"]})
        assert test_browser is not None
        await test_browser.close()
        await _shutdown_playwright()


class TestNavigate:
    """Tests for navigate function"""

    @pytest.mark.asyncio
    async def test_navigate_to_url(self, page, test_page_url):
        """Should navigate to a URL"""
        result = await navigate(page, test_page_url)
        assert result == page
        assert page.url == test_page_url

    @pytest.mark.asyncio
    async def test_empty_url_error(self, page):
        """Should throw error for empty URL"""
        with pytest.raises(Exception, match="Url is required"):
            await navigate(page, "")

    @pytest.mark.asyncio
    async def test_wait_after_navigation(self, page, test_page_url):
        """Should wait after navigation when specified"""
        import time

        start_time = time.time()
        await navigate(page, test_page_url, 100)
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000
        assert elapsed >= 100


class TestElem:
    """Tests for elem function"""

    @pytest.mark.asyncio
    async def test_find_element_by_id(self, page, test_page_url):
        """Should find element by ID"""
        await navigate(page, test_page_url)
        element = await elem(page, "id", "main-title")
        assert element is not None
        text = await element.text_content()
        assert text == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_find_element_by_class(self, page, test_page_url):
        """Should find element by class"""
        await navigate(page, test_page_url)
        element = await elem(page, "class", "header")
        assert element is not None
        count = await element.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_find_element_by_tag(self, page, test_page_url):
        """Should find element by tag"""
        await navigate(page, test_page_url)
        element = await elem(page, "tag", "h1")
        assert element is not None
        text = await element.text_content()
        assert text == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_find_element_by_xpath(self, page, test_page_url):
        """Should find element by xpath"""
        await navigate(page, test_page_url)
        element = await elem(page, "xpath", '//h1[@id="main-title"]')
        assert element is not None
        text = await element.text_content()
        assert text == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_empty_selector_error(self, page, test_page_url):
        """Should throw error for empty selector"""
        await navigate(page, test_page_url)
        with pytest.raises(Exception, match="Selector is required"):
            await elem(page, "id", "")

    @pytest.mark.asyncio
    async def test_invalid_selector_type(self, page, test_page_url):
        """Should throw error for invalid selector type"""
        await navigate(page, test_page_url)
        with pytest.raises(Exception, match="Invalid selector type"):
            await elem(page, "invalid", "test")


class TestInput:
    """Tests for input function"""

    @pytest.mark.asyncio
    async def test_input_text_into_field(self, page, test_page_url):
        """Should input text into a field"""
        await navigate(page, test_page_url)
        await input_action(page, "id", "search-box", "test search term")
        element = await elem(page, "id", "search-box")
        value = await element.input_value()
        assert value == "test search term"

    @pytest.mark.asyncio
    async def test_wait_after_input(self, page, test_page_url):
        """Should wait after input when specified"""
        await navigate(page, test_page_url)
        import time

        start_time = time.time()
        await input_action(page, "id", "search-box", "test", 100)
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000
        assert elapsed >= 100


class TestClick:
    """Tests for click function"""

    @pytest.mark.asyncio
    async def test_click_on_element(self, page, test_page_url):
        """Should click on an element"""
        await navigate(page, test_page_url)
        await click(page, "id", "show-hidden")

        # Check if hidden content is now visible
        hidden_content = await elem(page, "id", "hidden-content")
        is_visible = await hidden_content.is_visible()
        assert is_visible is True

    @pytest.mark.asyncio
    async def test_click_element_by_class(self, page, test_page_url):
        """Should click on element by class"""
        await navigate(page, test_page_url)
        # This will click the submit button (which prevents default in the test page)
        await click(page, "class", "submit-button")


class TestDoubleClick:
    """Tests for doubleClick function"""

    @pytest.mark.asyncio
    async def test_double_click_on_element(self, page, test_page_url):
        """Should double click on an element"""
        await navigate(page, test_page_url)
        await double_click(page, "id", "show-hidden")

        # Check if hidden content is now visible
        hidden_content = await elem(page, "id", "hidden-content")
        is_visible = await hidden_content.is_visible()
        assert is_visible is True


class TestClickCheckBox:
    """Tests for clickCheckBox function"""

    @pytest.mark.asyncio
    async def test_check_checkbox(self, page, test_page_url):
        """Should check a checkbox"""
        await navigate(page, test_page_url)

        # Add a checkbox to the page for testing
        await page.evaluate(
            """() => {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = 'test-checkbox';
            document.body.appendChild(checkbox);
        }"""
        )

        await click_check_box(page, "id", "test-checkbox")
        checkbox = await elem(page, "id", "test-checkbox")
        is_checked = await checkbox.is_checked()
        assert is_checked is True


class TestGetData:
    """Tests for getData function"""

    @pytest.mark.asyncio
    async def test_get_text_content(self, page, test_page_url):
        """Should get text content"""
        await navigate(page, test_page_url)
        text = await get_data(page, "id", "main-title", "text")
        assert text == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_get_html_content(self, page, test_page_url):
        """Should get HTML content"""
        await navigate(page, test_page_url)
        html = await get_data(page, "id", "main-title", "html")
        assert "StepWright Test Page" in html

    @pytest.mark.asyncio
    async def test_get_input_value(self, page, test_page_url):
        """Should get input value"""
        await navigate(page, test_page_url)
        # Set a value first
        await input_action(page, "id", "search-box", "test value")
        value = await get_data(page, "id", "search-box", "value")
        assert value == "test value"

    @pytest.mark.asyncio
    async def test_get_default_content(self, page, test_page_url):
        """Should get default (innerText) content"""
        await navigate(page, test_page_url)
        text = await get_data(page, "id", "main-title", "default")
        assert text == "StepWright Test Page"

    @pytest.mark.asyncio
    async def test_wait_before_get_data(self, page, test_page_url):
        """Should wait before getting data when specified"""
        await navigate(page, test_page_url)
        import time

        start_time = time.time()
        await get_data(page, "id", "main-title", "text", 100)
        end_time = time.time()
        elapsed = (end_time - start_time) * 1000
        assert elapsed >= 100
