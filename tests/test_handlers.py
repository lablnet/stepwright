# tests/test_handlers.py
# Unit tests for action and data flow handlers in StepWright

import os
import json
import pathlib
import pytest
import unittest.mock
from unittest.mock import AsyncMock, MagicMock

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


@pytest.mark.asyncio
async def test_network_handlers_comprehensive():
    from stepwright.handlers.network_handlers import _handle_intercept, setup_resource_blocking

    mock_page = AsyncMock()
    mock_page.on = MagicMock()
    collector = {}

    # Intercept response listener setup and execution
    step_ic = BaseStep(id="ic1", action="intercept", object="api/*", data_type="json", key="api_res")
    await _handle_intercept(mock_page, step_ic, collector)

    # Trigger response listener callback directly
    assert mock_page.on.called
    response_callback = mock_page.on.call_args[0][1]

    mock_resp = AsyncMock()
    mock_resp.url = "https://example.com/api/users"
    mock_resp.request.method = "GET"
    mock_resp.json.return_value = {"users": ["alice", "bob"]}

    import asyncio
    task = response_callback(mock_resp)
    if asyncio.iscoroutine(task) or hasattr(task, "__await__"):
        await task

    # Setup resource blocking
    await setup_resource_blocking(mock_page, None)  # Noop
    await setup_resource_blocking(mock_page, ["image", "stylesheet"])
    mock_page.route.assert_called_once()


@pytest.mark.asyncio
async def test_data_flow_comprehensive(tmp_path):
    from stepwright.handlers.data_flow_handlers import _handle_read_data, _handle_write_data, _handle_custom_callback

    mock_page = AsyncMock()
    collector = {}

    # Read CSV file
    csv_path = str(tmp_path / "read.csv")
    with open(csv_path, "w") as f:
        f.write("name,age\nalice,30\nbob,25\n")
    step_csv_read = BaseStep(id="r_csv", action="readData", value=csv_path, data_type="csv", key="csv_data")
    await _handle_read_data(mock_page, step_csv_read, collector)
    assert len(collector["csv_data"]) == 2

    # Read Text lines
    txt_path = str(tmp_path / "read.txt")
    with open(txt_path, "w") as f:
        f.write("line1\nline2\n")
    step_txt_read = BaseStep(id="r_txt", action="readData", value=txt_path, data_type="text", key="txt_data")
    await _handle_read_data(mock_page, step_txt_read, collector)
    assert collector["txt_data"] == ["line1", "line2"]

    # Write CSV file
    out_csv = str(tmp_path / "out.csv")
    collector["out_items"] = [{"title": "Item 1", "price": "10"}]
    step_csv_write = BaseStep(id="w_csv", action="writeData", value=out_csv, data_type="csv", key="out_items")
    await _handle_write_data(mock_page, step_csv_write, collector)
    assert os.path.exists(out_csv)

    # Custom action callback missing callback raises ValueError
    step_no_cb = BaseStep(id="c_err", action="custom")
    with pytest.raises(ValueError):
        await _handle_custom_callback(mock_page, step_no_cb, collector)

    # Custom action callback success
    async def my_cb(pg, coll, stp): return "cb_result"
    step_cb = BaseStep(id="c_ok", action="custom", callback=my_cb, key="cb_key")
    await _handle_custom_callback(mock_page, step_cb, collector)
    assert collector["cb_key"] == "cb_result"


@pytest.mark.asyncio
async def test_file_handlers_comprehensive(tmp_path):
    from stepwright.handlers.file_handlers import (
        _handle_event_download,
        _handle_save_pdf,
        _handle_download_pdf,
    )

    mock_page = AsyncMock()
    mock_page.url = "https://example.com/viewer.html?file=doc.pdf"
    collector = {}

    # Event download - missing value error
    with pytest.raises(ValueError):
        await _handle_event_download(mock_page, BaseStep(id="d1", action="eventBaseDownload"), collector)

    # Event download - element not visible
    mock_target = AsyncMock()
    mock_target.is_visible = AsyncMock(return_value=False)
    mock_page.locator = MagicMock(return_value=mock_target)
    await _handle_event_download(mock_page, BaseStep(id="d2", action="eventBaseDownload", object="btn", value=str(tmp_path / "f.txt"), key="file"), collector)
    assert collector["file"] is None

    # Save PDF - missing value error
    with pytest.raises(ValueError):
        await _handle_save_pdf(mock_page, BaseStep(id="p1", action="savePDF"), collector)

    # Save PDF - URL with query param .pdf
    mock_page.evaluate.return_value = None
    pdf_path = str(tmp_path / "out.pdf")
    step_pdf = BaseStep(id="p2", action="savePDF", value=pdf_path, key="pdf_key")

    # Mock async_playwright context response
    mock_resp = AsyncMock()
    mock_resp.ok = True
    mock_resp.body.return_value = b"%PDF-1.4 mock pdf data"

    mock_req_ctx = AsyncMock()
    mock_req_ctx.get.return_value = mock_resp

    mock_pw = AsyncMock()
    mock_pw.request.new_context.return_value = mock_req_ctx

    with unittest.mock.patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_pw
        mock_apw.return_value = mock_cm

        await _handle_save_pdf(mock_page, step_pdf, collector)
        assert os.path.exists(pdf_path)
        assert collector["pdf_key"] == pdf_path

    # Download PDF - missing object / value errors
    with pytest.raises(ValueError):
        await _handle_download_pdf(mock_page, BaseStep(id="dp1", action="downloadPDF", value="v"), collector)
    with pytest.raises(ValueError):
        await _handle_download_pdf(mock_page, BaseStep(id="dp2", action="downloadPDF", object="o"), collector)

    # Download PDF - count 0
    mock_link = AsyncMock()
    mock_link.count.return_value = 0
    mock_page.locator.return_value = mock_link
    await _handle_download_pdf(mock_page, BaseStep(id="dp3", action="downloadPDF", object="link", value="val"), collector)
    assert collector["file"] is None

    # Download PDF - direct href success
    mock_link.count.return_value = 1
    mock_link.get_attribute.return_value = "https://example.com/doc.pdf"
    dl_pdf_path = str(tmp_path / "downloaded.pdf")
    step_dl_pdf = BaseStep(id="dp4", action="downloadPDF", object="link", value=dl_pdf_path, key="dl_key")

    with unittest.mock.patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_pw
        mock_apw.return_value = mock_cm

        await _handle_download_pdf(mock_page, step_dl_pdf, collector)
        assert os.path.exists(dl_pdf_path)
        assert collector["dl_key"] == dl_pdf_path


