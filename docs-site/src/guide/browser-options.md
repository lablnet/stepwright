# Browser Options

StepWright allows you to configure the underlying Playwright browser via the `RunOptions` dataclass. You pass this object as the second argument to `run_scraper`.

## Headless Mode

By default, StepWright runs Headless (the browser exists only in memory). If you are building or debugging a scraper, you often want to see what is happening.

```python
from stepwright import run_scraper, RunOptions

results = await run_scraper(templates, RunOptions(
    browser={"headless": False}
))
```

## Slow Motion
When debugging in Headful mode, the browser often moves too fast to see which element is being interacted with. You can artificially slow down every action using `slow_mo` (in milliseconds).

```python
results = await run_scraper(templates, RunOptions(
    browser={
        "headless": False, 
        "slow_mo": 500  # 500ms delay between EVERY action
    }
))
```

## Proxies
To route your traffic through a residential or datacenter proxy, supply the network configuration.

```python
results = await run_scraper(templates, RunOptions(
    browser={
        "proxy": {
            "server": "http://my-proxy:8080",
            "username": "usr",
            "password": "pwd"
        }
    }
))
```

## Engine Selection
StepWright supports `chromium`, `firefox`, and `webkit` browser engines.

```python
results = await run_scraper(templates, RunOptions(
    engine="firefox"
))
```

## Device Emulation
Emulate mobile devices (e.g. `"iPhone 13"`, `"Pixel 5"`) and custom environment settings (User-Agent, Viewport, Locale, Geolocation):

```python
results = await run_scraper(templates, RunOptions(
    device="iPhone 13",
    locale="en-US",
    timezone_id="America/New_York"
))
```

## Concurrency & Rate Limiting
Control maximum concurrent tab execution and delay launches:

```python
results = await run_scraper(templates, RunOptions(
    max_concurrency=4,
    rate_limit_delay_ms=250
))
```

## Stealth & Anti-Bot Evasion Mode
Enable automated fingerprint evasion scripts (`stealth=True`) to mask `navigator.webdriver`, `window.chrome`, and WebGL flags:

```python
results = await run_scraper(templates, RunOptions(
    stealth=True
))
```


