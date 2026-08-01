# test_developer_experience.py
# Unit tests for developer experience options (metrics collection and debug_on_failure)
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
from stepwright import (
    BaseStep,
    TabTemplate,
    RunOptions,
    run_scraper_with_metrics,
    ExecutionMetrics,
    StepMetric,
)


@pytest.mark.asyncio
async def test_metrics_collection(test_page_html_path):
    """Test that metrics collection tracks executed steps and timing"""
    file_url = f"file://{test_page_html_path}"

    template = TabTemplate(
        tab="metrics_test",
        steps=[
            BaseStep(id="s1_nav", action="navigate", value=file_url),
            BaseStep(id="s2_title", action="getTitle", key="page_title"),
            BaseStep(id="s3_data", action="data", object="#main-title", key="h1_title"),
        ],
    )

    options = RunOptions(collect_metrics=True, browser={"headless": True})
    results, metrics = await run_scraper_with_metrics([template], options)

    assert len(results) > 0
    assert isinstance(metrics, ExecutionMetrics)
    assert metrics.total_steps_executed == 3
    assert metrics.failed_steps_count == 0
    assert len(metrics.step_metrics) == 3
    assert metrics.total_duration_ms > 0

    step_ids = [m.step_id for m in metrics.step_metrics]
    assert step_ids == ["s1_nav", "s2_title", "s3_data"]
    for m in metrics.step_metrics:
        assert m.success is True
        assert m.duration_ms >= 0


@pytest.mark.asyncio
async def test_debug_on_failure_flag(capsys, test_page_html_path):
    """Test that debug_on_failure logs diagnostic output when step fails"""
    file_url = f"file://{test_page_html_path}"

    template = TabTemplate(
        tab="debug_test",
        steps=[
            BaseStep(id="nav", action="navigate", value=file_url),
            BaseStep(
                id="failing_click",
                action="click",
                object="#non_existent_element_xyz",
                terminateonerror=False,
                retry=0,
            ),
        ],
    )

    options = RunOptions(debug_on_failure=True, browser={"headless": True})
    results, metrics = await run_scraper_with_metrics([template], options)

    captured = capsys.readouterr()
    assert "STEP DEBUG ON FAILURE" in captured.out or "failing_click" in captured.out