@pytest.mark.asyncio
async def test_handlers_error_branches_and_edge_cases(tmp_path):
    """Test handlers error paths (unsupported actions, data mapping edge cases, file storage)"""
    from stepwright.handlers.data_flow_handlers import _handle_write_data, _handle_read_data
    from stepwright.handlers.interaction_handlers import _handle_drag_and_drop
    from stepwright.handlers.network_handlers import setup_resource_blocking

    mock_page = AsyncMock()
    collector = {}

    # Write data with missing file path
    step_no_path_write = BaseStep(id="w_no_path", action="writeData", key="key")
    collector["key"] = [{"a": 1}]
    with pytest.raises(ValueError, match="writeData requires a file path"):
        await _handle_write_data(mock_page, step_no_path_write, collector)

    # Read data with missing file path
    step_no_path_read = BaseStep(id="r_no_path", action="readData", key="key")
    with pytest.raises(ValueError, match="readData requires a file path"):
        await _handle_read_data(mock_page, step_no_path_read, collector)

    # Read data file not found
    step_fnf = BaseStep(id="r_fnf", action="readData", value=str(tmp_path / "non_existent.txt"))
    with pytest.raises(FileNotFoundError):
        await _handle_read_data(mock_page, step_fnf, collector)

    # Drag and drop success with mock locators
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 1
    mock_page.locator = MagicMock(return_value=mock_loc)
    step_drag = BaseStep(id="d1", action="dragAndDrop", object="src", targetObject="dst")
    await _handle_drag_and_drop(mock_page, step_drag, collector)
    mock_loc.first.drag_to.assert_called_once()

    # Network block resources empty list
    await setup_resource_blocking(mock_page, [])


@pytest.mark.asyncio
async def test_file_handlers_fallbacks_and_frames(tmp_path):
    """Test savePDF viewer fallback, shadow root clicks, and downloadPDF popup page handling"""
    from stepwright.handlers.file_handlers import _handle_save_pdf, _handle_download_pdf, _handle_event_download

    mock_page = AsyncMock()
    mock_page.url = "https://example.com/doc"
    mock_page.evaluate = AsyncMock(side_effect=["http://example.com/doc.pdf", True])
    collector = {}

    pdf_out = str(tmp_path / "fallback.pdf")
    step_save = BaseStep(id="sp", action="savePDF", value=pdf_out, key="sp_key")

    mock_resp = AsyncMock()
    mock_resp.ok = True
    mock_resp.body.return_value = b"%PDF-1.4 mock pdf data"

    mock_req = AsyncMock()
    mock_req.get.return_value = mock_resp

    mock_pw = AsyncMock()
    mock_pw.request.new_context.return_value = mock_req

    with unittest.mock.patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_pw
        mock_apw.return_value = mock_cm

        await _handle_save_pdf(mock_page, step_save, collector)
        assert collector["sp_key"] == pdf_out

    # downloadPDF via new tab popup event
    mock_link = AsyncMock()
    mock_link.count.return_value = 1
    mock_link.get_attribute.return_value = "javascript:void(0)"
    mock_page.locator = MagicMock(return_value=mock_link)

    mock_new_page = AsyncMock()
    mock_new_page.url = "https://example.com/popup.pdf"
    mock_page.context.wait_for_event = AsyncMock(return_value=mock_new_page)

    dl_out = str(tmp_path / "popup.pdf")
    step_dl = BaseStep(id="dp", action="downloadPDF", object="#btn", value=dl_out, key="dp_key")

    with unittest.mock.patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_pw
        mock_apw.return_value = mock_cm

        await _handle_download_pdf(mock_page, step_dl, collector)
        assert collector["dp_key"] == dl_out


@pytest.mark.asyncio
async def test_loop_handlers_handle_open():
    """Test _handle_open action with new tab context creation and subSteps execution"""
    from stepwright.handlers.loop_handlers import _handle_open, _handle_foreach


    mock_page = AsyncMock()
    mock_page.url = "https://example.com/parent"

    mock_link = AsyncMock()
    mock_link.count.return_value = 1
    mock_link.get_attribute.return_value = "https://example.com/child"
    mock_page.locator = MagicMock(return_value=mock_link)

    mock_child_page = AsyncMock()
    mock_page.context.new_page.return_value = mock_child_page

    collector = {"parent_val": 123}
    step_open = BaseStep(
        id="open_tab",
        action="open",
        object="#link",
        subSteps=[BaseStep(id="child_step", action="navigate", value="https://example.com/child")]
    )

    async def mock_execute_step(pg, stp, coll, on_res=None):
        coll["child_executed"] = True

    await _handle_open(mock_page, step_open, collector, mock_execute_step)
    assert collector.get("child_executed") is True
    mock_child_page.close.assert_called_once()

    # _handle_open with count 0 skipping
    mock_link.count.return_value = 0
    await _handle_open(mock_page, step_open, collector, mock_execute_step)

    # _handle_foreach with value list source
    collector["items_list"] = [{"name": "A"}, {"name": "B"}]
    step_foreach = BaseStep(
        id="fe",
        action="foreach",
        value="{{items_list}}",
        subSteps=[BaseStep(id="s", action="navigate", value="v")]
    )
    await _handle_foreach(mock_page, step_foreach, collector, mock_execute_step)
    assert "item_0" in collector


