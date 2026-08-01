# What's New in StepWright

## 🚀 Version 2.0.0 - The Next-Generation Scraping Engine

StepWright 2.0.0 is a milestone major release that elevates StepWright into an enterprise-grade, anti-bot resilient, multi-engine web scraping & automation platform.

---

### 🏎️ 1. Pluggable Browser Driver Architecture
- **`BaseDriver` Contract**: Abstract Base Class defining standard browser driver contracts (`launch`, `goto`, `click`, `fill`, `type`, `evaluate`, `screenshot`, `text_content`, `inner_html`, etc.).
- **`PlaywrightDriver` Default**: Concrete implementation wrapping Playwright with automatic event loop lifecycle management and thread-safe recycling.
- **Custom Driver Registration**: Pass custom drivers via `RunOptions(driver=MyCustomDriver())` or `TabTemplate(driver=MyCustomDriver())`.

---

### 🗄️ 2. Enterprise Storage Adapter Architecture
- **`BaseStorageAdapter` Contract**: Abstract Base Class defining standard storage contracts (`connect`, `write`, `close`).
- **14 Built-in Adapters**: Relational DBs (`SQLiteAdapter`, `PostgreSQLAdapter`, `MySQLAdapter`), NoSQL DBs (`MongoDBAdapter`, `DynamoDBAdapter`), Search (`ElasticsearchAdapter`), Cloud Storage (`S3StorageAdapter`, `GCSStorageAdapter`, `AzureBlobAdapter`), Queues (`RabbitMQAdapter`, `KafkaAdapter`), and Files (`JSONFileAdapter`, `CSVFileAdapter`, `XMLFileAdapter`).
- **Custom Adapter Registration**: Register custom storage adapters via `register_adapter("name", CustomAdapter)`.

---

### 🥷 3. Stealth Mode, Proxies & Smart Rotation
- **Smart Proxy Rotation Pool (`ProxyPool`)**: Multi-proxy pool manager supporting `round_robin`, `random`, and `sticky` rotation strategies.
- **Auto-Healing & Cooldown**: Automatically tracks proxy failure counts and cools down banned/failing proxies (`COOLING`) for $N$ seconds, restoring them once healthy.
- **Automated Stealth Fingerprint Evasion (`stealth=True`)**: Automatically injects init scripts (`add_init_script`) to mask `navigator.webdriver`, `navigator.languages`, `navigator.plugins`, `window.chrome`, `Permissions` API, and WebGL UNMASKED_VENDOR/RENDERER flags.
- **Proxy Configuration (`proxy` & `ProxyConfig`)**: Pass HTTP, HTTPS, or SOCKS5 proxies with optional authentication credentials per `TabTemplate` or globally in `RunOptions`.
- **CAPTCHA & Challenge Detection Hooks (`on_captcha`)**: Detect Cloudflare challenge frames or CAPTCHA elements (`captcha_selector`) during step execution and invoke custom resolution callback handlers (`on_captcha`).

---

### ⌨️ 4. Additional Step Actions & Page Controls
- **6 New Declarative Actions**: `press`, `type`, `dialog`, `mouseMove`, `waitForNavigation`, `setHeaders`.
- **Keyboard Key Presses (`press`)**: Send keyboard key press events (`"Enter"`, `"Control+A"`, `"Backspace"`) to targeted DOM elements or page keyboard.
- **Typing with Delay (`type` / `clickAndType`)**: Focus elements, clear inputs (`clearBeforeInput=True`), and type text with human-like key delays (`inputDelay`).
- **Dialog Auto-Handling (`dialog`)**: Automatically accept or dismiss browser alert, confirm, or prompt popups during step execution (`value="accept"` or `value="dismiss"`).
- **Mouse Movements (`mouseMove`)**: Smoothly move mouse cursor to target DOM elements (`object`) or coordinate pairs (`value="350,450"`).
- **Navigation State Waits & Headers (`waitForNavigation`, `setHeaders`)**: Explicitly wait for page load states (`"networkidle"`, `"domcontentloaded"`) and dynamically inject extra HTTP request headers.

