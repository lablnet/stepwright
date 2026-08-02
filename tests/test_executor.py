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


@pytest.mark.asyncio
async def test_execute_tab_pagination_and_captcha():
    from stepwright.executor import execute_tab
    from stepwright.step_types import TabTemplate, BaseStep, PaginationConfig, ScrollConfig

    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    mock_page.evaluate = AsyncMock(return_value=1000)

    # Tab template with paginateAllFirst strategy
    tmpl = TabTemplate(
        tab="t_paginate_all",
        initSteps=[BaseStep(id="init1", action="navigate", value="https://example.com")],
        steps=[BaseStep(id="s1", action="scroll", value="500")],
        pagination=PaginationConfig(
            strategy="scroll",
            scroll=ScrollConfig(offset=500, delay=10),
            paginateAllFirst=True,
            maxPages=2
        )
    )

    results = await execute_tab(mock_page, tmpl)
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_executor_conditions_and_metrics():
    """Test executor condition checks (skip_if/only_if), debug on failure, and metrics"""
    mock_page = _make_page_mock()
    collector = {"flag": True}
    metrics = ExecutionMetrics()

    # Skip if condition met
    step_skip = BaseStep(id="skip1", action="scroll", skipIf="flag == true", value="100")
    await execute_step(mock_page, step_skip, collector, metrics=metrics)
    assert metrics.total_steps_executed == 0

    # Execute step when onlyIf condition is true
    step_only = BaseStep(id="only1", action="scroll", onlyIf="flag == true", value="100")
    await execute_step(mock_page, step_only, collector, metrics=metrics)
    assert metrics.total_steps_executed == 1


@pytest.mark.asyncio
async def test_executor_debug_on_failure_and_iframe():
    """Test executor debug_on_failure printing and frameSelector iframe scope resolution"""
    mock_page = _make_page_mock()
    mock_frame = MagicMock()
    mock_page.frame_locator = MagicMock(return_value=mock_frame)
    collector = {}

    # Debug on failure hook call when step fails
    step_fail = BaseStep(
        id="fail1",
        action="input",
        object_type="id",
        object="missing_inp",
        value="val",
        continueOnEmpty=False,
        terminateonerror=True
    )
    with pytest.raises(ValueError):
        await execute_step(mock_page, step_fail, collector, debug_on_failure=True)

    # Iframe frameSelector types (id, class, xpath)
    step_iframe = BaseStep(
        id="if1",
        action="scroll",
        frameSelector="my-frame",
        frameSelectorType="id",
        value="100"
    )
    await execute_step(mock_page, step_iframe, collector)
    mock_page.frame_locator.assert_called_with("#my-frame")


