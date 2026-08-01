# tests/test_executor.py
# Unit tests for StepWright core execution engine

import pytest
from unittest.mock import AsyncMock, MagicMock

from stepwright.step_types import BaseStep, ExecutionMetrics
from stepwright.executor import _execute_step_internal, execute_step


def _make_page_mock():
    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    mock_loc = MagicMock()
    mock_loc.count = AsyncMock(return_value=0)
    mock_page.locator = MagicMock(return_value=mock_loc)
    return mock_page


@pytest.mark.asyncio
async def test_executor_input_missing_element_error():
    mock_page = _make_page_mock()
    collector = {}

    # Input element not found with terminateonerror=True raises ValueError
    step_input_err = BaseStep(
        id="inp_err",
        action="input",
        object_type="id",
        object="non_existent",
        value="test",
        continueOnEmpty=False,
        terminateonerror=True
    )
    with pytest.raises(ValueError, match="Input element not found"):
        await _execute_step_internal(mock_page, step_input_err, collector)


@pytest.mark.asyncio
async def test_executor_click_missing_element_error():
    mock_page = _make_page_mock()
    collector = {}

    # Click element not found with terminateonerror=True raises ValueError
    step_click_err = BaseStep(
        id="clk_err",
        action="click",
        object_type="id",
        object="non_existent",
        continueOnEmpty=False,
        terminateonerror=True
    )
    with pytest.raises(ValueError, match="Element not found"):
        await _execute_step_internal(mock_page, step_click_err, collector)


@pytest.mark.asyncio
async def test_executor_retry_logic():
    mock_page = _make_page_mock()
    collector = {}
    metrics = ExecutionMetrics()

    # Retry logic exception propagation on final attempt with terminateonerror=True
    step_retry = BaseStep(
        id="r1",
        action="input",
        object_type="id",
        object="missing",
        value="val",
        continueOnEmpty=False,
        terminateonerror=True,
        retry=1,
        retryDelay=10
    )
    with pytest.raises(ValueError):
        await execute_step(mock_page, step_retry, collector, metrics=metrics)