---

### 📡 5. Network & API Request Interception
- **`intercept` Step Action**: Capture background JSON/XHR/Fetch REST API responses matching URL patterns/globs directly into collector memory without DOM parsing.
- **Resource Blocking (`block_resources`)**: Abort heavy asset types (`image`, `stylesheet`, `font`, `media`, `script`) per template or globally in `RunOptions` for ultra-fast text/API extraction.
- **Custom HTTP Headers (`extra_http_headers`)**: Set custom request headers (e.g. Authorization tokens, Referer, Accept-Language) per template or globally.

---

### 🌐 6. Multi-Engine, Device Emulation & Concurrency Controls
- **Multi-Engine Browser Selection**: Switch between `chromium`, `firefox`, and `webkit` browser engines dynamically via `RunOptions(engine="firefox")` or per `TabTemplate`.
- **Mobile Device Emulation**: Emulate mobile devices using Playwright's device catalog presets (`device="iPhone 13"`, `device="Pixel 5"`). Supports custom Viewports, User-Agent strings, Locales, Timezones, Geolocation, and Permissions.
- **Concurrency Rate Limiting**: Prevent server overload and IP blocks using `max_concurrency` semaphore limits and `rate_limit_delay_ms` launch delays across `ParallelTemplate` and `ParameterizedTemplate` workflows.

---

### 🔍 7. Developer Experience, Static Validation & Metrics
- **Static Template Format Validation (`validate_template_format`)**: Statically checks step configuration, action types, selector types, and mandatory parameter fields without launching Playwright.
- **Expected Data Flow Validation (`validate_template_data`)**: Verifies that the template data flow extracts all required collector output keys.
- **Debug Diagnostic Trace (`debug_on_failure=True`)**: Prints detailed step diagnostics (step ID, action, selector, value, current URL, error trace) whenever a step fails.
- **Execution Metrics Tracking (`run_scraper_with_metrics`)**: Returns an `ExecutionMetrics` object detailing total execution duration, step execution counts, failure counts, and per-step timing metrics (`StepMetric`).

---

## 🚀 Version 1.1.0 - The Concurrency & Data Flow Update

StepWright 1.1.0 is a massive update that evolves the library from a sequential task runner into a high-performance concurrent scraping engine. This release introduces parallel execution, parameterized templates, and advanced data flow capabilities, allowing you to treat web scraping like a standard data engineering pipeline.

---

### ⚡ Parallel & Concurrent Execution
Run multiple independent scraping workflows simultaneously across different browser pages (tabs) within the exact same browser context.

- **`ParallelTemplate`**: Group multiple disparate `TabTemplate` objects into a single execution context. StepWright will use `asyncio.gather` to execute them all at once.
- **`ParameterizedTemplate`**: The ultimate scaling tool. Provide a single base `TabTemplate` filled with `{{placeholder}}` syntax. Pass a list of values (e.g., 50 stock ticker symbols), and StepWright will instantly clone the template 50 times, inject the specific ticker into each clone, and run all 50 extractions concurrently.

```python
# Search for exactly 4 items at the SAME time!
task = ParameterizedTemplate(
    template=search_tmpl,      # Contains {{term}} in navigate/input steps
    parameter_key="term",
    values=["SSD", "RAM", "GPU", "CPU"]
)
results = await run_scraper([task])
print(f"Collected total: {len(results)} items")
```

---

### 📂 Advanced Data Flows (Pipeline I/O)
Integrate external datasets directly into your scraping sequence using built-in file handlers, eliminating the need to write custom Python file-parsing wrappers.

- **`readData` Action**: Import seeds or targets from **JSON, CSV, Excel (`.xlsx`), or Plain Text** files into the internal collector memory.
- **Enhanced `foreach` Loops**: The `foreach` loop can now iterate over string lists loaded into memory via `readData`, executing a sub-workflow for every item in the file (like searching every keyword from a CSV).
- **`writeData` Action**: Programmatically dump the contents of the collector back out to the filesystem in JSON, CSV, or Text format as a formal step in the workflow.

