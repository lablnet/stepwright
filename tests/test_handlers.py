# tests/test_handlers.py
# Unit tests for action and data flow handlers in StepWright

import os
import json
import pytest
from unittest.mock import AsyncMock

from stepwright.step_types import BaseStep
from stepwright.handlers.file_handlers import _handle_event_download, _handle_save_pdf
from stepwright.handlers.data_flow_handlers import _handle_read_data, _handle_write_data
from stepwright.handlers.loop_handlers import clone_step_with_index
from stepwright.handlers.page_actions import _handle_reload, _handle_get_url, _handle_get_title, _handle_screenshot
from stepwright.handlers.network_handlers import _handle_intercept


@pytest.mark.asyncio
async def test_file_handlers_validation(tmp_path):
    mock_page = AsyncMock()
    collector = {}

    # Event download missing value raises ValueError
    step_no_val = BaseStep(id="d1", action="eventBaseDownload")
    with pytest.raises(ValueError):
        await _handle_event_download(mock_page, step_no_val, collector)

    # Save PDF missing value raises ValueError
    step_pdf_no_val = BaseStep(id="p1", action="savePDF")
    with pytest.raises(ValueError):
        await _handle_save_pdf(mock_page, step_pdf_no_val, collector)


@pytest.mark.asyncio
async def test_data_flow_read_and_write(tmp_path):
    mock_page = AsyncMock()
    collector = {}

    # Read data missing value raises ValueError
    step_read_no_val = BaseStep(id="r1", action="readData")
    with pytest.raises(ValueError):
        await _handle_read_data(mock_page, step_read_no_val, collector)

    # Read data missing file with continueOnEmpty
    step_missing_file = BaseStep(id="r2", action="readData", value="non_existent.json", continueOnEmpty=True)
    await _handle_read_data(mock_page, step_missing_file, collector)

    # Read JSON file
    json_path = str(tmp_path / "test.json")
    with open(json_path, "w") as f:
        json.dump({"a": 1}, f)
    step_read_json = BaseStep(id="r3", action="readData", value=json_path, data_type="json", key="read_json")
    await _handle_read_data(mock_page, step_read_json, collector)
    assert collector["read_json"] == {"a": 1}

    # Write data JSON
    out_json = str(tmp_path / "out_write.json")
    step_write = BaseStep(id="w1", action="writeData", value=out_json, data_type="json")
    collector["read_json"] = [{"val": 100}]
    await _handle_write_data(mock_page, step_write, collector)
    assert os.path.exists(out_json)


def test_loop_handlers_cloning():
    parent_step = BaseStep(
        id="p1",
        action="click",
        object="btn_{{ i }}",
        subSteps=[
            BaseStep(id="c1", action="input", value="val_{{ i_plus1 }}")
        ]
    )
    cloned = clone_step_with_index(parent_step, 0, "i")
    assert cloned.object == "btn_0"
    assert cloned.subSteps[0].value == "val_1"


@pytest.mark.asyncio
async def test_page_and_network_actions():
    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Example Title"
    collector = {}

    # Reload
    step_reload = BaseStep(id="r1", action="reload", value="domcontentloaded")
    await _handle_reload(mock_page, step_reload, collector)
    mock_page.reload.assert_called_once_with(wait_until="domcontentloaded")

    # Get URL
    step_url = BaseStep(id="u1", action="getUrl", key="curr_url")
    await _handle_get_url(mock_page, step_url, collector)
    assert collector["curr_url"] == "https://example.com"

    # Get Title
    step_title = BaseStep(id="t1", action="getTitle", key="curr_title")
    await _handle_get_title(mock_page, step_title, collector)
    assert collector["curr_title"] == "Example Title"

    # Screenshot missing value raises ValueError
    step_ss_no_val = BaseStep(id="s1", action="screenshot")
    with pytest.raises(ValueError):
        await _handle_screenshot(mock_page, step_ss_no_val, collector)

    # Intercept missing pattern raises ValueError
    step_ic_no_val = BaseStep(id="i1", action="intercept")
    with pytest.raises(ValueError):
        await _handle_intercept(mock_page, step_ic_no_val, collector)


@pytest.mark.asyncio
async def test_page_storage_and_viewport_handlers():
    from stepwright.handlers.page_actions import (
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
    )

    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    collector = {}

    # Wait for selector missing object raises ValueError
    with pytest.raises(ValueError):
        await _handle_wait_for_selector(mock_page, BaseStep(id="w1", action="waitForSelector"), collector)

    # Set cookies validation errors
    with pytest.raises(ValueError):
        await _handle_set_cookies(mock_page, BaseStep(id="c1", action="setCookies", object="name"), collector)
    with pytest.raises(ValueError):
        await _handle_set_cookies(mock_page, BaseStep(id="c2", action="setCookies", value="val"), collector)

    # Set local storage validation errors
    with pytest.raises(ValueError):
        await _handle_set_local_storage(mock_page, BaseStep(id="l1", action="setLocalStorage", value="val"), collector)
    with pytest.raises(ValueError):
        await _handle_set_local_storage(mock_page, BaseStep(id="l2", action="setLocalStorage", object="key"), collector)

    # Set session storage validation errors
    with pytest.raises(ValueError):
        await _handle_set_session_storage(mock_page, BaseStep(id="s1", action="setSessionStorage", value="val"), collector)
    with pytest.raises(ValueError):
        await _handle_set_session_storage(mock_page, BaseStep(id="s2", action="setSessionStorage", object="key"), collector)

    # Set viewport size validation error
    with pytest.raises(ValueError):
        await _handle_set_viewport_size(mock_page, BaseStep(id="v1", action="setViewportSize"), collector)

    # Storage and viewport successes with mock page
    mock_page.evaluate.side_effect = [
        "meta_content",  # getMeta
        "storage_val",   # getLocalStorage
        "session_val",   # getSessionStorage
    ]
    mock_page.context.cookies = AsyncMock(return_value=[{"name": "session_id", "value": "xyz123"}])

    await _handle_get_meta(mock_page, BaseStep(id="m1", action="getMeta", object="description", key="desc"), collector)
    assert collector["desc"] == "meta_content"

    await _handle_get_cookies(mock_page, BaseStep(id="gc1", action="getCookies", object="session_id", key="my_cookie"), collector)
    assert collector["my_cookie"] == "xyz123"

    await _handle_get_local_storage(mock_page, BaseStep(id="gl1", action="getLocalStorage", object="user_token", key="token"), collector)
    assert collector["token"] == "storage_val"

    await _handle_get_session_storage(mock_page, BaseStep(id="gs1", action="getSessionStorage", object="state_key", key="state"), collector)
    assert collector["state"] == "session_val"

    mock_page.viewport_size = {"width": 1280, "height": 720}
    await _handle_get_viewport_size(mock_page, BaseStep(id="gv1", action="getViewportSize", key="vp"), collector)
    assert collector["vp"] == {"width": 1280, "height": 720}

