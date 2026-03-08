# tests/test_parallel_flows.py
import json
import csv
import pathlib
import pytest

from src.parser import run_scraper
from src.step_types import (
    BaseStep,
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    RunOptions,
)


@pytest.mark.asyncio
async def test_parallel_templates():
    """Test running multiple templates concurrently"""
    html_path = pathlib.Path(__file__).parent / "parallel_demo.html"
    file_uri = f"file://{html_path.absolute()}"

    t1 = TabTemplate(
        tab="laptop-search",
        steps=[
            BaseStep(id="nav", action="navigate", value=f"{file_uri}?q=laptop"),
            BaseStep(
                id="items",
                action="foreach",
                object=".product",
                subSteps=[
                    BaseStep(id="name", action="data", object=".name", key="name"),
                    BaseStep(id="price", action="data", object=".price", key="price"),
                ],
            ),
        ],
    )

    t2 = TabTemplate(
        tab="phone-search",
        steps=[
            BaseStep(id="nav", action="navigate", value=f"{file_uri}?q=phone"),
            BaseStep(
                id="items",
                action="foreach",
                object=".product",
                subSteps=[
                    BaseStep(id="name", action="data", object=".name", key="name"),
                    BaseStep(id="price", action="data", object=".price", key="price"),
                ],
            ),
        ],
    )

    parallel = ParallelTemplate(templates=[t1, t2])

    # run_scraper accepts List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]]
    results = await run_scraper([parallel], RunOptions(browser={"headless": True}))

    # Results should contain data from both tabs
    assert len(results) >= 4
    names = [r.get("name") for r in results]
    assert "Gaming Laptop" in names
    assert "iPhone 15" in names
    print(f"\n✅ Parallel templates test passed with {len(results)} results")


@pytest.mark.asyncio
async def test_parameterized_template():
    """Test generating templates from a parameter list"""
    html_path = pathlib.Path(__file__).parent / "parallel_demo.html"
    file_uri = f"file://{html_path.absolute()}"

    base_t = TabTemplate(
        tab="search",
        steps=[
            # We use {{keyword}} as our parameter placeholder
            BaseStep(
                id="nav", action="navigate", value=f"{file_uri}?q={{{{keyword}}}}"
            ),
            BaseStep(
                id="items",
                action="foreach",
                object=".product",
                subSteps=[
                    BaseStep(id="name", action="data", object=".name", key="name"),
                ],
            ),
        ],
    )

    param_t = ParameterizedTemplate(
        template=base_t, parameter_key="keyword", values=["tablet", "monitor"]
    )

    results = await run_scraper([param_t], RunOptions(browser={"headless": True}))

    names = [r.get("name") for r in results]
    assert "tablet Generic Item" in names
    assert "monitor Generic Item" in names
    print("✅ Parameterized template test passed")


@pytest.mark.asyncio
async def test_file_data_flows(tmp_path):
    """Test readData, writeData and external foreach source"""
    input_file = tmp_path / "keywords.json"
    output_file = tmp_path / "results.csv"

    # 1. Setup input file
    keywords = ["kiwi", "mango"]
    with open(input_file, "w") as f:
        json.dump(keywords, f)

    html_path = pathlib.Path(__file__).parent / "parallel_demo.html"
    file_uri = f"file://{html_path.absolute()}"

    # 2. Define template that reads file and loops over it
    t = TabTemplate(
        tab="flow-test",
        steps=[
            # Read keywords
            BaseStep(
                id="read",
                action="readData",
                value=str(input_file),
                data_type="json",
                key="keyword_list",
            ),
            # Loop over keywords
            BaseStep(
                id="loop",
                action="foreach",
                value="{{keyword_list}}",
                subSteps=[
                    BaseStep(
                        id="nav", action="navigate", value=f"{file_uri}?q={{{{item}}}}"
                    ),
                    BaseStep(
                        id="extract", action="data", object=".name", key="found_name"
                    ),
                ],
                key="extracted_items",
            ),
            # Write results
            BaseStep(
                id="write",
                action="writeData",
                value=str(output_file),
                data_type="csv",
                key="extracted_items",
            ),
        ],
    )

    await run_scraper([t], RunOptions(browser={"headless": True}))

    # 3. Verify output
    assert output_file.exists()
    with open(output_file, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["found_name"] == "kiwi Generic Item"
    print("✅ File data flows test passed")


@pytest.mark.asyncio
async def test_custom_callback():
    """Test custom action and custom format callback"""

    def my_custom_logic(page, collector, step):
        # Calculate something or modify collector
        return f"Hello from {step.id}"

    def my_custom_format_reader(path, step):
        # Simulate custom parsing
        return ["custom1", "custom2"]

    t = TabTemplate(
        tab="callback-test",
        steps=[
            # Custom action
            BaseStep(
                id="custom-act", action="custom", callback=my_custom_logic, key="msg"
            ),
            # Custom format (fake path)
            BaseStep(
                id="custom-read",
                action="readData",
                value="fake.bin",
                data_type="custom",
                callback=my_custom_format_reader,
                key="custom_items",
                continueOnEmpty=True,
            ),
        ],
    )

    results = await run_scraper([t], RunOptions(browser={"headless": True}))

    assert results[0]["msg"] == "Hello from custom-act"
    assert results[0]["custom_items"] == ["custom1", "custom2"]
    print("✅ Custom callback test passed")