```python
# Load a CSV into the collector under the key 'keywords'
BaseStep(id="load", action="readData", value="keywords.csv", data_type="csv", key="keywords")

# Iterate over that data directly inside the browser interaction flow!
BaseStep(
    id="loop",
    action="foreach",
    value="{{keywords}}", 
    subSteps=[ ... ]
)
```

---

### 🛠️ Custom Callbacks & Closure Hooks
Complete flexibility for advanced edge cases. StepWright no longer traps you in the configuration dictionary.

- **Custom Actions**: Execute arbitrary Python functions as a `BaseStep`. The callback is invoked with the Playwright `page`, the `collector`, and the `step` object itself, allowing you to execute raw Playwright commands or complex network interceptors.
- **Custom Formats**: Don't use CSV or JSON? Read from an XML file by passing `data_type="custom"` and providing a Python callback that parses the file and returns a list of targets to the engine.

```python
def xml_reader(filepath, step_config):
    import xml.etree.ElementTree as ET
    return [el.text for el in ET.parse(filepath).findall('.//item')]

BaseStep(id="load-xml", action="readData", value="data.xml", data_type="custom", callback=xml_reader, key="items")
```

---

## What's New in StepWright 1.0.0

## 🚀 New Features

### 🔁 Retry Logic
Automatically retry failed steps with configurable delays to handle flaky networks and dynamic content.

```python
BaseStep(
    id="click_button",
    action="click",
    object_type="id",
    object="flaky-button",
    retry=3,              # Retry up to 3 times
    retryDelay=1000        # Wait 1 second between retries
)
```

**Benefits:**
- Handle transient failures automatically
- Reduce manual intervention for flaky operations
- Configurable retry count and delay

---

### 🎛️ Conditional Execution
Execute or skip steps based on JavaScript conditions for dynamic workflow control.

```python
# Skip step if condition is true
BaseStep(
    id="optional_click",
    action="click",
    skipIf="document.querySelector('.modal').classList.contains('hidden')"
)

# Execute only if condition is true
BaseStep(
    id="conditional_data",
    action="data",
    onlyIf="document.querySelector('#dynamic-content') !== null"
)
```

**Benefits:**
- Dynamic workflow adaptation
- Handle different page states gracefully
- Reduce unnecessary operations

---

### ⏳ Smart Waiting
Wait for specific selectors to appear or change state before performing actions.

```python
BaseStep(
    id="click_after_load",
    action="click",
    object_type="id",
    object="target-button",
    waitForSelector="#loading-indicator",
    waitForSelectorTimeout=5000,
    waitForSelectorState="hidden"  # Wait until hidden
)
```

**Benefits:**
- Handle dynamic content loading
- Prevent race conditions
- More reliable element interactions

---

### 🔀 Fallback Selectors
Provide multiple selector options for increased robustness when dealing with variable page structures.

```python
BaseStep(
    id="click_with_fallback",
    action="click",
    object_type="id",
    object="primary-button",
    fallbackSelectors=[
        {"object_type": "class", "object": "btn-primary"},
        {"object_type": "xpath", "object": "//button[contains(text(), 'Submit')]"}
    ]
)
```

**Benefits:**
- Handle page structure variations
- Increase scraping success rate
- Support multiple page layouts

---

### 🖱️ Enhanced Click Interactions
Support for double-click, right-click, modifier keys, and force clicks.

```python
# Double click
BaseStep(id="double_click", action="click", doubleClick=True)

# Right click (context menu)
BaseStep(id="right_click", action="click", rightClick=True)

# Modifier keys (Ctrl/Cmd+Click)
BaseStep(id="multi_select", action="click", clickModifiers=["Control"])

# Force click hidden elements
BaseStep(id="force_click", action="click", forceClick=True)
```

**Benefits:**
- Handle complex UI interactions
- Support multi-select scenarios
- Click elements that aren't immediately visible

---

### ⌨️ Input Enhancements
More control over input behavior with clearing and human-like typing delays.

