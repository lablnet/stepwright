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

## Disabling Media (Speed Optimization)
If you don't need to see images or load heavy media, you can significantly speed up your scraping and save bandwidth by blocking them. Note that this requires access to the Playwright `page` directly, which you can do using a [Custom Action Callback](/guide/advanced/data-flows#custom-callbacks-advanced).

```python
# A custom hook to block media on the page
def block_media(page, collector, step):
    async def route_handler(route):
        if route.request.resource_type in ["image", "media", "font"]:
            await route.abort()
        else:
            await route.continue_()
            
    # Note: Requires an async wrapper or using Playwright's sync API
    page.route("**/*", route_handler)
    return "Optimizations applied"
```
