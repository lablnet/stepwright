# examples/network_interception.py
# Example demonstrating Network & API Request Interception, Resource Blocking, and Custom Headers

import asyncio
from stepwright import (
    run_scraper,
    TabTemplate,
    BaseStep,
    RunOptions,
    validate_template_format,
)


async def main():
    # 1. Define workflow with API request interception and resource blocking
    template = TabTemplate(
        tab="api_interception_demo",
        # Speed optimization: block images, stylesheets, and fonts
        block_resources=["image", "stylesheet", "font"],
        # Add custom headers to all outgoing request headers
        extra_http_headers={
            "X-Scraper-Client": "StepWright/1.4.0",
            "Accept-Language": "en-US,en;q=0.9",
        },
        steps=[
            # Intercept background API response during page navigation
            BaseStep(
                id="listen_api",
                action="intercept",
                object="**/hn.algolia.com/api/v1/search*",  # URL pattern / glob
                data_type="json",
                key="api_response",
            ),
            BaseStep(
                id="nav",
                action="navigate",
                value="https://hn.algolia.com",
            ),
        ],
    )

    # Validate template format before running
    res = validate_template_format(template)
    print(f"✅ Format Valid: {res.is_valid}")

    options = RunOptions(
        browser={"headless": True},
        collect_metrics=True,
    )

    print("🚀 Launching scraper with API Interception & Resource Blocking...")
    results = await run_scraper([template], options)
    print(f"📊 Execution results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
