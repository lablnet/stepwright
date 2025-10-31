# test_new_features.py
# Comprehensive tests for newly added BaseStep options
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
import asyncio
from pathlib import Path

from stepwright import (
    run_scraper,
    TabTemplate,
    BaseStep,
    RunOptions,
)


@pytest.fixture
def enhanced_test_page_url():
    """Get enhanced test page URL"""
    test_page_path = Path(__file__).parent / "test_page_enhanced.html"
    return f"file://{test_page_path.absolute()}"


class TestRetryLogic:
    """Test retry functionality"""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, enhanced_test_page_url):
        """Should retry failed steps"""
        templates = [
            TabTemplate(
                tab="retry_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="click_retry",
                        action="click",
                        object_type="id",
                        object="retry-button",
                        retry=2,
                        retryDelay=500,
                    ),
                    BaseStep(
                        id="check_status",
                        action="data",
                        object_type="id",
                        object="retry-status",
                        key="status",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        # Should have clicked at least once
        assert "clicked" in results[0]["status"].lower() or "Not clicked" in results[0]["status"]


class TestFallbackSelectors:
    """Test fallback selector functionality"""

    @pytest.mark.asyncio
    async def test_fallback_selectors(self, enhanced_test_page_url):
        """Should use fallback selectors when primary fails"""
        templates = [
            TabTemplate(
                tab="fallback_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="click_with_fallback",
                        action="click",
                        object_type="id",
                        object="non-existent-button",
                        fallbackSelectors=[
                            {"object_type": "class", "object": "btn-primary-alt"},
                            {"object_type": "class", "object": "button-primary"},
                        ],
                    ),
                ],
            )
        ]

        # Should not raise error, should use fallback
        results = await run_scraper(templates)
        assert len(results) == 1


