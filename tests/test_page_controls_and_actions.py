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


@pytest.mark.asyncio
async def test_page_actions_coverage_extensive(tmp_path):
    """Cover all edge cases and missing lines in page_actions.py"""
    from unittest.mock import AsyncMock, MagicMock
    from stepwright.handlers.page_actions import (
        _handle_screenshot,
        _handle_wait_for_selector,
        _handle_get_meta,
        _handle_get_cookies,
        _handle_set_cookies,
        _handle_get_local_storage,
        _handle_set_local_storage,
        _handle_get_session_storage,
        _handle_set_session_storage,
        _handle_get_viewport_size,
        _handle_set_viewport_size,
        _handle_evaluate,
        _handle_press,
        _handle_type,
        _handle_dialog,
        _handle_mouse_move,
        _handle_wait_for_navigation,
        _handle_set_headers,
    )

    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    mock_page.viewport_size = {"width": 1280, "height": 720}
    collector = {}

    # Screenshot missing value
    with pytest.raises(ValueError, match="requires 'value'"):
        await _handle_screenshot(mock_page, BaseStep(id="s1", action="screenshot"), collector)

    # Screenshot element count 0 fallback
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 0
    mock_page.locator = MagicMock(return_value=mock_loc)
    shot_path = str(tmp_path / "shot.png")
    await _handle_screenshot(mock_page, BaseStep(id="s2", action="screenshot", object="#missing", value=shot_path, key="k_shot"), collector)
    assert collector["k_shot"] == shot_path

    # Wait for selector missing object
    with pytest.raises(ValueError, match="requires object locator"):
        await _handle_wait_for_selector(mock_page, BaseStep(id="w1", action="waitForSelector"), collector)

    # Wait for selector success
    mock_loc.wait_for = AsyncMock()
    await _handle_wait_for_selector(mock_page, BaseStep(id="w2", action="waitForSelector", object="#btn", key="w_key"), collector)
    assert collector["w_key"] is True

    # Get meta single tag & all meta
    mock_page.evaluate = AsyncMock(return_value="meta description text")
    await _handle_get_meta(mock_page, BaseStep(id="m1", action="getMeta", object="description", key="meta_desc"), collector)
    assert collector["meta_desc"] == "meta description text"

    mock_page.evaluate = AsyncMock(return_value={"og:title": "title text"})
    await _handle_get_meta(mock_page, BaseStep(id="m2", action="getMeta", key="meta_all"), collector)
    assert collector["meta_all"] == {"og:title": "title text"}

    # Get cookies single & all
    mock_page.context.cookies = AsyncMock(return_value=[{"name": "session", "value": "abc12345"}])
    await _handle_get_cookies(mock_page, BaseStep(id="c1", action="getCookies", object="session", key="cookie_sess"), collector)
    assert collector["cookie_sess"] == "abc12345"

    await _handle_get_cookies(mock_page, BaseStep(id="c2", action="getCookies", key="cookies_all"), collector)
    assert collector["cookies_all"] == {"session": "abc12345"}

    # Set cookies validation & success
    with pytest.raises(ValueError):
        await _handle_set_cookies(mock_page, BaseStep(id="sc1", action="setCookies", object="name"), collector)
    await _handle_set_cookies(mock_page, BaseStep(id="sc2", action="setCookies", object="name", value="val"), collector)

    # Get & Set LocalStorage
    mock_page.evaluate = AsyncMock(return_value="ls_val")
    await _handle_get_local_storage(mock_page, BaseStep(id="gls1", action="getLocalStorage", object="token", key="ls_t"), collector)
    assert collector["ls_t"] == "ls_val"

    mock_page.evaluate = AsyncMock(return_value={"k": "v"})
    await _handle_get_local_storage(mock_page, BaseStep(id="gls2", action="getLocalStorage", key="ls_all"), collector)
    assert collector["ls_all"] == {"k": "v"}

    with pytest.raises(ValueError):
        await _handle_set_local_storage(mock_page, BaseStep(id="sls1", action="setLocalStorage"), collector)
    mock_page.evaluate = AsyncMock()
    await _handle_set_local_storage(mock_page, BaseStep(id="sls2", action="setLocalStorage", object="k", value="v"), collector)

    # Get & Set SessionStorage
    mock_page.evaluate = AsyncMock(return_value="ss_val")
    await _handle_get_session_storage(mock_page, BaseStep(id="gss1", action="getSessionStorage", object="token", key="ss_t"), collector)
    assert collector["ss_t"] == "ss_val"

    mock_page.evaluate = AsyncMock(return_value={"sk": "sv"})
    await _handle_get_session_storage(mock_page, BaseStep(id="gss2", action="getSessionStorage", key="ss_all"), collector)
    assert collector["ss_all"] == {"sk": "sv"}



    with pytest.raises(ValueError):
        await _handle_set_session_storage(mock_page, BaseStep(id="sss1", action="setSessionStorage"), collector)
    await _handle_set_session_storage(mock_page, BaseStep(id="sss2", action="setSessionStorage", object="sk", value="sv"), collector)

    # Viewport size
    await _handle_get_viewport_size(mock_page, BaseStep(id="v1", action="getViewportSize", key="vp_key"), collector)
    assert collector["vp_key"] == {"width": 1280, "height": 720}

    with pytest.raises(ValueError):
        await _handle_set_viewport_size(mock_page, BaseStep(id="v2", action="setViewportSize"), collector)
    with pytest.raises(ValueError):
        await _handle_set_viewport_size(mock_page, BaseStep(id="v3", action="setViewportSize", value="invalid_fmt"), collector)
    await _handle_set_viewport_size(mock_page, BaseStep(id="v4", action="setViewportSize", value="1920x1080"), collector)

    # Evaluate
    with pytest.raises(ValueError):
        await _handle_evaluate(mock_page, BaseStep(id="e1", action="evaluate"), collector)
    mock_page.evaluate = AsyncMock(return_value=42)
    await _handle_evaluate(mock_page, BaseStep(id="e2", action="evaluate", value="1+1", key="eval_res"), collector)
    assert collector["eval_res"] == 42


    # Press & Type
    with pytest.raises(ValueError):
        await _handle_press(mock_page, BaseStep(id="pr1", action="press"), collector)
    await _handle_press(mock_page, BaseStep(id="pr2", action="press", value="Enter"), collector)
    await _handle_press(mock_page, BaseStep(id="pr3", action="press", object="#btn", value="Enter"), collector)

    with pytest.raises(ValueError):
        await _handle_type(mock_page, BaseStep(id="tp1", action="type"), collector)
    await _handle_type(mock_page, BaseStep(id="tp2", action="type", object="input", value="val", clearBeforeInput=True), collector)

    # Dialog
    mock_dialog = MagicMock()
    mock_dialog.message = "Alert test"
    mock_dialog.accept = AsyncMock()
    mock_dialog.dismiss = AsyncMock()
    mock_page.on = MagicMock()

    await _handle_dialog(mock_page, BaseStep(id="dlg1", action="dialog", value="accept"), collector)
    handler_cb = mock_page.on.call_args[0][1]
    handler_cb(mock_dialog)

    await _handle_dialog(mock_page, BaseStep(id="dlg2", action="dialog", value="dismiss"), collector)
    handler_cb_dismiss = mock_page.on.call_args[0][1]
    handler_cb_dismiss(mock_dialog)

    # MouseMove
    with pytest.raises(ValueError):
        await _handle_mouse_move(mock_page, BaseStep(id="mm1", action="mouseMove"), collector)
    with pytest.raises(ValueError):
        await _handle_mouse_move(mock_page, BaseStep(id="mm2", action="mouseMove", value="single_coord"), collector)
    await _handle_mouse_move(mock_page, BaseStep(id="mm3", action="mouseMove", object="#btn"), collector)
    await _handle_mouse_move(mock_page, BaseStep(id="mm4", action="mouseMove", value="100,200"), collector)

    # WaitForNavigation
    await _handle_wait_for_navigation(mock_page, BaseStep(id="wn1", action="waitForNavigation", value="load"), collector)
    await _handle_wait_for_navigation(mock_page, BaseStep(id="wn2", action="waitForNavigation", value="https://example.com/page"), collector)

    # SetHeaders
    with pytest.raises(ValueError):
        await _handle_set_headers(mock_page, BaseStep(id="sh1", action="setHeaders"), collector)
    await _handle_set_headers(mock_page, BaseStep(id="sh2", action="setHeaders", object="X-Key", value="Val"), collector)
    collector["hdr_dict"] = {"X-Custom": "CustomVal"}
    await _handle_set_headers(mock_page, BaseStep(id="sh3", action="setHeaders", key="hdr_dict"), collector)