@pytest.mark.asyncio
async def test_data_flow_excel_and_adapter_write(tmp_path):
    """Test Excel writeData, custom storage_adapter, and skipOnError error handling"""
    from stepwright.handlers.data_flow_handlers import _handle_write_data, _handle_read_data

    mock_page = AsyncMock()
    collector = {"items": [{"name": "item1", "val": 10}]}

    # writeData with storage_adapter string identifier
    step_adp = BaseStep(id="w_adp", action="writeData", key="items", value=str(tmp_path / "f.json"), storage_adapter="json")
    await _handle_write_data(mock_page, step_adp, collector)

    # writeData with excel format (new file + existing file)
    excel_path = str(tmp_path / "test.xlsx")
    step_excel = BaseStep(id="w_excel", action="writeData", key="items", value=excel_path, data_type="excel")
    await _handle_write_data(mock_page, step_excel, collector)
    assert os.path.exists(excel_path)
    # Append to existing excel
    await _handle_write_data(mock_page, step_excel, collector)

    # readData with excel format
    step_read_excel = BaseStep(id="r_excel", action="readData", value=excel_path, data_type="excel", key="excel_items")
    await _handle_read_data(mock_page, step_read_excel, collector)
    assert len(collector["excel_items"]) >= 1

    # writeData with skipOnError true (e.g. invalid type or callback exception)
    step_err_skip = BaseStep(id="w_err", action="writeData", value=str(tmp_path / "err.txt"), data_type="custom", skipOnError=True)
    await _handle_write_data(mock_page, step_err_skip, collector)


@pytest.mark.asyncio
async def test_file_handlers_additional_download_paths(tmp_path):
    """Test _handle_event_download missing element and exception paths"""
    from stepwright.handlers.file_handlers import _handle_event_download

    mock_page = AsyncMock()
    mock_target = AsyncMock()
    mock_target.is_visible.return_value = False

    with patch("stepwright.handlers.file_handlers.elem", AsyncMock(return_value=mock_target)):
        step = BaseStep(id="ev_dl", action="eventBaseDownload", object="#dl", value=str(tmp_path / "f.txt"))
        collector = {}
        await _handle_event_download(mock_page, step, collector)
        assert collector.get("ev_dl") is None

    # Exception path
    with patch("stepwright.handlers.file_handlers.elem", AsyncMock(side_effect=Exception("Elem error"))):
        step_err = BaseStep(id="ev_err", action="eventBaseDownload", object="#dl", value=str(tmp_path / "f.txt"))
        await _handle_event_download(mock_page, step_err, collector)
        assert collector.get("ev_err") is None


@pytest.mark.asyncio
async def test_network_handlers_exhaustive_coverage_sweep():

    """Test all remaining uncovered lines in network_handlers.py"""
    from stepwright.handlers.network_handlers import _handle_intercept, setup_resource_blocking

    mock_page = MagicMock()
    registered_cb = None

    def mock_on(event, cb):
        nonlocal registered_cb
        registered_cb = cb

    mock_page.on = mock_on
    collector = {}

    # Regex pattern & method mismatch predicate test
    step_intercept = BaseStep(id="int1", action="interceptResponse", object="^https://api\\.example\\.com/.*", value="POST", data_type="json", regex=r"id:(\d+)")
    await _handle_intercept(mock_page, step_intercept, collector)


    # Trigger predicate false method match
    mock_resp_get = MagicMock()
    mock_resp_get.request.method = "GET"
    mock_resp_get.url = "https://api.example.com/items"
    registered_cb(mock_resp_get)

    # Trigger JSON parse fallback to text -> json.loads
    mock_resp_post = MagicMock()
    mock_resp_post.request.method = "POST"
    mock_resp_post.url = "https://api.example.com/items"
    mock_resp_post.json = AsyncMock(side_effect=Exception("not json"))
    mock_resp_post.text = AsyncMock(return_value='{"data": "id:123"}')
    registered_cb(mock_resp_post)

    # Test resource blocking route abort & continue
    route_cb = None

    async def mock_route(url_pattern, handler):
        nonlocal route_cb
        route_cb = handler

    mock_page.route = AsyncMock(side_effect=mock_route)
    await setup_resource_blocking(mock_page, ["image", "stylesheet"])

    mock_route_img = MagicMock()
    mock_route_img.request.resource_type = "image"
    mock_route_img.abort = AsyncMock(return_value=None)
    await route_cb(mock_route_img)
    mock_route_img.abort.assert_called_once()

    mock_route_doc = MagicMock()
    mock_route_doc.request.resource_type = "document"
    mock_route_doc.continue_ = AsyncMock(return_value=None)
    await route_cb(mock_route_doc)
    mock_route_doc.continue_.assert_called_once()


@pytest.mark.asyncio
async def test_data_and_network_handlers_coverage_boost():

    """Test required empty data field error and network interception text/bytes formats"""
    import asyncio
    from stepwright.handlers.data_handlers import _handle_data_extraction
    from stepwright.handlers.network_handlers import _handle_intercept


    mock_page = AsyncMock()
    collector = {}

    # Data extraction required empty value raises ValueError
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 1
    mock_loc.first.text_content.return_value = ""
    mock_page.locator = MagicMock(return_value=mock_loc)

    step_req = BaseStep(id="d_req", action="data", object="#txt", key="k_req", required=True, data_type="text")
    with pytest.raises(ValueError, match="Required data field is empty"):
        await _handle_data_extraction(mock_page, step_req, collector)

    # Intercept missing url pattern error
    with pytest.raises(ValueError, match="requires a target URL pattern"):
        await _handle_intercept(mock_page, BaseStep(id="i_err", action="intercept"), collector)

    # Intercept format text and bytes listeners
    mock_page.on = MagicMock()
    step_txt = BaseStep(id="ic_txt", action="intercept", value="^https://example.com/api/.*", data_type="text", key="t_res")
    await _handle_intercept(mock_page, step_txt, collector)
    cb_txt = mock_page.on.call_args[0][1]

    mock_resp = AsyncMock()
    mock_resp.url = "https://example.com/api/test"
    mock_resp.request.method = "GET"
    mock_resp.text.return_value = "hello raw text"

    task = cb_txt(mock_resp)
    if asyncio.iscoroutine(task) or hasattr(task, "__await__"):
        await task
    assert collector.get("t_res") == "hello raw text"


