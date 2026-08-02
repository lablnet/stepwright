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
    assert helpers.replace_data_placeholders(None, collector) is None
    assert helpers.replace_data_placeholders("{{ missing }}", collector) == "_missing_"
    assert helpers.replace_data_placeholders("{{ none }}", {"none": None}) == "{{ none }}"


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
    helpers.locator_for(mock_ctx, "css", ".custom")
    mock_ctx.locator.assert_called_with(".custom")


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
    assert helpers.flatten_nested_foreach_results({"title": "solo"}) == {"title": "solo"}
    assert helpers.flatten_nested_foreach_results({"cat": "x", "item_0": None}) == []


def test_transform_data_regex():
    assert helpers.transform_data_regex("Price $100", r"\$(\d+)", 1) == "100"
    assert helpers.transform_data_regex("Price $100", r"\$(\d+)", 99) == "$100"
    assert helpers.transform_data_regex("", r"x", 0) == ""
    assert helpers.transform_data_regex("abc", r"(", 1) == "abc"


@pytest.mark.asyncio
async def test_apply_random_delay():
    mock_page = AsyncMock()
    await helpers.apply_random_delay(mock_page, {"min": 10, "max": 50})
    mock_page.wait_for_timeout.assert_called_once()
    await helpers.apply_random_delay(mock_page, None)
    await helpers.apply_random_delay(mock_page, {"min": 50, "max": 10})
    mock_page.wait_for_timeout.assert_called_once()


@pytest.mark.asyncio
async def test_ensure_dir():
    await helpers._ensure_dir("tmp_test_dir/file.txt")


@pytest.mark.asyncio
async def test_evaluate_condition_and_helpers_edge_cases():
    """Test evaluate_condition JS string evaluation and custom loop index keys"""
    mock_page = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value=True)

    collector = {"var_val": "abc"}
    res = await helpers.evaluate_condition(mock_page, "var_val == 'abc'", collector)
    assert res is True

    # Custom index key placeholder replacement
    assert helpers.replace_index_placeholders("item_{{ k }}", 4, char="k") == "item_4"
    assert helpers.replace_index_placeholders("item_{{ k_plus1 }}", 4, char="k") == "item_5"

    mock_page.evaluate.side_effect = RuntimeError("bad condition")
    assert await helpers.evaluate_condition(mock_page, "bad js", collector) is False


@pytest.mark.asyncio
async def test_locator_fallback_wait_and_transform_edges():
    page = MagicMock()
    primary = AsyncMock()
    primary.count.return_value = 0
    fallback_missing = AsyncMock()
    fallback_missing.count.return_value = 0
    fallback_hit = AsyncMock()
    fallback_hit.count.return_value = 1
    page.locator.side_effect = [primary, fallback_missing, fallback_hit]

    loc, used_type, used_selector = await helpers.find_locator_with_fallbacks(
        page,
        None,
        "id",
        "missing",
        [
            {"object_type": "class", "object": "also-missing"},
            {"object_type": "tag", "object": "button"},
        ],
    )
    assert loc is fallback_hit
    assert (used_type, used_selector) == ("tag", "button")

    page.locator.side_effect = [primary]
    loc, used_type, used_selector = await helpers.find_locator_with_fallbacks(
        page,
        None,
        "id",
        "missing",
        [{"object_type": "", "object": "ignored"}],
    )
    assert (loc, used_type, used_selector) == (None, None, None)

    wait_loc = AsyncMock()
    page.locator.side_effect = None
    page.locator.return_value = wait_loc
    step = MagicMock()
    step.waitForSelector = "#ready"
    step.waitForSelectorTimeout = 5
    step.waitForSelectorState = "attached"
    step.object_type = "css"
    await helpers.wait_for_selector_if_configured(page, step, None)
    wait_loc.wait_for.assert_awaited_with(state="attached", timeout=5)

    wait_loc.wait_for.side_effect = RuntimeError("not ready")
    await helpers.wait_for_selector_if_configured(page, step, None)

    step.waitForSelector = None
    await helpers.wait_for_selector_if_configured(page, step, None)

    transform_page = AsyncMock()
    transform_page.evaluate.return_value = "ABC"
    assert await helpers.apply_transform(transform_page, "abc", "value.toUpperCase()", {}) == "ABC"
    assert await helpers.apply_transform(transform_page, None, "value", {}) is None
    transform_page.evaluate.side_effect = RuntimeError("bad transform")
    assert await helpers.apply_transform(transform_page, "abc", "bad", {}) == "abc"