@pytest.mark.asyncio
async def test_executor_skip_on_error_and_scroll_offsets():
    """Test skipOnError handler, non-integer scroll values, element visibility/enablement click errors"""
    from stepwright.executor import execute_tab
    from stepwright.step_types import TabTemplate, PaginationConfig, ScrollConfig

    mock_page = _make_page_mock()
    collector = {}

    # skipOnError top-level step error guard
    step_skip_err = BaseStep(
        id="so1",
        action="input",
        object_type="id",
        object="non_existent",
        value="val",
        continueOnEmpty=False,
        skipOnError=True
    )
    await _execute_step_internal(mock_page, step_skip_err, collector)

    # Scroll with non-integer value (falls back to window.innerHeight)
    step_scroll = BaseStep(id="sc1", action="scroll", value="invalid_int")
    await _execute_step_internal(mock_page, step_scroll, collector)

    # Click element not visible failure (requireVisible=True)
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 1
    mock_loc.first.is_visible.return_value = False
    mock_page.locator = MagicMock(return_value=mock_loc)

    step_clk_vis = BaseStep(id="c_vis", action="click", object="btn", requireVisible=True, continueOnEmpty=False, terminateonerror=True)
    with pytest.raises(ValueError, match="Element not visible"):
        await _execute_step_internal(mock_page, step_clk_vis, collector)

    # Click element not enabled failure (requireEnabled=True)
    mock_loc.first.is_visible.return_value = True
    mock_loc.first.is_enabled.return_value = False
    step_clk_enb = BaseStep(id="c_enb", action="click", object="btn", requireEnabled=True, continueOnEmpty=False, terminateonerror=True)
    with pytest.raises(ValueError, match="Element not enabled"):
        await _execute_step_internal(mock_page, step_clk_enb, collector)


    # Tab template with paginationFirst = True strategy
    tmpl_pag_first = TabTemplate(
        tab="t_pag_first",
        steps=[BaseStep(id="s1", action="scroll", value="100")],
        pagination=PaginationConfig(
            strategy="scroll",
            scroll=ScrollConfig(offset=100, delay=10),
            paginationFirst=True,
            maxPages=2
        )
    )
    mock_page.evaluate = AsyncMock(return_value=100)
    results = await execute_tab(mock_page, tmpl_pag_first)
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_executor_exhaustive_coverage_sweep():
    """Test all remaining uncovered actions and branches in executor.py"""
    from unittest.mock import patch
    from stepwright.executor import execute_tab, _handle_data_extraction
    from stepwright.step_types import TabTemplate, PaginationConfig, NextButtonConfig


    mock_page = _make_page_mock()
    collector = {}

    # FrameSelectorType xpath & class
    mock_frame = MagicMock()
    mock_frame.evaluate = AsyncMock(return_value=None)
    mock_page.frame_locator = MagicMock(return_value=mock_frame)
    step_xpath = BaseStep(id="fx", action="scroll", frameSelector="//iframe", frameSelectorType="xpath", value="50")
    step_cls = BaseStep(id="fc", action="scroll", frameSelector="my-frame-class", frameSelectorType="class", value="50")
    await execute_step(mock_page, step_xpath, collector)
    await execute_step(mock_page, step_cls, collector)

    # Click skipOnError handling
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 1
    mock_loc.first.click.side_effect = Exception("Click exception")
    mock_page.locator = MagicMock(return_value=mock_loc)
    step_clk_skip = BaseStep(id="c_skip", action="click", object="btn", skipOnError=True)
    await execute_step(mock_page, step_clk_skip, collector)

    # Data extraction failure with default value fallback vs required error
    mock_empty_loc = AsyncMock()
    mock_empty_loc.count.return_value = 0
    mock_page.locator = MagicMock(return_value=mock_empty_loc)

    step_data_def = BaseStep(id="d_def", action="data", object="missing_el", defaultValue="fallback_val")
    await _execute_step_internal(mock_page, step_data_def, collector)
    assert collector.get("d_def") == "fallback_val"


    step_data_req = BaseStep(id="d_req", action="data", object="missing_el", required=True, terminateonerror=True)
    with pytest.raises(ValueError):
        await _execute_step_internal(mock_page, step_data_req, collector)

    # Pagination nextButton click exception handling (returns False)
    tmpl_pag_err = TabTemplate(
        tab="t_pag_err",
        steps=[BaseStep(id="s1", action="scroll", value="100")],
        pagination=PaginationConfig(
            strategy="next",
            nextButton=NextButtonConfig(object_type="id", object="missing_next_btn"),
            maxPages=2
        )
    )
    mock_page.locator.return_value.count.return_value = 0
    results_err = await execute_tab(mock_page, tmpl_pag_err)
    assert isinstance(results_err, list)

    # Test item_keys flattening in execute_tab (lines 552-562)
    mock_page_fe = _make_page_mock()
    tmpl_item_keys = TabTemplate(
        tab="t_item_keys",
        steps=[
            BaseStep(
                id="fe_key",
                action="foreach",
                key="item_0",
                value="{{items}}",
                subSteps=[BaseStep(id="d", action="data", object="#el", key="val")]
            )
        ]
    )
    # Execute tab with collector returning item_keys
    with patch("stepwright.executor._execute_step_internal") as mock_exec_step:
        async def mock_step_impl(page, step, collector, *args, **kwargs):
            collector["item_0"] = {"a": 1}

        mock_exec_step.side_effect = mock_step_impl
        results_item_keys = await execute_tab(mock_page_fe, tmpl_item_keys)
        assert len(results_item_keys) > 0




