# examples/custom_driver_demo.py
# Example demonstrating custom driver implementation extending BaseDriver

import asyncio
from typing import Any, Dict, Optional
from stepwright import (
    BaseDriver,
    PlaywrightDriver,
    run_scraper,
    TabTemplate,
    BaseStep,
    RunOptions,
)


class LoggingCustomDriver(PlaywrightDriver):
    """
    Example custom driver extending PlaywrightDriver with custom logging & metrics hooks.
    """

    async def goto(
        self, page: Any, url: str, wait_until: str = "networkidle", timeout: Optional[int] = None
    ) -> None:
        print(f"  🏎️  [CustomDriver] Navigating page to: {url}")
        await super().goto(page, url, wait_until=wait_until, timeout=timeout)

    async def click(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        print("  🖱️  [CustomDriver] Intercepted click action")
        await super().click(locator, options=options)

    async def fill(self, locator: Any, value: str, options: Optional[Dict[str, Any]] = None) -> None:
        print(f"  ⌨️  [CustomDriver] Intercepted fill action with value: '{value}'")
        await super().fill(locator, value, options=options)


async def main():
    # Instantiate custom driver
    custom_driver = LoggingCustomDriver()

    template = TabTemplate(
        tab="custom_driver_demo",
        steps=[
            BaseStep(
                id="nav",
                action="navigate",
                value="https://example.com",
            ),
            BaseStep(
                id="extract_title",
                action="data",
                object="h1",
                key="title",
            ),
        ],
    )

    # Pass custom driver instance into RunOptions
    options = RunOptions(
        driver=custom_driver,
        browser={"headless": True},
    )

    print("🚀 Running scraper with custom driver instance...")
    results = await run_scraper([template], options)
    print(f"📊 Results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
