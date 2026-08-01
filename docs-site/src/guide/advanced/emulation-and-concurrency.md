# Emulation, Multi-Engine & Concurrency Controls

StepWright supports multi-browser engine switching (`chromium`, `firefox`, `webkit`), mobile device emulation presets, custom environment contexts, and concurrency rate-limiting.

---

## 🌐 1. Multi-Engine Selection (`engine`)

You can specify which browser engine to launch directly in `RunOptions` or per `TabTemplate`:

```python
from stepwright import run_scraper, TabTemplate, BaseStep, RunOptions

template = TabTemplate(
    tab="firefox_flow",
    engine="firefox",  # Choose "chromium", "firefox", or "webkit"
    steps=[
        BaseStep(id="nav", action="navigate", value="https://example.com"),
        BaseStep(id="title", action="getTitle", key="title"),
    ]
)

# Or set global engine in RunOptions
options = RunOptions(engine="webkit")
results = await run_scraper([template], options)
```

---

## 📱 2. Device Emulation (`device`)

StepWright integrates with Playwright device emulation presets (e.g., `"iPhone 13"`, `"Pixel 5"`, `"iPad Pro 11"`). Setting a device automatically configures the appropriate viewport, user agent, mobile flags, and touch support.

```python
template = TabTemplate(
    tab="mobile_search",
    device="iPhone 13",  # Emulates iPhone 13 viewport & touch events
    steps=[
        BaseStep(id="nav", action="navigate", value="https://example.com"),
        BaseStep(id="data", action="data", object=".mobile-menu", key="menu"),
    ]
)
```

### Custom Environment Overrides
You can also manually set environment context options in `RunOptions` or `TabTemplate`:

```python
options = RunOptions(
    user_agent="CustomBot/2.0 (+https://example.com/bot)",
    viewport={"width": 390, "height": 844},
    locale="en-US",
    timezone_id="America/New_York",
    geolocation={"latitude": 37.7749, "longitude": -122.4194},
    permissions=["geolocation"],
    is_mobile=True,
    has_touch=True,
)
```

---

## 🚦 3. Concurrency Throttling & Rate Limiting

When running concurrent workflows with `ParallelTemplate` or `ParameterizedTemplate`, control request spikes and prevent IP blocking using `max_concurrency` and `rate_limit_delay_ms`:

```python
from stepwright import ParameterizedTemplate

# Execute 20 search queries with max 3 concurrent tabs and a 500ms launch delay
task = ParameterizedTemplate(
    template=base_search_template,
    parameter_key="keyword",
    values=["tech", "science", "health", "finance", "design"],
    max_concurrency=3,        # Max concurrent Playwright pages
    rate_limit_delay_ms=500,  # Pause 500ms between tab launches
)

results = await run_scraper([task])
```
