# test_stealth_and_proxies.py
# Unit tests for Stealth Anti-Bot Evasion, Proxy Configuration, and CAPTCHA Detection Hooks

import pytest
from stepwright import (
    BaseStep,
    TabTemplate,
    RunOptions,
    ProxyConfig,
    run_scraper,
    validate_template_format,
    apply_stealth_scripts,
)


def test_validator_proxy_and_stealth():
    """Test format validation for ProxyConfig and stealth options"""
    # Valid
    t1 = TabTemplate(
        tab="valid",
        stealth=True,
        proxy=ProxyConfig(server="http://proxy:8080"),
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    assert validate_template_format(t1).is_valid is True

    # Invalid proxy server
    t2 = TabTemplate(
        tab="invalid",
        proxy=ProxyConfig(server=""),  # empty server
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    res = validate_template_format(t2)
    assert res.is_valid is False
    assert any(e.code == "INVALID_PROXY_SERVER" for e in res.errors)


@pytest.mark.asyncio
async def test_stealth_script_injection(test_page_html_path):
    """Test stealth script injection removes navigator.webdriver flag"""
    file_url = f"file://{test_page_html_path}"

    template = TabTemplate(
        tab="stealth_test",
        stealth=True,
        steps=[
            BaseStep(id="s1", action="navigate", value=file_url),
            BaseStep(
                id="s2_webdriver",
                action="evaluate",
                value="() => navigator.webdriver",
                key="webdriver_val",
            ),
        ],
    )

    options = RunOptions(stealth=True, browser={"headless": True})
    results = await run_scraper([template], options)

    assert len(results) > 0
    # Stealth script sets navigator.webdriver to undefined (represented as None in Python)
    assert results[0].get("webdriver_val") is None


@pytest.mark.asyncio
async def test_captcha_detection_hook(test_page_html_path):
    """Test CAPTCHA detection hook invocation"""
    file_url = f"file://{test_page_html_path}"
    captcha_triggered = False

    def on_captcha_cb(page, collector):
        nonlocal captcha_triggered
        captcha_triggered = True
        collector["captcha_found"] = True

    template = TabTemplate(
        tab="captcha_test",
        captcha_selector="h1",  # Target h1 element as dummy captcha trigger for test
        on_captcha=on_captcha_cb,
        steps=[
            BaseStep(id="s1", action="navigate", value=file_url),
            BaseStep(id="s2", action="getTitle", key="title"),
        ],
    )

    options = RunOptions(browser={"headless": True})
    results = await run_scraper([template], options)

    assert captcha_triggered is True
    assert results[0].get("captcha_found") is True
