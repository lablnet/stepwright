# Pluggable Browser Driver Architecture

StepWright 2.0.0 features a **Pluggable Browser Driver Architecture** matching the architecture of `stepwright-php`. 

By decoupling step execution logic from Playwright directly, StepWright allows you to plug in custom browser backends (e.g., Selenium, Undetected Chromium, Pyppeteer, or lightweight HTTP/Requests engines) while maintaining `PlaywrightDriver` as the ultra-fast default.

---

## 🏗️ Architecture Overview

All browser interactions in StepWright are routed through the `BaseDriver` contract:

```
StepWright Engine (Templates, Steps, Handlers)
                      │
                      ▼
            BaseDriver Contract
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
PlaywrightDriver  SeleniumDriver  Custom Driver
```

---

## 🛠️ The `BaseDriver` Contract

To implement a custom browser driver, create a class that inherits from `BaseDriver`:

```python
from typing import Any, Dict, Optional
from stepwright import BaseDriver

class MyCustomDriver(BaseDriver):
    async def launch(self, options: Optional[Dict[str, Any]] = None) -> Any:
        # Launch custom browser process
        pass

    async def goto(self, page: Any, url: str, wait_until: str = "networkidle", timeout: Optional[int] = None) -> None:
        # Custom navigation logic
        pass

    async def click(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        # Custom click implementation
        pass

    async def fill(self, locator: Any, value: str, options: Optional[Dict[str, Any]] = None) -> None:
        # Custom input fill logic
        pass

    # Implement additional BaseDriver abstract methods...
```

---

## 🚀 Using Custom Drivers

You can pass custom driver instances directly via `RunOptions` or per `TabTemplate`:

### Global Driver in `RunOptions`

```python
import asyncio
from stepwright import run_scraper, TabTemplate, BaseStep, RunOptions
from my_custom_driver import MyCustomDriver

async def main():
    template = TabTemplate(
        tab="custom_demo",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(id="title", action="data", object="h1", key="heading"),
        ],
    )

    # Pass custom driver instance
    options = RunOptions(
        driver=MyCustomDriver(),
        browser={"headless": True},
    )

    results = await run_scraper([template], options)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

### Per-Template Driver Override

```python
template = TabTemplate(
    tab="selenium_tab",
    driver=SeleniumDriver(),  # Custom driver for this tab
    steps=[
        BaseStep(id="s1", action="navigate", value="https://example.com"),
    ],
)
```

---

## 🧪 Extending `PlaywrightDriver`

Instead of building a driver from scratch, you can subclass `PlaywrightDriver` to add custom hooks, metrics, or request logging:

```python
from typing import Any, Dict, Optional
from stepwright import PlaywrightDriver

class LoggingDriver(PlaywrightDriver):
    async def goto(self, page: Any, url: str, wait_until: str = "networkidle", timeout: Optional[int] = None) -> None:
        print(f"📡 [LoggingDriver] Navigating to {url}")
        await super().goto(page, url, wait_until=wait_until, timeout=timeout)

    async def click(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        print("🖱️ [LoggingDriver] Click intercepted")
        await super().click(locator, options=options)
```
