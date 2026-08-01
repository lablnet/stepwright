# test_network_interception.py
# Unit tests for Network & API Request Interception, Resource Blocking, and Custom Headers

import pytest
from stepwright import (
    BaseStep,
    TabTemplate,
    RunOptions,
    run_scraper,
    validate_template_format,
)


def test_validator_intercept_action():
    """Test format validation for intercept action"""
    # Valid
    t1 = TabTemplate(
        tab="valid",
        steps=[BaseStep(id="i1", action="intercept", object="**/api/*", key="data")],
    )
    assert validate_template_format(t1).is_valid is True

    # Invalid (missing pattern)
    t2 = TabTemplate(
        tab="invalid",
        steps=[BaseStep(id="i2", action="intercept")],
    )
    res = validate_template_format(t2)
    assert res.is_valid is False
    assert any(e.code == "MISSING_INTERCEPT_PATTERN" for e in res.errors)


@pytest.mark.asyncio
async def test_resource_blocking_and_headers(test_page_html_path):
    """Test executing a tab with resource blocking and custom extra_http_headers"""
    file_url = f"file://{test_page_html_path}"

    template = TabTemplate(
        tab="net_test",
        block_resources=["image", "font"],
        extra_http_headers={"X-Test-Header": "StepWrightTest"},
        steps=[
            BaseStep(id="s1", action="navigate", value=file_url),
            BaseStep(id="s2", action="getTitle", key="title"),
        ],
    )

    options = RunOptions(browser={"headless": True})
    results = await run_scraper([template], options)

    assert len(results) > 0
    assert results[0].get("title") is not None