@pytest.mark.asyncio
async def test_file_handlers_viewer_fallbacks_and_download_errors(tmp_path):
    """Test savePDF link href fallback and downloadPDF error paths"""
    from stepwright.handlers.file_handlers import _handle_save_pdf, _handle_download_pdf
    from unittest.mock import patch


    mock_page = AsyncMock()
    mock_page.url = "https://example.com/pdf_viewer"
    collector = {}

    # savePDF page.pdf exception -> direct pdf_url candidate fetch
    mock_page.pdf.side_effect = Exception("No chrome print")
    mock_page.evaluate.return_value = "https://example.com/doc.pdf"

    target_pdf = str(tmp_path / "out.pdf")
    step_spdf = BaseStep(id="spdf", action="savePDF", value=target_pdf)

    with patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_p = MagicMock()
        mock_apw.return_value.__aenter__ = AsyncMock(return_value=mock_p)
        mock_apw.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_req_ctx = MagicMock()
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.body = AsyncMock(return_value=b"%PDF-1.4 test content")
        mock_req_ctx.get = AsyncMock(return_value=mock_resp)
        mock_req_ctx.dispose = AsyncMock(return_value=None)
        mock_p.request.new_context = AsyncMock(return_value=mock_req_ctx)

        await _handle_save_pdf(mock_page, step_spdf, collector)
        assert collector.get("spdf") == target_pdf








    # downloadPDF missing object locator error
    with pytest.raises(ValueError, match="downloadPDF requires object locator"):
        await _handle_download_pdf(mock_page, BaseStep(id="dl_err", action="downloadPDF"), collector)

    # downloadPDF GET HTTP 404 response status handling
    mock_link = MagicMock()
    mock_link.count = AsyncMock(return_value=1)
    mock_link.get_attribute = AsyncMock(return_value="https://example.com/missing.pdf")
    mock_page.locator = MagicMock(return_value=mock_link)

    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status = 404
    mock_resp.status_text = "Not Found"


    with patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_p = MagicMock()
        mock_apw.return_value.__aenter__ = AsyncMock(return_value=mock_p)
        mock_apw.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_req_ctx = MagicMock()
        mock_req_ctx.get = AsyncMock(return_value=mock_resp)
        mock_req_ctx.dispose = AsyncMock(return_value=None)
        mock_p.request.new_context = AsyncMock(return_value=mock_req_ctx)

        step_dl = BaseStep(id="dl1", action="downloadPDF", object="#dl_btn", value=str(tmp_path / "missing.pdf"))
        await _handle_download_pdf(mock_page, step_dl, collector)
        assert collector.get("file") is None




@pytest.mark.asyncio
async def test_interaction_handlers_missing_elements_and_virtual_scroll():
    """Test hover, select, dragAndDrop, upload missing element logs and virtualScroll container missing path"""
    from stepwright.handlers.interaction_handlers import (
        _handle_hover,
        _handle_select,
        _handle_drag_and_drop,
        _handle_upload,
        _handle_virtual_scroll
    )
    from unittest.mock import patch


    mock_page = AsyncMock()
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 0
    mock_page.locator = MagicMock(return_value=mock_loc)
    collector = {}

    # Hover missing element
    await _handle_hover(mock_page, BaseStep(id="h1", action="hover", object="missing"), collector)

    # Select missing element
    await _handle_select(mock_page, BaseStep(id="s1", action="select", object="missing", value="opt1"), collector)

    # DragAndDrop missing elements
    await _handle_drag_and_drop(mock_page, BaseStep(id="dd1", action="dragAndDrop", object="missing_src", targetObject="missing_tgt"), collector)

    # Upload missing element
    await _handle_upload(mock_page, BaseStep(id="u1", action="uploadFile", object="missing", value="file.png"), collector)

    # VirtualScroll container missing element
    mock_vs_loc = MagicMock()
    mock_vs_loc.count = AsyncMock(return_value=1)
    mock_vs_loc.first.evaluate = AsyncMock(return_value=None)
    mock_exec_fn = AsyncMock(return_value=None)
    with patch("stepwright.handlers.interaction_handlers.find_locator_with_fallbacks", AsyncMock(return_value=(mock_vs_loc, "css", "item_selector"))):
        step_vs = BaseStep(
            id="vs1",
            action="virtualScroll",
            object="item_selector",
            virtualScrollContainer="missing_container",
            subSteps=[BaseStep(id="sub1", action="scroll", value="100")]
        )
        await _handle_virtual_scroll(mock_page, step_vs, collector, mock_exec_fn)


