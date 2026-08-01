# Network & API Request Interception

StepWright allows you to intercept background XHR/Fetch REST API responses, block unwanted heavy media resource types, and inject custom HTTP request headers.

---

## 📡 1. `intercept` Action

Modern single-page applications (SPAs) load dynamic data via JSON REST or GraphQL APIs. Instead of scraping DOM elements, you can capture response payloads directly:

```python
from stepwright import TabTemplate, BaseStep, run_scraper

template = TabTemplate(
    tab="intercept_api_demo",
    steps=[
        # Setup intercept listener matching URL glob pattern
        BaseStep(
            id="capture_products",
            action="intercept",
            object="**/api/v1/products*",  # URL pattern / glob / regex
            data_type="json",              # "json", "text", or "bytes"
            key="products_json",
        ),
        # Navigate to page triggering background API calls
        BaseStep(
            id="nav",
            action="navigate",
            value="https://example.com/store",
        ),
    ]
)

results = await run_scraper([template])
print(results[0]["products_json"])  # Contains full parsed JSON API payload
```

---

## 🛡️ 2. Resource Blocking (`block_resources`)

Speed up scraping workflows by blocking heavy network assets (`image`, `stylesheet`, `font`, `media`, `script`) per template or globally in `RunOptions`:

```python
template = TabTemplate(
    tab="fast_text_scraper",
    block_resources=["image", "stylesheet", "font", "media"],
    steps=[
        BaseStep(id="nav", action="navigate", value="https://example.com"),
        BaseStep(id="text", action="data", object="body", key="content"),
    ]
)
```

---

## 🔑 3. Custom HTTP Headers (`extra_http_headers`)

Inject custom request headers (Authorization tokens, Referer headers, Accept-Language, API keys) into all outgoing HTTP requests:

```python
template = TabTemplate(
    tab="custom_headers_demo",
    extra_http_headers={
        "Authorization": "Bearer my_secret_token",
        "X-Custom-Client": "StepWright/1.4.0",
        "Accept-Language": "en-US,en;q=0.9",
    },
    steps=[
        BaseStep(id="nav", action="navigate", value="https://api.example.com/dashboard"),
    ]
)
```