```python
# Clear before input (default: True)
BaseStep(
    id="clear_and_input",
    action="input",
    clearBeforeInput=True
)

# Human-like typing with delays
BaseStep(
    id="human_like_input",
    action="input",
    inputDelay=100  # 100ms delay between each character
)
```

**Benefits:**
- Better form interaction
- Mimic human behavior
- Handle pre-filled fields correctly

---

### 🔍 Advanced Data Extraction
Regex extraction, JavaScript transformations, required fields, and default values.

```python
# Extract with regex
BaseStep(
    id="extract_price",
    action="data",
    regex=r"\$(\d+\.\d+)",
    regexGroup=1
)

# Transform with JavaScript
BaseStep(
    id="transform_data",
    action="data",
    transform="value.toUpperCase().trim()"
)

# Required field with default
BaseStep(
    id="get_required_data",
    action="data",
    required=True,
    defaultValue="N/A"
)
```

**Benefits:**
- Extract structured data from unstructured text
- Transform data on-the-fly
- Handle missing data gracefully

---

### ✅ Element State Validation
Ensure elements are visible and enabled before performing actions.

```python
BaseStep(
    id="click_visible",
    action="click",
    requireVisible=True,
    requireEnabled=True
)
```

**Benefits:**
- Prevent errors from invalid interactions
- Ensure elements are ready before actions
- More reliable scraping

---

### 🤖 Human-like Behavior
Add random delays to mimic human interaction patterns.

```python
BaseStep(
    id="human_like_action",
    action="click",
    randomDelay={"min": 500, "max": 2000}
)
```

**Benefits:**
- Reduce detection by anti-bot systems
- More natural browsing patterns
- Better for testing user interactions

---

### 🌐 New Page Actions
Comprehensive set of page manipulation and information retrieval actions.

#### Reload Page
```python
BaseStep(id="reload", action="reload", waitUntil="networkidle")
```

#### Get Current URL
```python
BaseStep(id="get_url", action="getUrl", key="current_url")
```

#### Get Page Title
```python
BaseStep(id="get_title", action="getTitle", key="page_title")
```

#### Meta Tags Management
```python
# Get specific meta tag
BaseStep(id="get_description", action="getMeta", object="description", key="meta")

# Get all meta tags
BaseStep(id="get_all_meta", action="getMeta", key="all_meta")
```

#### Cookies Management
```python
# Get all cookies
BaseStep(id="get_cookies", action="getCookies", key="cookies")

# Get specific cookie
BaseStep(id="get_session", action="getCookies", object="session_id", key="session")

# Set cookie
BaseStep(id="set_cookie", action="setCookies", object="preference", value="dark_mode")
```

#### LocalStorage & SessionStorage
```python
# Get/Set localStorage
BaseStep(id="get_storage", action="getLocalStorage", object="key", key="value")
BaseStep(id="set_storage", action="setLocalStorage", object="key", value="value")

# Get/Set sessionStorage
BaseStep(id="get_session", action="getSessionStorage", object="key", key="value")
BaseStep(id="set_session", action="setSessionStorage", object="key", value="value")
```

#### Viewport Operations
```python
# Get viewport size
BaseStep(id="get_viewport", action="getViewportSize", key="viewport")

# Set viewport size
BaseStep(id="set_viewport", action="setViewportSize", value="1920x1080")
```

#### Enhanced Screenshot
```python
# Full page screenshot
BaseStep(id="screenshot", action="screenshot", value="./page.png", data_type="full")

# Element screenshot
BaseStep(id="element_screenshot", action="screenshot", object_type="id", object="content")
```

#### Wait for Selector (Explicit Action)
```python
BaseStep(
    id="wait_for_element",
    action="waitForSelector",
    object_type="id",
    object="dynamic-content",
    value="visible",
    wait=5000
)
```

#### Evaluate JavaScript
```python
BaseStep(
    id="custom_js",
    action="evaluate",
    value="() => document.querySelector('.counter').textContent",
    key="counter_value"
)
```