@pytest.mark.asyncio
async def test_loop_handlers_exhaustive_coverage_sweep():
    """Test all remaining uncovered lines in loop_handlers.py"""
    from stepwright.handlers.loop_handlers import _handle_foreach, _handle_open

    mock_page = AsyncMock()
    mock_loc = AsyncMock()
    mock_loc.count.return_value = 0
    mock_page.locator = MagicMock(return_value=mock_loc)
    collector = {}

    mock_fe_exec = AsyncMock(return_value=None)
    # foreach value missing placeholder formatting error
    step_fe_invalid_val = BaseStep(id="fe1", action="foreach", value="no_placeholder", subSteps=[BaseStep(id="sub", action="scroll", value="10")])
    await _handle_foreach(mock_page, step_fe_invalid_val, collector, mock_fe_exec)

    # foreach value not a list in collector
    collector["not_a_list"] = "just_a_string"
    step_fe_not_list = BaseStep(id="fe2", action="foreach", value="{{not_a_list}}", subSteps=[BaseStep(id="sub", action="scroll", value="10")])
    await _handle_foreach(mock_page, step_fe_not_list, collector, mock_fe_exec)

    # foreach missing subSteps exception
    collector["my_list"] = [1, 2]
    step_fe_no_sub = BaseStep(id="fe3", action="foreach", value="{{my_list}}")
    with pytest.raises(ValueError, match="foreach step requires subSteps"):
        await _handle_foreach(mock_page, step_fe_no_sub, collector, mock_fe_exec)

    # foreach subStep terminateonerror exception
    mock_exec_err = AsyncMock(side_effect=Exception("Substep error"))
    step_fe_sub_err = BaseStep(
        id="fe4",
        action="foreach",
        value="{{my_list}}",
        subSteps=[BaseStep(id="sub_err", action="scroll", value="10", terminateonerror=True)]
    )
    with pytest.raises(Exception, match="Substep error"):
        await _handle_foreach(mock_page, step_fe_sub_err, collector, mock_exec_err)

    # foreach callback exception
    mock_cb_err = AsyncMock(side_effect=Exception("Callback error"))
    step_fe_cb_err = BaseStep(
        id="fe5",
        action="foreach",
        value="{{my_list}}",
        key="res",
        subSteps=[BaseStep(id="s1", action="scroll", value="10")]
    )
    await _handle_foreach(mock_page, step_fe_cb_err, collector, mock_fe_exec, on_result=mock_cb_err)


    # open relative link (non http)
    mock_link_loc = AsyncMock()
    mock_link_loc.count.return_value = 1
    mock_link_loc.get_attribute.return_value = "/relative/path"
    mock_page.locator = MagicMock(return_value=mock_link_loc)
    mock_page.url = "https://example.com/base"

    mock_new_page = MagicMock()
    mock_new_page.goto = AsyncMock(return_value=None)
    mock_new_page.wait_for_load_state = AsyncMock(return_value=None)
    mock_new_page.close = AsyncMock(return_value=None)

    mock_ctx = MagicMock()
    mock_ctx.new_page = AsyncMock(return_value=mock_new_page)
    mock_ctx.wait_for_event = AsyncMock(return_value=mock_new_page)
    mock_page.context = mock_ctx


    mock_exec_op = AsyncMock(return_value=None)
    step_open_rel = BaseStep(id="op_rel", action="open", object="#link", subSteps=[BaseStep(id="sub_op", action="scroll", value="10")])
    await _handle_open(mock_page, step_open_rel, collector, mock_exec_op)

    # open no href Meta click attempt
    mock_link_loc.get_attribute.return_value = None
    mock_link_loc.click = AsyncMock(side_effect=[Exception("Meta click failed"), None])
    mock_ctx.wait_for_event = AsyncMock(return_value=mock_new_page)

    step_open_meta = BaseStep(id="op_meta", action="open", object="#link", subSteps=[BaseStep(id="sub_op2", action="scroll", value="10")])
    await _handle_open(mock_page, step_open_meta, collector, mock_exec_op)




    # open subStep terminateonerror exception
    mock_link_loc.get_attribute.side_effect = None
    mock_link_loc.get_attribute.return_value = "https://example.com/substep-error"
    mock_link_loc.click = AsyncMock(return_value=None)
    mock_exec_op_err = AsyncMock(side_effect=Exception("Open substep error"))
    step_open_sub_err = BaseStep(
        id="op_sub_err",
        action="open",
        object="#link",
        subSteps=[BaseStep(id="sub_err2", action="scroll", value="10", terminateonerror=True)]
    )
    await _handle_open(mock_page, step_open_sub_err, collector, mock_exec_op_err)

    # open action terminateonerror top-level exception
    mock_link_loc.count.return_value = 1
    mock_link_loc.get_attribute.side_effect = Exception("Open attribute error")
    step_open_top_err = BaseStep(
        id="op_top_err",
        action="open",
        object="#link",
        terminateonerror=True,
        subSteps=[BaseStep(id="sub3", action="scroll", value="10")]
    )
    with pytest.raises(Exception, match="Open attribute error"):
        await _handle_open(mock_page, step_open_top_err, collector, AsyncMock())


@pytest.mark.asyncio
async def test_network_intercept_response_branches(monkeypatch):
    """Exercise network response formats, method filtering, regex transforms, and routes."""
    import asyncio
    from stepwright.handlers.network_handlers import _handle_intercept, setup_resource_blocking

    created = []
    original_create_task = asyncio.create_task

    def capture_task(coro):
        task = original_create_task(coro)
        created.append(task)
        return task

    monkeypatch.setattr("stepwright.handlers.network_handlers.asyncio.create_task", capture_task)

    mock_page = AsyncMock()
    mock_page.on = MagicMock()
    collector = {"tenant": "acme"}

    step_json_fallback = BaseStep(
        id="json_fallback",
        action="intercept",
        object="https://api.example.com/{{tenant}}/*",
        value="POST",
        data_type="json",
        key="json_payload",
    )
    await _handle_intercept(mock_page, step_json_fallback, collector)
    cb = mock_page.on.call_args[0][1]

    wrong_method = AsyncMock()
    wrong_method.url = "https://api.example.com/acme/items"
    wrong_method.request.method = "GET"
    cb(wrong_method)
    await asyncio.gather(*created)
    assert "json_payload" not in collector

    created.clear()
    json_text = AsyncMock()
    json_text.url = "https://api.example.com/acme/items"
    json_text.request.method = "POST"
    json_text.json.side_effect = ValueError("not json api")
    json_text.text.return_value = '{"ok": true}'
    cb(json_text)
    await asyncio.gather(*created)
    assert collector["json_payload"] == {"ok": True}

    created.clear()
    step_regex = BaseStep(
        id="regex_text",
        action="intercept",
        object="^https://cdn\\.example\\.com/report$",
        data_type="text",
        regex=r"total=(\d+)",
        regexGroup=1,
        key="total",
    )
    await _handle_intercept(mock_page, step_regex, collector)
    cb = mock_page.on.call_args[0][1]
    text_resp = AsyncMock()
    text_resp.url = "https://cdn.example.com/report"
    text_resp.request.method = "GET"
    text_resp.text.return_value = "status=ok total=42"
    cb(text_resp)
    await asyncio.gather(*created)
    assert collector["total"] == "42"

    created.clear()
    step_bytes = BaseStep(id="bytes", action="intercept", object="blob", data_type="bytes")
    await _handle_intercept(mock_page, step_bytes, collector)
    cb = mock_page.on.call_args[0][1]
    bytes_resp = AsyncMock()
    bytes_resp.url = "https://example.com/blob.bin"
    bytes_resp.request.method = "GET"
    bytes_resp.body.return_value = b"abc"
    cb(bytes_resp)
    await asyncio.gather(*created)
    assert collector["bytes"] == b"abc"

    route = AsyncMock()
    route.request.resource_type = "image"
    await setup_resource_blocking(mock_page, ["image"])
    handler = mock_page.route.call_args[0][1]
    await handler(route)
    route.abort.assert_awaited_once()

    route2 = AsyncMock()
    route2.request.resource_type = "xhr"
    await handler(route2)
    route2.continue_.assert_awaited_once()


