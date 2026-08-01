# test_page_controls_and_actions.py
# Unit tests for Page Controls & Additional Actions (press, type, dialog, mouseMove, waitForNavigation, setHeaders)

import pytest
from stepwright import (
    BaseStep,
    TabTemplate,
    RunOptions,
    run_scraper,
    validate_template_format,
)


def test_validator_new_actions():
    """Test validator checks for new page control actions"""
    # Valid
    t1 = TabTemplate(
        tab="valid",
        steps=[
            BaseStep(id="p1", action="press", value="Enter"),
            BaseStep(id="t1", action="type", object="input", value="hello"),
            BaseStep(id="m1", action="mouseMove", value="100,200"),
        ],
    )
    assert validate_template_format(t1).is_valid is True

    # Invalid press (missing key in value)
    t2 = TabTemplate(
        tab="invalid_press",
        steps=[BaseStep(id="p2", action="press")],
    )
    res2 = validate_template_format(t2)
    assert res2.is_valid is False
    assert any(e.code == "MISSING_PRESS_KEY" for e in res2.errors)


@pytest.mark.asyncio
async def test_page_control_actions_execution(test_page_html_path):
    """Test execution of new page control actions (type, press, mouseMove, setHeaders)"""
    file_url = f"file://{test_page_html_path}"

    template = TabTemplate(
        tab="actions_test",
        steps=[
            BaseStep(
                id="headers",
                action="setHeaders",
                object="X-Test-Action",
                value="StepWright160",
            ),
            BaseStep(id="nav", action="navigate", value=file_url),
            BaseStep(
                id="move",
                action="mouseMove",
                value="50,50",
            ),
            BaseStep(
                id="type_val",
                action="type",
                object="input[type='text']",
                value="Test Input Text",
                inputDelay=10,
            ),
            BaseStep(
                id="press_key",
                action="press",
                object="input[type='text']",
                value="Tab",
            ),
            BaseStep(
                id="wait_state",
                action="waitForNavigation",
                value="domcontentloaded",
            ),
            BaseStep(id="title", action="getTitle", key="title"),
        ],
    )

    options = RunOptions(browser={"headless": True})
    results = await run_scraper([template], options)

    assert len(results) > 0
    assert results[0].get("title") is not None
