# What's New in StepWright 1.0.0

## 🎉 Major Release - Enhanced Scraping Capabilities

StepWright 1.0.0 introduces a comprehensive set of new features designed to make web scraping more robust, flexible, and powerful. This release focuses on reliability, conditional logic, advanced interactions, and expanded page manipulation capabilities.

---

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
