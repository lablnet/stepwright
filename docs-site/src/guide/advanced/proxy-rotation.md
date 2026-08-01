# Smart Proxy Rotation & Auto-Healing Proxy Pool

StepWright 2.0.0 features a **Smart Proxy Rotation & Auto-Healing Proxy Pool Engine** to prevent IP bans, handle HTTP rate-limiting (`429 Too Many Requests`, `403 Forbidden`), and automatically cool down failing proxies during large-scale scraping jobs.

---

## 🏗️ Core Features

- **Multi-Proxy Pool Initialization**: Accepts lists of proxy strings, dictionaries, or `ProxyConfig` instances.
- **Rotation Strategies**:
  - `round_robin` (Default): Distributes requests sequentially across all healthy proxies.
  - `random`: Selects a random healthy proxy per request/tab.
  - `sticky`: Assigns and keeps the same proxy for a given session/tab ID.
- **Auto-Healing & Cooldown**: Automatically cools down failing proxies for $N$ seconds after $M$ consecutive errors, automatically restoring them once healthy.

---

## 🚀 Basic Usage

```python
import asyncio
from stepwright import (
    ProxyPool,
    ProxyConfig,
    TabTemplate,
    BaseStep,
    RunOptions,
    run_scraper,
)

async def main():
    # 1. Create a ProxyPool instance
    proxy_pool = ProxyPool(
        proxies=[
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            ProxyConfig(
                server="http://proxy3.example.com:8080",
                username="user",
                password="pass",
            ),
        ],
        strategy="round_robin",
        max_failures=3,
        cooldown_seconds=300,  # 5 minutes
    )

    # 2. Attach proxy_pool to RunOptions or TabTemplate
    template = TabTemplate(
        tab="proxy_demo",
        proxy_pool=proxy_pool,
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(id="title", action="data", object="h1", key="heading"),
        ],
    )

    options = RunOptions(browser={"headless": True})
    results = await run_scraper([template], options)
    print(results)

    # 3. View pool health statistics
    print(proxy_pool.get_stats())
    # {'total': 3, 'healthy': 3, 'cooling': 0, 'banned': 0, 'strategy': 'round_robin'}

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📊 Health Tracking & Manual Reporting

You can manually report proxy failures or successes in custom step callbacks or error handlers:

```python
# Report proxy failure (cools down after max_failures threshold)
proxy_pool.report_failure("http://proxy1.example.com:8080", reason="HTTP 429")

# Report proxy success (resets failure count and sets status to healthy)
proxy_pool.report_success("http://proxy1.example.com:8080")
```