@pytest.mark.asyncio
async def test_file_handlers_additional_download_paths(tmp_path):
    """Cover event downloads plus save/download fallback misses and relative URL fetches."""
    from unittest.mock import patch
    from stepwright.handlers.file_handlers import _handle_event_download, _handle_save_pdf, _handle_download_pdf

    collector = {"name": "report"}

    mock_page = AsyncMock()
    mock_page.url = "https://example.com/base/viewer"
    mock_target = AsyncMock()
    mock_target.is_visible.return_value = True
    mock_page.locator = MagicMock(return_value=mock_target)

    class DownloadInfo:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        @property
        async def value(self):
            dl = AsyncMock()
            dl.save_as.side_effect = lambda path: pathlib.Path(path).write_bytes(b"downloaded")
            return dl

    mock_page.expect_download = MagicMock(return_value=DownloadInfo())
    event_path = str(tmp_path / "event.txt")
    await _handle_event_download(
        mock_page,
        BaseStep(id="ed", action="eventBaseDownload", object="#download", value=event_path, key="event_file"),
        collector,
    )
    assert pathlib.Path(event_path).read_bytes() == b"downloaded"
    assert collector["event_file"] == event_path

    mock_page.wait_for_load_state.side_effect = Exception("load state unavailable")
    mock_page.evaluate.side_effect = [None, []]
    mock_page.frames = [mock_page]
    mock_page.main_frame = mock_page
    missing_pdf = str(tmp_path / "{{name}}.pdf")
    await _handle_save_pdf(
        mock_page,
        BaseStep(id="sp_missing", action="savePDF", value=missing_pdf, key="missing_pdf"),
        collector,
    )
    assert collector["missing_pdf"] is None

    mock_link = AsyncMock()
    mock_link.count.return_value = 1
    mock_link.get_attribute.return_value = "files/doc.pdf"
    mock_page.locator = MagicMock(return_value=mock_link)

    mock_resp = AsyncMock()
    mock_resp.ok = True
    mock_resp.body.return_value = b"%PDF relative"
    mock_req = AsyncMock()
    mock_req.get.return_value = mock_resp
    mock_pw = AsyncMock()
    mock_pw.request.new_context.return_value = mock_req

    with patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_pw
        mock_apw.return_value = mock_cm

        out_path = str(tmp_path / "relative.pdf")
        await _handle_download_pdf(
            mock_page,
            BaseStep(id="rel", action="downloadPDF", object="#rel", value=out_path, key="relative_file"),
            collector,
        )
        assert pathlib.Path(out_path).read_bytes() == b"%PDF relative"
        assert collector["relative_file"] == out_path


@pytest.mark.asyncio
async def test_data_flow_remaining_branches(tmp_path, monkeypatch):
    """Cover custom read/write branches, empty writes, non-list coercion, and skipOnError."""
    from stepwright.handlers.data_flow_handlers import (
        _close_openpyxl_workbook,
        _handle_read_data,
        _handle_write_data,
    )

    class BrokenWorkbook:
        _archive = object()

        def close(self):
            raise RuntimeError("close failed")

    class BrokenArchive:
        def close(self):
            raise RuntimeError("archive failed")

    wb = BrokenWorkbook()
    wb._archive = BrokenArchive()
    _close_openpyxl_workbook(wb)

    collector = {"rows": [], "single": {"a": 1}, "plain": ["x", "y"]}
    mock_page = AsyncMock()

    empty_csv = tmp_path / "empty.csv"
    await _handle_write_data(
        mock_page,
        BaseStep(id="empty", action="writeData", key="rows", value=str(empty_csv), data_type="csv"),
        collector,
    )
    assert not empty_csv.exists()

    one_csv = tmp_path / "one.csv"
    await _handle_write_data(
        mock_page,
        BaseStep(id="single", action="writeData", key="single", value=str(one_csv), data_type="csv"),
        collector,
    )
    assert "a" in one_csv.read_text()

    overwrite_txt = tmp_path / "overwrite.txt"
    await _handle_write_data(
        mock_page,
        BaseStep(
            id="text",
            action="writeData",
            key="plain",
            value=str(overwrite_txt),
            data_type="text",
            continueOnEmpty=False,
        ),
        collector,
    )
    assert overwrite_txt.read_text() == "x\ny\n"

    async def custom_reader(path, step):
        return {"path": pathlib.Path(path).name, "step": step.id}

    await _handle_read_data(
        mock_page,
        BaseStep(id="custom_read", action="readData", value=str(tmp_path / "missing.custom"), data_type="custom", callback=custom_reader),
        collector,
    )
    assert collector["custom_read"]["step"] == "custom_read"

    async def custom_writer(path, data, step):
        pathlib.Path(path).write_text(data["message"])

    collector["custom_payload"] = {"message": "hello"}
    custom_out = tmp_path / "custom.txt"
    await _handle_write_data(
        mock_page,
        BaseStep(
            id="custom_write",
            action="writeData",
            key="custom_payload",
            value=str(custom_out),
            data_type="custom",
            callback=custom_writer,
        ),
        collector,
    )
    assert custom_out.read_text() == "hello"

    await _handle_read_data(
        mock_page,
        BaseStep(
            id="skip_read",
            action="readData",
            value=str(tmp_path / "missing.json"),
            data_type="custom",
            skipOnError=True,
        ),
        collector,
    )

    def boom_writer(path, data, step):
        raise RuntimeError("writer failed")

    await _handle_write_data(
        mock_page,
        BaseStep(
            id="skip_write",
            action="writeData",
            key="custom_payload",
            value=str(tmp_path / "skip.txt"),
            data_type="custom",
            callback=boom_writer,
            skipOnError=True,
        ),
        collector,
    )

    original_import = __import__

    def fail_openpyxl_import(name, *args, **kwargs):
        if name == "openpyxl":
            raise ImportError()
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fail_openpyxl_import)
    with pytest.raises(ImportError):
        await _handle_read_data(
            mock_page,
            BaseStep(id="excel_no_import", action="readData", value=str(one_csv), data_type="excel"),
            collector,
        )


