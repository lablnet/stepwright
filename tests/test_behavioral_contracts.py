"""Behavioral contracts for results, retries, cleanup, and storage adapters."""

import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from stepwright import (
    BaseStorageAdapter,
    BaseStep,
    CSVFileAdapter,
    JSONFileAdapter,
    SQLiteAdapter,
    TabTemplate,
    XMLFileAdapter,
)
from stepwright.scraper import get_device_preset
from stepwright import executor as executor_module
from stepwright import parser as parser_module


@pytest.mark.asyncio
async def test_end_to_end_scrape_returns_expected_records(test_page_url):
    template = TabTemplate(
        tab="behavioral-contract",
        steps=[
            BaseStep(id="navigate", action="navigate", value=test_page_url),
            BaseStep(
                id="articles",
                action="foreach",
                object_type="class",
                object="article",
                subSteps=[
                    BaseStep(id="title", action="data", object_type="tag", object="h2", key="title", data_type="text"),
                    BaseStep(id="link", action="data", object_type="tag", object="a/@href", key="link", data_type="attribute"),
                ],
            ),
        ],
    )

    results = await parser_module.run_scraper([template])

    assert [item["title"] for item in results] == [
        "First Article Title",
        "Second Article Title",
        "Third Article Title",
        "Fourth Article Title",
    ]
    assert results[0]["link"] == "https://example.com/article1"


@pytest.mark.asyncio
async def test_run_scraper_closes_page_context_and_browser_on_step_failure(monkeypatch):
    browser = MagicMock()
    browser.close = AsyncMock()
    context = MagicMock()
    context.close = AsyncMock()
    page = MagicMock()
    page.close = AsyncMock()
    browser.new_context = AsyncMock(return_value=context)
    context.new_page = AsyncMock(return_value=page)

    monkeypatch.setattr(parser_module, "get_browser", AsyncMock(return_value=browser))
    monkeypatch.setattr(parser_module, "_shutdown_playwright", AsyncMock())

    async def fail_execute(*args, **kwargs):
        raise RuntimeError("expected step failure")

    monkeypatch.setattr(parser_module, "execute_tab", fail_execute)
    template = TabTemplate(tab="cleanup", steps=[BaseStep(id="boom", action="custom")])

    with pytest.raises(RuntimeError, match="expected step failure"):
        await parser_module.run_scraper_with_metrics([template], parser_module.RunOptions())

    page.close.assert_awaited_once()
    browser.close.assert_awaited_once()
    parser_module._shutdown_playwright.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_succeeds_after_transient_failure(monkeypatch):
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()
    step = BaseStep(id="retry", action="custom", retry=2, retryDelay=1)
    calls = 0

    async def flaky(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("transient")

    monkeypatch.setattr(executor_module, "_execute_step_internal", flaky)
    await executor_module.execute_step(page, step, {})

    assert calls == 2
    page.wait_for_timeout.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retry_raises_after_max_attempts_and_records_failure(monkeypatch):
    page = MagicMock()
    page.wait_for_timeout = AsyncMock()
    step = BaseStep(id="always-fails", action="custom", retry=2, retryDelay=3)
    metrics = executor_module.ExecutionMetrics()

    async def always_fail(*args, **kwargs):
        raise RuntimeError("permanent")

    monkeypatch.setattr(executor_module, "_execute_step_internal", always_fail)
    with pytest.raises(RuntimeError, match="permanent"):
        await executor_module.execute_step(page, step, {}, metrics=metrics)

    assert page.wait_for_timeout.await_count == 2
    assert metrics.failed_steps_count == 1
    assert metrics.step_metrics[-1].success is False
    assert metrics.step_metrics[-1].error == "permanent"


@pytest.mark.parametrize("adapter_type, suffix", [
    (JSONFileAdapter, ".json"),
    (CSVFileAdapter, ".csv"),
    (XMLFileAdapter, ".xml"),
])
def test_file_adapter_contract_round_trip(adapter_type, suffix, tmp_path):
    path = tmp_path / f"records{suffix}"
    records = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]
    adapter = adapter_type(file_path=str(path))

    assert adapter.write(records) is True
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "Ada" in text and "Grace" in text
    adapter.close()


def test_sqlite_adapter_contract_persists_all_records(tmp_path):
    path = tmp_path / "records.sqlite"
    adapter = SQLiteAdapter(db_path=str(path), table_name="records")
    records = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]

    assert adapter.write(records) is True
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT id, name FROM records ORDER BY id").fetchall()

    assert rows == [("1", "Ada"), ("2", "Grace")]
    adapter.close()


def test_template_serialization_handles_lists_and_plain_values(tmp_path):
    step = BaseStep(id="step", action="navigate", value="https://example.test")
    path = tmp_path / "templates.json"

    saved = parser_module.save_template([step, {"raw": True}], path)
    assert json.loads(saved)[1] == {"raw": True}
    assert json.loads(parser_module.template_to_json([step, {"raw": True}]))[1] == {"raw": True}
    assert json.loads(parser_module.template_to_json({"plain": True})) == {"plain": True}
    assert json.loads(parser_module.template_to_json(step))["action"] == "navigate"


def test_base_storage_adapter_contract_methods_are_callable():
    class MinimalAdapter(BaseStorageAdapter):
        def connect(self):
            return super().connect()

        def write(self, data, options=None):
            return super().write(data, options)

        def close(self):
            return super().close()

    adapter = MinimalAdapter()
    assert adapter.connect() is None
    assert adapter.write([]) is None
    assert adapter.close() is None


@pytest.mark.asyncio
async def test_unknown_device_preset_has_actionable_error(monkeypatch):
    monkeypatch.setattr("stepwright.scraper._get_pw", AsyncMock(return_value=SimpleNamespace(devices={"Known": {}})))
    with pytest.raises(ValueError, match="Unknown device preset"):
        await get_device_preset("Missing")


@pytest.mark.asyncio
async def test_public_result_actions_store_expected_values():
    page = MagicMock()
    page.url = "https://example.test/items"
    page.title = AsyncMock(return_value="Items")
    page.context.cookies = AsyncMock(return_value=[{"name": "session", "value": "abc"}])
    page.evaluate = AsyncMock(side_effect=[{"description": "demo"}, {"token": "xyz"}, "evaluated"])
    page.viewport_size = {"width": 800, "height": 600}
    collector = {}

    actions = [
        BaseStep(id="url", action="getUrl", key="url"),
        BaseStep(id="title", action="getTitle", key="title"),
        BaseStep(id="meta", action="getMeta", key="meta"),
        BaseStep(id="cookie", action="getCookies", object="session", key="cookie"),
        BaseStep(id="storage", action="getLocalStorage", key="storage"),
        BaseStep(id="viewport", action="getViewportSize", key="viewport"),
        BaseStep(id="eval", action="evaluate", value="return 1", key="eval"),
    ]

    for step in actions:
        await executor_module._execute_step_internal(page, step, collector)

    assert collector["url"] == "https://example.test/items"
    assert collector["title"] == "Items"
    assert collector["meta"] == {"description": "demo"}
    assert collector["cookie"] == "abc"
    assert collector["storage"] == {"token": "xyz"}
    assert collector["viewport"] == {"width": 800, "height": 600}
    assert collector["eval"] == "evaluated"