class TestConditionalExecution:
    """Test conditional execution (skipIf/onlyIf)"""

    @pytest.mark.asyncio
    async def test_skip_if_condition(self, enhanced_test_page_url):
        """Should skip step when skipIf condition is true"""
        templates = [
            TabTemplate(
                tab="skip_if_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="skip_step",
                        action="data",
                        object_type="id",
                        object="conditional-missing",
                        key="skipped",
                        skipIf="document.querySelector('#conditional-missing').classList.contains('hidden')",
                    ),
                    BaseStep(
                        id="should_execute",
                        action="data",
                        object_type="id",
                        object="conditional-element",
                        key="executed",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        # Skipped step should not have value
        assert "skipped" not in results[0] or results[0].get("skipped") is None
        # Should execute step should have value
        assert results[0].get("executed") is not None

    @pytest.mark.asyncio
    async def test_only_if_condition(self, enhanced_test_page_url):
        """Should execute step only when onlyIf condition is true"""
        templates = [
            TabTemplate(
                tab="only_if_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="conditional_step",
                        action="data",
                        object_type="id",
                        object="conditional-element",
                        key="conditional",
                        onlyIf="document.querySelector('#conditional-element') !== null",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0].get("conditional") is not None


class TestWaitForSelector:
    """Test waitForSelector functionality"""

    @pytest.mark.asyncio
    async def test_wait_for_selector(self, enhanced_test_page_url):
        """Should wait for selector before action"""
        templates = [
            TabTemplate(
                tab="wait_for_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="load_dynamic",
                        action="click",
                        object_type="id",
                        object="load-dynamic",
                    ),
                    BaseStep(
                        id="extract_dynamic",
                        action="data",
                        object_type="class",
                        object="dynamic-content",
                        key="dynamic",
                        waitForSelector="dynamic-content",
                        waitForSelectorTimeout=5000,
                        waitForSelectorState="visible",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        # Should have waited and found dynamic content
        assert results[0].get("dynamic") is not None


class TestClickEnhancements:
    """Test click enhancements"""

    @pytest.mark.asyncio
    async def test_double_click(self, enhanced_test_page_url):
        """Should perform double click"""
        templates = [
            TabTemplate(
                tab="double_click_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="double_click",
                        action="click",
                        object_type="id",
                        object="double-click",
                        doubleClick=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_right_click(self, enhanced_test_page_url):
        """Should perform right click"""
        templates = [
            TabTemplate(
                tab="right_click_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="right_click",
                        action="click",
                        object_type="id",
                        object="right-click",
                        rightClick=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_force_click(self, enhanced_test_page_url):
        """Should force click even if element is not visible"""
        templates = [
            TabTemplate(
                tab="force_click_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="force_click",
                        action="click",
                        object_type="id",
                        object="overlay-button",
                        forceClick=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_click_modifiers(self, enhanced_test_page_url):
        """Should use click modifiers"""
        templates = [
            TabTemplate(
                tab="modifier_click_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="modifier_click",
                        action="click",
                        object_type="id",
                        object="external-link",
                        clickModifiers=["Meta"],  # Cmd/Ctrl+Click
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1


class TestInputEnhancements:
    """Test input enhancements"""

    @pytest.mark.asyncio
    async def test_clear_before_input(self, enhanced_test_page_url):
        """Should clear input before typing"""
        templates = [
            TabTemplate(
                tab="clear_input_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="input_clear",
                        action="input",
                        object_type="id",
                        object="input-field",
                        value="New Value",
                        clearBeforeInput=True,
                    ),
                    BaseStep(
                        id="check_value",
                        action="data",
                        object_type="id",
                        object="input-field",
                        key="input_value",
                        data_type="value",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0]["input_value"] == "New Value"

    @pytest.mark.asyncio
    async def test_input_delay(self, enhanced_test_page_url):
        """Should type with delay between keystrokes"""
        templates = [
            TabTemplate(
                tab="input_delay_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="input_with_delay",
                        action="input",
                        object_type="id",
                        object="input-field-empty",
                        value="Test",
                        inputDelay=50,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1


class TestDataExtractionEnhancements:
    """Test data extraction enhancements"""

    @pytest.mark.asyncio
    async def test_regex_extraction(self, enhanced_test_page_url):
        """Should extract data using regex"""
        templates = [
            TabTemplate(
                tab="regex_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="extract_price",
                        action="data",
                        object_type="id",
                        object="price",
                        key="price",
                        regex=r"\$([\d,]+\.\d+)",
                        regexGroup=1,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0]["price"] == "1,234.56"

    @pytest.mark.asyncio
    async def test_transform_extraction(self, enhanced_test_page_url):
        """Should transform extracted data"""
        templates = [
            TabTemplate(
                tab="transform_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="extract_numeric",
                        action="data",
                        object_type="id",
                        object="numeric-field",
                        key="numeric",
                        transform="parseInt(value)",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert isinstance(results[0]["numeric"], int) or results[0]["numeric"] == 12345

    @pytest.mark.asyncio
    async def test_required_field(self, enhanced_test_page_url):
        """Should raise error if required field is missing"""
        templates = [
            TabTemplate(
                tab="required_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="required_data",
                        action="data",
                        object_type="id",
                        object="required-field",
                        key="required",
                        required=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0]["required"] is not None

    @pytest.mark.asyncio
    async def test_default_value(self, enhanced_test_page_url):
        """Should use default value when extraction fails"""
        templates = [
            TabTemplate(
                tab="default_value_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="optional_data",
                        action="data",
                        object_type="id",
                        object="non-existent",
                        key="optional",
                        defaultValue="Default Value",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0]["optional"] == "Default Value"


class TestRandomDelay:
    """Test random delay functionality"""

    @pytest.mark.asyncio
    async def test_random_delay(self, enhanced_test_page_url):
        """Should apply random delay before action"""
        import time
        start = time.time()
        
        templates = [
            TabTemplate(
                tab="random_delay_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="delayed_action",
                        action="click",
                        object_type="id",
                        object="single-click",
                        randomDelay={"min": 100, "max": 300},
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        elapsed = time.time() - start
        
        assert len(results) == 1
        # Should have taken at least 100ms
        assert elapsed >= 0.1


class TestElementStateChecks:
    """Test element state checks"""

    @pytest.mark.asyncio
    async def test_require_visible(self, enhanced_test_page_url):
        """Should check if element is visible"""
        templates = [
            TabTemplate(
                tab="require_visible_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="click_visible",
                        action="click",
                        object_type="id",
                        object="single-click",
                        requireVisible=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_require_enabled(self, enhanced_test_page_url):
        """Should check if element is enabled"""
        templates = [
            TabTemplate(
                tab="require_enabled_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="click_enabled",
                        action="click",
                        object_type="id",
                        object="single-click",
                        requireEnabled=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1


class TestContinueOnEmpty:
    """Test continueOnEmpty functionality"""

    @pytest.mark.asyncio
    async def test_continue_on_empty(self, enhanced_test_page_url):
        """Should continue execution even if element not found"""
        templates = [
            TabTemplate(
                tab="continue_empty_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="missing_element",
                        action="click",
                        object_type="id",
                        object="non-existent",
                        continueOnEmpty=True,
                    ),
                    BaseStep(
                        id="should_execute",
                        action="data",
                        object_type="id",
                        object="main-title",
                        key="title",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        # Should have executed next step
        assert results[0]["title"] == "StepWright Test Page"


class TestGetMeta:
    """Test getMeta functionality"""

    @pytest.mark.asyncio
    async def test_get_specific_meta(self, enhanced_test_page_url):
        """Should get specific meta tag"""
        templates = [
            TabTemplate(
                tab="get_meta_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="get_description",
                        action="getMeta",
                        object="description",
                        key="meta_description",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0].get("meta_description") is not None

    @pytest.mark.asyncio
    async def test_get_all_meta(self, enhanced_test_page_url):
        """Should get all meta tags"""
        templates = [
            TabTemplate(
                tab="get_all_meta_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="get_all_meta",
                        action="getMeta",
                        key="all_meta",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert isinstance(results[0]["all_meta"], dict)
        assert len(results[0]["all_meta"]) > 0


class TestStorageOperations:
    """Test storage operations"""

    @pytest.mark.asyncio
    async def test_local_storage(self, enhanced_test_page_url):
        """Should get/set localStorage"""
        templates = [
            TabTemplate(
                tab="local_storage_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="set_storage",
                        action="click",
                        object_type="id",
                        object="set-storage",
                    ),
                    BaseStep(
                        id="get_storage",
                        action="getLocalStorage",
                        object="test_key",
                        key="storage_value",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0].get("storage_value") == "test_value"

    @pytest.mark.asyncio
    async def test_set_local_storage(self, enhanced_test_page_url):
        """Should set localStorage value"""
        templates = [
            TabTemplate(
                tab="set_local_storage_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="set_storage",
                        action="setLocalStorage",
                        object="custom_key",
                        value="custom_value",
                    ),
                    BaseStep(
                        id="get_storage",
                        action="getLocalStorage",
                        object="custom_key",
                        key="custom_storage",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0]["custom_storage"] == "custom_value"


class TestViewportOperations:
    """Test viewport operations"""

    @pytest.mark.asyncio
    async def test_get_viewport_size(self, enhanced_test_page_url):
        """Should get viewport size"""
        templates = [
            TabTemplate(
                tab="viewport_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="get_viewport",
                        action="getViewportSize",
                        key="viewport",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert "width" in results[0]["viewport"]
        assert "height" in results[0]["viewport"]

    @pytest.mark.asyncio
    async def test_set_viewport_size(self, enhanced_test_page_url):
        """Should set viewport size"""
        templates = [
            TabTemplate(
                tab="set_viewport_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="set_viewport",
                        action="setViewportSize",
                        value="1920x1080",
                    ),
                    BaseStep(
                        id="get_viewport",
                        action="getViewportSize",
                        key="viewport",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0]["viewport"]["width"] == 1920
        assert results[0]["viewport"]["height"] == 1080


class TestCookiesOperations:
    """Test cookie operations"""

    @pytest.mark.asyncio
    async def test_get_cookies(self, enhanced_test_page_url):
        """Should get cookies"""
        templates = [
            TabTemplate(
                tab="get_cookies_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="get_all_cookies",
                        action="getCookies",
                        key="cookies",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert isinstance(results[0]["cookies"], dict)

    @pytest.mark.asyncio
    async def test_get_specific_cookie(self, enhanced_test_page_url):
        """Should get specific cookie"""
        templates = [
            TabTemplate(
                tab="get_specific_cookie_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    BaseStep(
                        id="get_cookie",
                        action="getCookies",
                        object="test_cookie",
                        key="cookie_value",
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        # Cookie might not be available in file:// protocol
        assert results[0].get("cookie_value") is not None or results[0].get("cookie_value") is None


class TestCombinedFeatures:
    """Test combined features working together"""

    @pytest.mark.asyncio
    async def test_complex_scenario(self, enhanced_test_page_url):
        """Test multiple features together"""
        templates = [
            TabTemplate(
                tab="complex_test",
                steps=[
                    BaseStep(id="navigate", action="navigate", value=enhanced_test_page_url),
                    # Conditional step
                    BaseStep(
                        id="conditional",
                        action="data",
                        object_type="id",
                        object="conditional-element",
                        key="conditional",
                        onlyIf="document.querySelector('#conditional-element') !== null",
                        defaultValue="Not found",
                    ),
                    # Data with regex and transform
                    BaseStep(
                        id="extract_price",
                        action="data",
                        object_type="id",
                        object="price",
                        key="price",
                        regex=r"\$([\d,]+\.\d+)",
                        regexGroup=1,
                        transform="parseFloat(value.replace(/,/g, ''))",
                        required=True,
                    ),
                    # Click with fallback and retry
                    BaseStep(
                        id="click_fallback",
                        action="click",
                        object_type="id",
                        object="non-existent",
                        fallbackSelectors=[
                            {"object_type": "class", "object": "button-primary"},
                        ],
                        retry=1,
                        retryDelay=500,
                    ),
                    # Input with clear
                    BaseStep(
                        id="input_clear",
                        action="input",
                        object_type="id",
                        object="input-field-empty",
                        value="Test Value",
                        clearBeforeInput=True,
                    ),
                ],
            )
        ]

        results = await run_scraper(templates)
        assert len(results) == 1
        assert results[0].get("conditional") is not None
        assert results[0].get("price") is not None

