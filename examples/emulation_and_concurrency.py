# examples/emulation_and_concurrency.py
# Example demonstrating Device Emulation, Multi-Engine, and Concurrency Throttling with StepWright

import asyncio
from stepwright import (
    run_scraper,
    TabTemplate,
    ParameterizedTemplate,
    BaseStep,
    RunOptions,
    validate_template_format,
)


async def main():
    # 1. Define a search workflow template with mobile device emulation
    search_tmpl = TabTemplate(
        tab="mobile_search_{{keyword}}",
        device="iPhone 13",  # Emulate iPhone 13 viewport & touch events
        steps=[
            BaseStep(
                id="nav",
                action="navigate",
                value="https://news.ycombinator.com",
            ),
            BaseStep(
                id="title",
                action="getTitle",
                key="page_title",
            ),
        ],
    )

    # Validate template format before launching
    val_res = validate_template_format(search_tmpl)
    print(f"✅ Template valid: {val_res.is_valid}")

    # 2. Wrap in ParameterizedTemplate with concurrency throttling
    parameterized_flow = ParameterizedTemplate(
        template=search_tmpl,
        parameter_key="keyword",
        values=["python", "playwright", "ai", "data"],
        max_concurrency=2,  # Limit max concurrent tabs to 2
        rate_limit_delay_ms=500,  # 500ms delay between tab launches
    )

    # 3. Configure RunOptions with Firefox engine & custom geolocation
    options = RunOptions(
        engine="chromium",
        locale="en-US",
        timezone_id="America/New_York",
        collect_metrics=True,
    )

    print("🚀 Launching scraper with device emulation and max_concurrency=2...")
    results = await run_scraper([parameterized_flow], options)
    print(f"📊 Collected {len(results)} total results:")
    for r in results:
        print(f" - {r}")


if __name__ == "__main__":
    asyncio.run(main())
