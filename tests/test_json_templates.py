# test_json_templates.py
# Unit tests for JSON template export, import, loading, and execution

import json
from pathlib import Path
import pytest

from stepwright import (
    BaseStep,
    PaginationConfig,
    NextButtonConfig,
    ScrollConfig,
    ProxyConfig,
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    load_template,
    save_template,
    template_to_json,
    template_from_json,
    parse_template_from_dict,
    run_scraper,
)


def test_basestep_serialization(tmp_path: Path):
    step = BaseStep(
        id="step_1",
        action="data",
        object_type="css",
        object="h1.title",
        key="page_title",
        data_type="text",
        subSteps=[
            BaseStep(id="sub_1", action="click", object_type="id", object="btn")
        ]
    )

    d = step.to_dict()
    assert d["id"] == "step_1"
    assert d["action"] == "data"
    assert len(d["subSteps"]) == 1
    assert d["subSteps"][0]["id"] == "sub_1"

    # From dict
    restored = BaseStep.from_dict(d)
    assert restored.id == step.id
    assert restored.subSteps[0].id == "sub_1"

    # To JSON file and back
    json_path = tmp_path / "step.json"
    step.to_json(json_path)
    assert json_path.exists()

    from_file = BaseStep.from_json(json_path)
    assert from_file.id == step.id
    assert from_file.object == step.object


def test_tabtemplate_serialization(tmp_path: Path):
    template = TabTemplate(
        tab="test_tab",
        steps=[
            BaseStep(id="s1", action="navigate", value="https://example.com"),
            BaseStep(id="s2", action="data", object_type="css", object="h1", key="title", data_type="text"),
        ],
        pagination=PaginationConfig(
            strategy="next",
            nextButton=NextButtonConfig(object_type="css", object="a.next", wait=1000),
            maxPages=3,
        ),
        proxy=ProxyConfig(server="http://127.0.0.1:8080", username="user", password="pass"),
        stealth=True,
    )

    # To dict
    d = template.to_dict()
    assert d["type"] == "TabTemplate"
    assert d["tab"] == "test_tab"
    assert len(d["steps"]) == 2
    assert d["pagination"]["strategy"] == "next"
    assert d["pagination"]["nextButton"]["object"] == "a.next"
    assert d["proxy"]["server"] == "http://127.0.0.1:8080"

    # From dict
    restored = TabTemplate.from_dict(d)
    assert isinstance(restored, TabTemplate)
    assert restored.tab == "test_tab"
    assert len(restored.steps) == 2
    assert restored.pagination.nextButton.object == "a.next"
    assert isinstance(restored.proxy, ProxyConfig)
    assert restored.proxy.username == "user"

    # Save to JSON file
    file_path = tmp_path / "template.json"
    save_template(template, file_path)
    assert file_path.exists()

    # Load using top-level load_template
    loaded = load_template(file_path)
    assert isinstance(loaded, TabTemplate)
    assert loaded.tab == "test_tab"
    assert loaded.steps[0].value == "https://example.com"


def test_parallel_template_serialization(tmp_path: Path):
    t1 = TabTemplate(tab="t1", steps=[BaseStep(id="s1", action="navigate", value="https://site1.com")])
    t2 = TabTemplate(tab="t2", steps=[BaseStep(id="s2", action="navigate", value="https://site2.com")])
    p_template = ParallelTemplate(templates=[t1, t2], max_concurrency=2)

    d = p_template.to_dict()
    assert d["type"] == "ParallelTemplate"
    assert len(d["templates"]) == 2

    # Round trip
    restored = ParallelTemplate.from_dict(d)
    assert isinstance(restored, ParallelTemplate)
    assert len(restored.templates) == 2
    assert isinstance(restored.templates[0], TabTemplate)
    assert restored.templates[0].tab == "t1"

    # JSON File round trip
    json_path = tmp_path / "parallel.json"
    template_to_json(p_template, json_path)
    loaded = template_from_json(json_path)
    assert isinstance(loaded, ParallelTemplate)
    assert loaded.max_concurrency == 2


def test_parameterized_template_serialization(tmp_path: Path):
    base_t = TabTemplate(tab="search_{{keyword}}", steps=[BaseStep(id="s1", action="navigate", value="https://example.com/search?q={{keyword}}")])
    param_tmpl = ParameterizedTemplate(template=base_t, parameter_key="keyword", values=["python", "javascript"], max_concurrency=2)

    d = param_tmpl.to_dict()
    assert d["type"] == "ParameterizedTemplate"
    assert d["parameter_key"] == "keyword"
    assert d["values"] == ["python", "javascript"]

    restored = ParameterizedTemplate.from_dict(d)
    assert isinstance(restored, ParameterizedTemplate)
    assert restored.template.tab == "search_{{keyword}}"
    assert restored.values == ["python", "javascript"]


def test_auto_detect_template_types():
    tab_dict = {"tab": "auto_tab", "steps": [{"id": "s1", "action": "navigate", "value": "https://example.com"}]}
    parallel_dict = {"templates": [tab_dict], "max_concurrency": 2}
    param_dict = {"template": tab_dict, "parameter_key": "k", "values": ["a", "b"]}

    res_tab = parse_template_from_dict(tab_dict)
    assert isinstance(res_tab, TabTemplate)

    res_parallel = parse_template_from_dict(parallel_dict)
    assert isinstance(res_parallel, ParallelTemplate)

    res_param = parse_template_from_dict(param_dict)
    assert isinstance(res_param, ParameterizedTemplate)


@pytest.mark.asyncio
async def test_run_scraper_with_json_file(tmp_path: Path):
    html_path = tmp_path / "test.html"
    html_path.write_text("<html><body><h1 id='title'>Hello StepWright JSON</h1></body></html>", encoding="utf-8")

    template_dict = {
        "tab": "local_test",
        "steps": [
            {"id": "n1", "action": "navigate", "value": f"file://{html_path}"},
            {"id": "d1", "action": "data", "object_type": "id", "object": "title", "key": "title", "data_type": "text"},
        ]
    }

    json_file = tmp_path / "test_template.json"
    json_file.write_text(json.dumps(template_dict), encoding="utf-8")

    # Pass JSON file path directly to run_scraper
    results = await run_scraper(str(json_file))
    assert len(results) == 1
    assert results[0]["title"] == "Hello StepWright JSON"
