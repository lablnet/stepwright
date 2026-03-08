import pathlib
import pytest
from stepwright import run_scraper
from stepwright.step_types import TabTemplate, BaseStep, RunOptions


@pytest.mark.asyncio
async def test_nested_loops():
    html_path = pathlib.Path(__file__).parent / "nested.html"
    file_url = f"file://{html_path.absolute()}"

    template = TabTemplate(
        tab="nested-test",
        initSteps=[BaseStep(id="home", action="navigate", value=file_url)],
        perPageSteps=[
            BaseStep(
                id="loopCategories",
                index_key="i",
                action="foreach",
                object_type="xpath",
                object="//li[@class='category']",
                subSteps=[
                    BaseStep(
                        id="catName",
                        action="data",
                        object_type="xpath",
                        object="(//li[@class='category'])[{{i_plus1}}]//h2[@class='cat-name']",
                        key="category",
                        data_type="text",
                    ),
                    BaseStep(
                        id="loopItems",
                        index_key="j",
                        action="foreach",
                        key="products",
                        object_type="xpath",
                        object="(//li[@class='category'])[{{i_plus1}}]//li[@class='item']",
                        subSteps=[
                            BaseStep(
                                id="itemName",
                                action="data",
                                object_type="xpath",
                                object="((//li[@class='category'])[{{i_plus1}}]//li[@class='item'])[{{j_plus1}}]//span[@class='item-name']",
                                key="item_name",
                                data_type="text",
                            ),
                            BaseStep(
                                id="itemPrice",
                                action="data",
                                object_type="xpath",
                                object="((//li[@class='category'])[{{i_plus1}}]//li[@class='item'])[{{j_plus1}}]//span[@class='item-price']",
                                key="item_price",
                                data_type="text",
                            ),
                        ],
                    ),
                ],
            )
        ],
    )

    results = await run_scraper([template], RunOptions(browser={"headless": True}))

    # Analyze the results
    assert len(results) == 2

    # First Category (Electronics)
    assert results[0]["category"] == "Electronics"
    assert "products" in results[0]
    items_0 = results[0]["products"]
    assert len(items_0) == 2
    assert items_0[0]["item_name"] == "Laptop"
    assert items_0[0]["item_price"] == "$999"
    assert items_0[1]["item_name"] == "Smartphone"
    assert items_0[1]["item_price"] == "$499"

    # Second Category (Books)
    assert results[1]["category"] == "Books"
    assert "products" in results[1]
    items_1 = results[1]["products"]
    assert len(items_1) == 2
    assert items_1[0]["item_name"] == "Fiction"
    assert items_1[0]["item_price"] == "$19"
    assert items_1[1]["item_name"] == "Non-Fiction"
    assert items_1[1]["item_price"] == "$29"
