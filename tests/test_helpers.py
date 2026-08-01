# tests/test_helpers.py
# Unit tests for helper utility functions in StepWright

import pytest
from unittest.mock import MagicMock, AsyncMock
import stepwright.helpers as helpers


@pytest.mark.asyncio
async def test_replace_index_placeholders():
    assert helpers.replace_index_placeholders(None, 0) is None
    assert helpers.replace_index_placeholders("item_{{ i }}", 2) == "item_2"
    assert helpers.replace_index_placeholders("item_{{i_plus1}}", 2) == "item_3"


def test_replace_data_placeholders():
    collector = {"category": "News & Updates!", "count": 10}
    res = helpers.replace_data_placeholders("file_{{ category }}.json", collector)
    assert "News" in res


def test_locator_for():
    mock_ctx = MagicMock()
    helpers.locator_for(mock_ctx, "id", "my-id")
    mock_ctx.locator.assert_called_with("#my-id")
    helpers.locator_for(mock_ctx, "class", "my-class")
    mock_ctx.locator.assert_called_with(".my-class")
    helpers.locator_for(mock_ctx, "xpath", "//div")
    mock_ctx.locator.assert_called_with("xpath=//div")
    helpers.locator_for(mock_ctx, "tag", "h1")
    mock_ctx.locator.assert_called_with("h1")
    helpers.locator_for(mock_ctx, None, "span")
    mock_ctx.locator.assert_called_with("span")


@pytest.mark.asyncio
async def test_maybe_await():
    assert await helpers.maybe_await("sync_val") == "sync_val"
    async def async_fn(): return "async_val"
    assert await helpers.maybe_await(async_fn()) == "async_val"


def test_flatten_nested_foreach_results():
    nested_data = {
        "cat": "tech",
        "item_0": [{"title": "t1"}, {"title": "t2"}],
        "item_1": {"title": "t3"},
        "item_2": "primitive"
    }
    flattened = helpers.flatten_nested_foreach_results(nested_data)
    assert isinstance(flattened, list)
    assert len(flattened) == 4


def test_transform_data_regex():
    assert helpers.transform_data_regex("Price $100", r"\$(\d+)", 1) == "100"
    assert helpers.transform_data_regex("Price $100", r"\$(\d+)", 99) == "$100"


@pytest.mark.asyncio
async def test_apply_random_delay():
    mock_page = AsyncMock()
    await helpers.apply_random_delay(mock_page, {"min": 10, "max": 50})
    mock_page.wait_for_timeout.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_dir():
    await helpers._ensure_dir("tmp_test_dir/file.txt")