**Benefits:**
- Complete page manipulation capabilities
- Extract comprehensive page information
- Support advanced testing scenarios

---

### 🛡️ Enhanced Error Handling
New options for graceful error handling and continuation.

```python
# Skip step if error occurs
BaseStep(
    id="optional_step",
    action="click",
    skipOnError=True
)

# Continue even if element not found
BaseStep(
    id="optional_data",
    action="data",
    continueOnEmpty=True
)
```

**Benefits:**
- More resilient scraping workflows
- Handle optional elements gracefully
- Reduce workflow failures

---

## 📦 Code Organization Improvements

### Modular Handler Architecture
Action handlers have been reorganized into a dedicated `handlers/` subfolder for better maintainability:

- `data_handlers.py` - Data extraction logic with transformations
- `file_handlers.py` - File download and PDF operations
- `loop_handlers.py` - Foreach loops and new tab/window handling
- `page_actions.py` - Page-related actions (reload, getUrl, cookies, storage, etc.)

**Benefits:**
- Better code organization
- Easier maintenance and testing
- Clear separation of concerns

---

## 🧪 Testing Enhancements

### Comprehensive Test Coverage
- New test file `test_new_features.py` with 28+ test cases
- Enhanced test page `test_page_enhanced.html` with various scenarios
- Tests cover all new features including edge cases

**Benefits:**
- Higher code quality
- Regression prevention
- Confidence in new features

---

## 📝 API Changes

### Backward Compatibility
All new features are **100% backward compatible**. Existing code will continue to work without modifications.

### New Optional Fields
All new `BaseStep` fields are optional, maintaining backward compatibility:
- `retry`, `retryDelay`
- `skipIf`, `onlyIf`
- `waitForSelector`, `waitForSelectorTimeout`, `waitForSelectorState`
- `fallbackSelectors`
- `clickModifiers`, `doubleClick`, `forceClick`, `rightClick`
- `clearBeforeInput`, `inputDelay`
- `required`, `defaultValue`, `regex`, `regexGroup`, `transform`
- `timeout`, `waitUntil`
- `randomDelay`
- `requireVisible`, `requireEnabled`
- `skipOnError`, `continueOnEmpty`

### New Actions
Added to the `action` field type:
- `reload`, `getUrl`, `getTitle`, `getMeta`
- `getCookies`, `setCookies`
- `getLocalStorage`, `setLocalStorage`
- `getSessionStorage`, `setSessionStorage`
- `getViewportSize`, `setViewportSize`
- `screenshot`, `waitForSelector`, `evaluate`

---

## 🎯 Use Cases

### Real-World Scenarios Enabled

1. **E-commerce Scraping**
   - Handle dynamic product loading with `waitForSelector`
   - Extract prices with regex: `regex=r"\$(\d+\.\d+)"`
   - Retry flaky add-to-cart buttons

2. **Form Automation**
   - Fill forms with human-like typing delays
   - Handle conditional form fields with `skipIf`/`onlyIf`
   - Validate form state before submission

3. **Social Media Scraping**
   - Handle infinite scroll with fallback selectors
   - Extract metadata with `getMeta`
   - Manage authentication with cookies/localStorage

4. **Testing Scenarios**
   - Test different viewport sizes
   - Capture screenshots at different stages
   - Evaluate custom JavaScript for assertions

5. **Robust Scraping**
   - Retry failed operations automatically
   - Handle missing elements gracefully
   - Adapt to different page layouts

---

## 🔧 Migration Guide

### No Migration Required!
Since all new features are optional and backward compatible, **no code changes are required**.

### Optional: Adopt New Features
You can gradually adopt new features as needed:

```python
# Old way (still works)
BaseStep(id="click", action="click", object_type="id", object="button")

# New way (with enhancements)
BaseStep(
    id="click",
    action="click",
    object_type="id",
    object="button",
    retry=2,
    waitForSelector="#loading",
    requireVisible=True
)
```

---

**Version:** 1.0.0  
**Release Date:** Oct 31, 2025 
**Compatibility:** Python 3.8+
