import asyncio
import pathlib
from stepwright import run_scraper
from stepwright.step_types import TabTemplate, BaseStep, RunOptions


async def main():
    html_path = pathlib.Path(__file__).parent.parent / "tests" / "nested.html"
    file_url = f"file://{html_path.absolute()}"

    template = TabTemplate(
        tab="nested-example",
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

    print(f"Running scraper on {file_url}...")
    results = await run_scraper([template], RunOptions(browser={"headless": True}))

    import json

    print("Scraping completed. Results:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