@pytest.mark.asyncio
async def test_page_actions_remaining_branches(monkeypatch, tmp_path):
    """Cover page action success/error branches not hit by browser tests."""
    import asyncio
    from stepwright.handlers.page_actions import (
        _handle_reload,
        _handle_screenshot,
        _handle_wait_for_selector,
        _handle_get_meta,
        _handle_get_cookies,
        _handle_get_local_storage,
        _handle_get_session_storage,
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

    page = AsyncMock()
    page.url = "https://example.com"
    page.viewport_size = None
    collector = {"token": "abc", "headers": {"X-Test": "1"}}

    await _handle_reload(page, BaseStep(id="reload", action="reload", value="bad"), collector)
    page.reload.assert_awaited_with(wait_until="load")

    missing = AsyncMock()
    missing.count.return_value = 0
    page.locator = MagicMock(return_value=missing)
    shot_path = str(tmp_path / "full.png")
    await _handle_screenshot(page, BaseStep(id="shot", action="screenshot", object="#missing", value=shot_path, key="shot"), collector)
    page.screenshot.assert_awaited_with(path=shot_path, full_page=True)
    assert collector["shot"] == shot_path

    element = AsyncMock()
    element.count.return_value = 1
    page.locator = MagicMock(return_value=element)
    await _handle_screenshot(page, BaseStep(id="element_shot", action="screenshot", object="#el", value=str(tmp_path / "el.png")), collector)
    element.first.screenshot.assert_awaited()

    page.screenshot.side_effect = RuntimeError("boom")
    with pytest.raises(RuntimeError):
        await _handle_screenshot(page, BaseStep(id="bad_shot", action="screenshot", value=str(tmp_path / "bad.png"), terminateonerror=True), collector)
    page.screenshot.side_effect = None

    wait_loc = AsyncMock()
    wait_loc.wait_for.side_effect = RuntimeError("not found")
    page.locator = MagicMock(return_value=wait_loc)
    await _handle_wait_for_selector(page, BaseStep(id="wait", action="waitForSelector", object="#x", value="invalid", key="waited"), collector)
    assert collector["waited"] is False
    with pytest.raises(RuntimeError):
        await _handle_wait_for_selector(page, BaseStep(id="wait_term", action="waitForSelector", object="#x", terminateonerror=True), collector)

    page.evaluate.side_effect = [
        {"description": "site"},
        {"a": "1"},
        {"s": "2"},
        {"width": 800, "height": 600},
        "eval-result",
    ]
    await _handle_get_meta(page, BaseStep(id="meta_all", action="getMeta"), collector)
    await _handle_get_local_storage(page, BaseStep(id="ls_all", action="getLocalStorage"), collector)
    await _handle_get_session_storage(page, BaseStep(id="ss_all", action="getSessionStorage"), collector)
    await _handle_get_viewport_size(page, BaseStep(id="vp_eval", action="getViewportSize"), collector)
    await _handle_evaluate(page, BaseStep(id="eval", action="evaluate", value="'ok'"), collector)
    assert collector["meta_all"] == {"description": "site"}
    assert collector["vp_eval"] == {"width": 800, "height": 600}

    page.context.cookies.return_value = [{"name": "a", "value": "1"}, {"name": "b", "value": "2"}]
    await _handle_get_cookies(page, BaseStep(id="cookies", action="getCookies"), collector)
    assert collector["cookies"] == {"a": "1", "b": "2"}

    with pytest.raises(ValueError):
        await _handle_set_viewport_size(page, BaseStep(id="bad_vp", action="setViewportSize", value="wide"), collector)

    page.evaluate.side_effect = RuntimeError("bad js")
    await _handle_evaluate(page, BaseStep(id="eval_bad", action="evaluate", value="'bad'", key="eval_bad"), collector)
    assert collector["eval_bad"] is None
    with pytest.raises(RuntimeError):
        await _handle_evaluate(page, BaseStep(id="eval_term", action="evaluate", value="'bad'", terminateonerror=True), collector)
    page.evaluate.side_effect = None

    loc = AsyncMock()
    page.locator = MagicMock(return_value=loc)
    await _handle_press(page, BaseStep(id="press_el", action="press", object="#input", value="Enter"), collector)
    loc.press.assert_awaited_with("Enter")
    await _handle_press(page, BaseStep(id="press_page", action="press", value="Escape"), collector)
    page.keyboard.press.assert_awaited_with("Escape")
    with pytest.raises(ValueError):
        await _handle_press(page, BaseStep(id="press_bad", action="press"), collector)

    await _handle_type(
        page,
        BaseStep(id="type", action="type", object="#input", value="{{token}}", clearBeforeInput=True, inputDelay=5),
        collector,
    )
    loc.fill.assert_awaited_with("")
    loc.type.assert_awaited_with("abc", delay=5)
    with pytest.raises(ValueError):
        await _handle_type(page, BaseStep(id="type_bad", action="type", value="x"), collector)
    with pytest.raises(ValueError):
        await _handle_type(page, BaseStep(id="type_bad2", action="type", object="#input"), collector)

    created = []
    original_create_task = asyncio.create_task

    def capture_task(coro):
        task = original_create_task(coro)
        created.append(task)
        return task

    monkeypatch.setattr("stepwright.handlers.page_actions.asyncio.create_task", capture_task)
    page.on = MagicMock()
    await _handle_dialog(page, BaseStep(id="dialog", action="dialog", value="dismiss"), collector)
    dialog_cb = page.on.call_args[0][1]
    dialog = AsyncMock()
    dialog.message = "hello"
    dialog_cb(dialog)
    await asyncio.gather(*created)
    dialog.dismiss.assert_awaited_once()

    await _handle_mouse_move(page, BaseStep(id="mouse_el", action="mouseMove", object="#button"), collector)
    loc.hover.assert_awaited()
    await _handle_mouse_move(page, BaseStep(id="mouse_xy", action="mouseMove", value="10x20"), collector)
    page.mouse.move.assert_awaited_with(10, 20)
    with pytest.raises(ValueError):
        await _handle_mouse_move(page, BaseStep(id="mouse_bad", action="mouseMove", value="10"), collector)
    with pytest.raises(ValueError):
        await _handle_mouse_move(page, BaseStep(id="mouse_missing", action="mouseMove"), collector)

    await _handle_wait_for_navigation(page, BaseStep(id="nav_load", action="waitForNavigation", value="load", wait=12), collector)
    page.wait_for_load_state.assert_awaited_with("load", timeout=12)
    await _handle_wait_for_navigation(page, BaseStep(id="nav_url", action="waitForNavigation", value="**/done"), collector)
    page.wait_for_url.assert_awaited_with("**/done", timeout=30000)

    await _handle_set_headers(page, BaseStep(id="headers", action="setHeaders", key="headers"), collector)
    page.set_extra_http_headers.assert_awaited_with({"X-Test": "1"})

@pytest.mark.asyncio
async def test_save_pdf_viewer_click_frame_and_href_fallbacks(tmp_path):
    """Cover savePDF viewer-click, frame-click, href-fetch, and failed fetch fallback paths."""
    from unittest.mock import patch
    from stepwright.handlers.file_handlers import _handle_save_pdf

    class DownloadInfo:
        def __init__(self, payload):
            self.payload = payload

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        @property
        async def value(self):
            dl = AsyncMock()
            dl.save_as.side_effect = lambda path: pathlib.Path(path).write_bytes(self.payload)
            return dl

    page = AsyncMock()
    page.url = "https://example.com/viewer"
    page.context.cookies.return_value = [{"name": "sid", "value": "123"}]
    page.frames = [page]
    page.main_frame = page
    collector = {"slug": "doc"}

    page.evaluate.side_effect = [None, True]
    page.expect_download = MagicMock(return_value=DownloadInfo(b"main click"))
    out = str(tmp_path / "{{slug}}-main.pdf")
    await _handle_save_pdf(page, BaseStep(id="main_click", action="savePDF", value=out, key="main"), collector)
    resolved = str(tmp_path / "doc-main.pdf")
    assert pathlib.Path(resolved).read_bytes() == b"main click"
    assert collector["main"] == resolved

    frame = AsyncMock()
    page.evaluate.side_effect = [None, False]
    frame.evaluate.return_value = True
    page.frames = [page, frame]
    page.expect_download = MagicMock(return_value=DownloadInfo(b"frame click"))
    out = str(tmp_path / "frame.pdf")
    await _handle_save_pdf(page, BaseStep(id="frame_click", action="savePDF", value=out, key="frame"), collector)
    assert pathlib.Path(out).read_bytes() == b"frame click"

    page.frames = [page]
    page.evaluate.side_effect = [None, ["https://example.com/download.pdf"]]
    page.expect_download = MagicMock(side_effect=RuntimeError("no click download"))

    mock_resp = AsyncMock()
    mock_resp.ok = True
    mock_resp.body.return_value = b"href pdf"
    mock_req = AsyncMock()
    mock_req.get.return_value = mock_resp
    mock_pw = AsyncMock()
    mock_pw.request.new_context.return_value = mock_req

    with patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_pw
        mock_apw.return_value = mock_cm

        href_out = str(tmp_path / "href.pdf")
        await _handle_save_pdf(page, BaseStep(id="href", action="savePDF", value=href_out, key="href"), collector)
        assert pathlib.Path(href_out).read_bytes() == b"href pdf"

    page.evaluate.side_effect = ["/relative.pdf"]
    page.expect_download = MagicMock(side_effect=RuntimeError("no click download"))
    bad_resp = MagicMock()
    bad_resp.ok = False
    bad_resp.status = 500
    bad_resp.status_text.return_value = "Server Error"
    bad_req = AsyncMock()
    bad_req.get.return_value = bad_resp
    bad_pw = AsyncMock()
    bad_pw.request.new_context.return_value = bad_req

    with patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = bad_pw
        mock_apw.return_value = mock_cm

        failed_out = str(tmp_path / "failed.pdf")
        await _handle_save_pdf(page, BaseStep(id="failed", action="savePDF", value=failed_out, key="failed"), collector)
        assert collector["failed"] is None


@pytest.mark.asyncio
async def test_download_pdf_popup_empty_href_and_exception_paths(tmp_path):
    """Cover downloadPDF popup wait fallback, empty href, and outer exception handling."""
    from unittest.mock import patch
    from stepwright.handlers.file_handlers import _handle_download_pdf

    page = AsyncMock()
    page.url = "https://example.com/viewer"
    collector = {}

    link = AsyncMock()
    link.count.return_value = 1
    link.get_attribute.return_value = None
    link.click.side_effect = [RuntimeError("meta unsupported"), None]
    page.locator = MagicMock(return_value=link)

    new_page = AsyncMock()
    new_page.url = ""
    new_page.wait_for_load_state.side_effect = RuntimeError("load failed")
    page.context.wait_for_event = AsyncMock(return_value=new_page)

    await _handle_download_pdf(
        page,
        BaseStep(id="empty_href", action="downloadPDF", object="#pdf", value=str(tmp_path / "empty.pdf"), key="empty"),
        collector,
    )
    assert collector["empty"] is None
    new_page.close.assert_awaited_once()

    broken = AsyncMock()
    broken.count.side_effect = RuntimeError("locator exploded")
    page.locator = MagicMock(return_value=broken)
    await _handle_download_pdf(
        page,
        BaseStep(id="broken", action="downloadPDF", object="#pdf", value=str(tmp_path / "broken.pdf"), key="broken"),
        collector,
    )
    assert collector["broken"] is None

    ok_link = AsyncMock()
    ok_link.count.return_value = 1
    ok_link.get_attribute.return_value = "https://example.com/ok.pdf"
    page.locator = MagicMock(return_value=ok_link)
    page.context.cookies.return_value = []

    req = AsyncMock()
    req.get.side_effect = RuntimeError("network down")
    pw = AsyncMock()
    pw.request.new_context.return_value = req
    with patch("stepwright.handlers.file_handlers.async_playwright") as mock_apw:
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = pw
        mock_apw.return_value = mock_cm

        await _handle_download_pdf(
            page,
            BaseStep(id="network_error", action="downloadPDF", object="#pdf", value=str(tmp_path / "net.pdf"), key="net"),
            collector,
        )
        assert collector["net"] is None