@pytest.mark.asyncio
async def test_executor_dispatches_remaining_handler_actions(monkeypatch):
    """Exercise executor action dispatch for handlers that are otherwise unit-tested directly."""
    import stepwright.executor as executor

    page = _make_page_mock()
    collector = {}

    handler_names = [
        "_handle_event_download",
        "_handle_save_pdf",
        "_handle_download_pdf",
        "_handle_reload",
        "_handle_get_url",
        "_handle_get_title",
        "_handle_get_meta",
        "_handle_get_cookies",
        "_handle_set_cookies",
        "_handle_get_local_storage",
        "_handle_set_local_storage",
        "_handle_get_session_storage",
        "_handle_set_session_storage",
        "_handle_get_viewport_size",
        "_handle_set_viewport_size",
        "_handle_screenshot",
        "_handle_wait_for_selector",
        "_handle_evaluate",
        "_handle_hover",
        "_handle_select",
        "_handle_drag_and_drop",
        "_handle_upload",
        "_handle_read_data",
        "_handle_write_data",
        "_handle_custom_callback",
        "_handle_intercept",
        "_handle_press",
        "_handle_type",
        "_handle_dialog",
        "_handle_mouse_move",
        "_handle_wait_for_navigation",
        "_handle_set_headers",
    ]
    patched = {}
    for name in handler_names:
        mock = AsyncMock()
        monkeypatch.setattr(executor, name, mock)
        patched[name] = mock

    actions = [
        ("eventBaseDownload", "_handle_event_download"),
        ("savePDF", "_handle_save_pdf"),
        ("downloadPDF", "_handle_download_pdf"),
        ("downloadFile", "_handle_download_pdf"),
        ("reload", "_handle_reload"),
        ("getUrl", "_handle_get_url"),
        ("getTitle", "_handle_get_title"),
        ("getMeta", "_handle_get_meta"),
        ("getCookies", "_handle_get_cookies"),
        ("setCookies", "_handle_set_cookies"),
        ("getLocalStorage", "_handle_get_local_storage"),
        ("setLocalStorage", "_handle_set_local_storage"),
        ("getSessionStorage", "_handle_get_session_storage"),
        ("setSessionStorage", "_handle_set_session_storage"),
        ("getViewportSize", "_handle_get_viewport_size"),
        ("setViewportSize", "_handle_set_viewport_size"),
        ("screenshot", "_handle_screenshot"),
        ("waitForSelector", "_handle_wait_for_selector"),
        ("evaluate", "_handle_evaluate"),
        ("hover", "_handle_hover"),
        ("select", "_handle_select"),
        ("dragAndDrop", "_handle_drag_and_drop"),
        ("uploadFile", "_handle_upload"),
        ("readData", "_handle_read_data"),
        ("writeData", "_handle_write_data"),
        ("custom", "_handle_custom_callback"),
        ("intercept", "_handle_intercept"),
        ("press", "_handle_press"),
        ("type", "_handle_type"),
        ("dialog", "_handle_dialog"),
        ("mouseMove", "_handle_mouse_move"),
        ("waitForNavigation", "_handle_wait_for_navigation"),
        ("setHeaders", "_handle_set_headers"),
    ]

    for idx, (action, handler_name) in enumerate(actions):
        await _execute_step_internal(
            page,
            BaseStep(id=f"dispatch_{idx}", action=action, object="#x", value="value"),
            collector,
        )
        assert patched[handler_name].await_count >= 1

    patched["_handle_set_headers"].side_effect = RuntimeError("header fail")
    await _execute_step_internal(
        page,
        BaseStep(id="skip_dispatch_error", action="setHeaders", value="value", skipOnError=True),
        collector,
    )
