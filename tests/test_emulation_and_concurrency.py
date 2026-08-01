# test_emulation_and_concurrency.py
# Unit tests for multi-engine, device emulation, and concurrency options in StepWright

import pytest
from stepwright import (
    BaseStep,
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    RunOptions,
    run_scraper,
    run_scraper_with_metrics,
    validate_template_format,
    get_device_preset,
)


@pytest.mark.asyncio
async def test_device_preset_lookup():
    """Test retrieving Playwright device preset"""
    preset = await get_device_preset("iPhone 13")
    assert "user_agent" in preset or "viewport" in preset


def test_validator_engine_and_concurrency():
    """Test format validation for engine and concurrency options"""
    # Valid
    t1 = TabTemplate(
        tab="valid",
        engine="firefox",
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    p1 = ParallelTemplate(templates=[t1], max_concurrency=2)
    assert validate_template_format(p1).is_valid is True

    # Invalid engine
    t2 = TabTemplate(
        tab="invalid_engine",
        engine="safari",  # invalid (must be chromium, firefox, webkit)
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    res2 = validate_template_format(t2)
    assert res2.is_valid is False
    assert any(e.code == "INVALID_ENGINE" for e in res2.errors)

    # Invalid concurrency
    p3 = ParallelTemplate(templates=[t1], max_concurrency=0)  # invalid
    res3 = validate_template_format(p3)
    assert res3.is_valid is False
    assert any(e.code == "INVALID_CONCURRENCY" for e in res3.errors)


@pytest.mark.asyncio
async def test_emulation_context_execution(test_page_html_path):
    """Test browser execution with context emulation parameters (User-Agent, Viewport, Locale)"""
    file_url = f"file://{test_page_html_path}"

    template = TabTemplate(
        tab="emulation_test",
        user_agent="StepWrightMobileBot/1.0",
        viewport={"width": 390, "height": 844},
        steps=[
            BaseStep(id="s1", action="navigate", value=file_url),
            BaseStep(id="s2", action="getTitle", key="page_title"),
            BaseStep(
                id="s3_ua",
                action="evaluate",
                value="() => navigator.userAgent",
                key="ua",
            ),
            BaseStep(
                id="s4_size",
                action="getViewportSize",
                key="vp",
            ),
        ],
    )

    options = RunOptions(browser={"headless": True})
    results = await run_scraper([template], options)

    assert len(results) > 0
    res = results[0]
    assert res.get("ua") == "StepWrightMobileBot/1.0"
    assert res.get("vp") == {"width": 390, "height": 844}


@pytest.mark.asyncio
async def test_concurrency_throttling(test_page_html_path):
    """Test parallel template execution with max_concurrency semaphore"""
    file_url = f"file://{test_page_html_path}"

    base_tmpl = TabTemplate(
        tab="item",
        steps=[
            BaseStep(id="s1", action="navigate", value=file_url),
            BaseStep(id="s2", action="getTitle", key="title"),
        ],
    )

    param_tmpl = ParameterizedTemplate(
        template=base_tmpl,
        parameter_key="val",
        values=["a", "b", "c", "d"],
        max_concurrency=2,
        rate_limit_delay_ms=50,
    )

    options = RunOptions(collect_metrics=True, browser={"headless": True})
    results, metrics = await run_scraper_with_metrics([param_tmpl], options)

    assert len(results) == 4
    assert metrics.total_steps_executed == 8
