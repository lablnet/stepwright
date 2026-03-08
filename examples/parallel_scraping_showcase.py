# examples/parallel_scraping_showcase.py
"""
StepWright Parallel Scraping Showcase
------------------------------------
This example demonstrates how to use ParallelTemplate and ParameterizedTemplate
to run multiple scraping tasks concurrently, significantly increasing speed.
"""

import asyncio
import pathlib
from stepwright import (
    run_scraper,
    TabTemplate,
    BaseStep,
    ParallelTemplate,
    ParameterizedTemplate,
    RunOptions,
)


async def main():
    # 1. Setup local test page path
    html_path = pathlib.Path(__file__).parent.parent / "tests" / "parallel_demo.html"
    if not html_path.exists():
        print("⚠️  Note: This example works best with the 'parallel_demo.html' fixture.")
        file_uri = "https://example.com"  # Fallback
    else:
        file_uri = f"file://{html_path.absolute()}"

    print("🚀 Starting StepWright Parallel Showcase...")

    # --- SCENARIO 1: ParallelTemplate ---
    # Running two different workflows at the same time

    t1 = TabTemplate(
        tab="search-electronics",
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
        tab="search-books",
        steps=[
            BaseStep(id="nav", action="navigate", value=f"{file_uri}?q=books"),
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

    # Combine them into a ParallelTemplate
    parallel_batch = ParallelTemplate(templates=[t1, t2])

    print("\n📦 Running ParallelTemplate (Two different tabs at once)...")
    results_p = await run_scraper(
        [parallel_batch], RunOptions(browser={"headless": True})
    )
    print(f"✅ ParallelTemplate finished. Results collected: {len(results_p)}")

    # --- SCENARIO 2: ParameterizedTemplate ---
    # Running the SAME workflow for multiple values (e.g. keywords) concurrently

    search_base = TabTemplate(
        tab="search_{{keyword}}",
        steps=[
            # {{keyword}} will be replaced by the values provided below
            BaseStep(
                id="nav", action="navigate", value=f"{file_uri}?q={{{{keyword}}}}"
            ),
            BaseStep(
                id="extract",
                action="foreach",
                object=".product",
                subSteps=[
                    BaseStep(id="item_name", action="data", object=".name", key="name"),
                ],
            ),
        ],
    )

    parameterized_batch = ParameterizedTemplate(
        template=search_base,
        parameter_key="keyword",
        values=["phone", "tablet", "monitor", "camera"],
    )

    print("\n📦 Running ParameterizedTemplate (4 keywords concurrently)...")
    results_param = await run_scraper(
        [parameterized_batch], RunOptions(browser={"headless": True})
    )
    print(f"✅ ParameterizedTemplate finished. Results collected: {len(results_param)}")

    # Summary
    print("\n" + "=" * 40)
    print(f"✨ Total Parallel Results: {len(results_p)}")
    print(f"✨ Total Parameterized Results: {len(results_param)}")
    print("=" * 40)


if __name__ == "__main__":
    asyncio.run(main())
