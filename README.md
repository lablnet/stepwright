# StepWright

A powerful web scraping library built with Playwright that provides a declarative, step-by-step approach to web automation and data extraction.

## Features

- 🚀 **Declarative Scraping**: Define scraping workflows using Python dictionaries or dataclasses
- 🔄 **Pagination Support**: Built-in support for next button and scroll-based pagination
- 📊 **Data Collection**: Extract text, HTML, values, and files from web pages
- 🔗 **Multi-tab Support**: Handle multiple tabs and complex navigation flows
- 📄 **PDF Generation**: Save pages as PDFs or trigger print-to-PDF actions
- 📥 **File Downloads**: Download files with automatic directory creation
- 🔁 **Looping & Iteration**: ForEach loops for processing multiple elements
- 📡 **Streaming Results**: Real-time result processing with callbacks
- 🎯 **Error Handling**: Graceful error handling with configurable termination
- 🔧 **Flexible Selectors**: Support for ID, class, tag, and XPath selectors
- 🔁 **Retry Logic**: Automatic retry on failure with configurable delays
- 🎛️ **Conditional Execution**: Skip or execute steps based on JavaScript conditions
- ⏳ **Smart Waiting**: Wait for selectors before actions with configurable timeouts
- 🔀 **Fallback Selectors**: Multiple selector fallbacks for increased robustness
- 🖱️ **Enhanced Clicks**: Double-click, right-click, modifier keys, and force clicks
- ⌨️ **Input Enhancements**: Clear before input, human-like typing delays
- 🔍 **Data Transformations**: Regex extraction, JavaScript transformations, default values
- 🌐 **Page Actions**: Reload, get URL/title, meta tags, cookies, localStorage, viewport
- 🤖 **Human-like Behavior**: Random delays to mimic human interaction
- ✅ **Element State Checks**: Require visible/enabled before actions

## Installation

```bash
# Using pip
pip install stepwright

# Using pip with development dependencies
pip install stepwright[dev]

# From source
git clone https://github.com/lablnet/stepwright.git
cd stepwright
pip install -e .
```

## Quick Start

### Basic Usage

```python
import asyncio
from stepwright import run_scraper, TabTemplate, BaseStep

async def main():
    templates = [
        TabTemplate(
            tab="example",
            steps=[
                BaseStep(
                    id="navigate",
                    action="navigate",
                    value="https://example.com"
                ),
                BaseStep(
                    id="get_title",
                    action="data",
                    object_type="tag",
                    object="h1",
                    key="title",
                    data_type="text"
                )
            ]
        )
    ]

    results = await run_scraper(templates)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### Core Functions

#### `run_scraper(templates, options=None)`

Main function to execute scraping templates.

**Parameters:**
- `templates`: List of `TabTemplate` objects
- `options`: Optional `RunOptions` object

**Returns:** `List[Dict[str, Any]]`

```python
results = await run_scraper(templates, RunOptions(
    browser={"headless": True}
))
```

#### `run_scraper_with_callback(templates, on_result, options=None)`

Execute scraping with streaming results via callback.

**Parameters:**
- `templates`: List of `TabTemplate` objects
- `on_result`: Callback function for each result (can be sync or async)
- `options`: Optional `RunOptions` object

```python
async def process_result(result, index):
    print(f"Result {index}: {result}")

await run_scraper_with_callback(templates, process_result)
```

### Types

#### `TabTemplate`

```python
@dataclass
class TabTemplate:
    tab: str
    initSteps: Optional[List[BaseStep]] = None      # Steps executed once before pagination
    perPageSteps: Optional[List[BaseStep]] = None   # Steps executed for each page
    steps: Optional[List[BaseStep]] = None          # Single steps array
    pagination: Optional[PaginationConfig] = None
```

#### `BaseStep`

```python
@dataclass
class BaseStep:
    id: str
    description: Optional[str] = None
    object_type: Optional[SelectorType] = None  # 'id' | 'class' | 'tag' | 'xpath'
    object: Optional[str] = None
    action: Literal[
        "navigate", "input", "click", "data", "scroll", 
        "eventBaseDownload", "foreach", "open", "savePDF", 
        "printToPDF", "downloadPDF", "downloadFile",
        "reload", "getUrl", "getTitle", "getMeta", "getCookies", 
        "setCookies", "getLocalStorage", "setLocalStorage", 
        "getSessionStorage", "setSessionStorage", "getViewportSize", 
        "setViewportSize", "screenshot", "waitForSelector", "evaluate"
    ] = "navigate"
    value: Optional[str] = None
    key: Optional[str] = None
    data_type: Optional[DataType] = None        # 'text' | 'html' | 'value' | 'default' | 'attribute'
    wait: Optional[int] = None
    terminateonerror: Optional[bool] = None
    subSteps: Optional[List["BaseStep"]] = None
    autoScroll: Optional[bool] = None
    
    # Retry configuration
    retry: Optional[int] = None                  # Number of retries on failure (default: 0)
    retryDelay: Optional[int] = None            # Delay between retries in ms (default: 1000)
    
    # Conditional execution
    skipIf: Optional[str] = None                 # JavaScript expression - skip step if true
    onlyIf: Optional[str] = None                # JavaScript expression - execute only if true
    
    # Element waiting and state
    waitForSelector: Optional[str] = None        # Wait for selector before action
    waitForSelectorTimeout: Optional[int] = None # Timeout for waitForSelector in ms (default: 30000)
    waitForSelectorState: Optional[Literal["visible", "hidden", "attached", "detached"]] = None
    
    # Multiple selector fallbacks
    fallbackSelectors: Optional[List[Dict[str, str]]] = None  # List of {object_type, object}
    
    # Click enhancements
    clickModifiers: Optional[List[ClickModifier]] = None  # ['Control', 'Meta', 'Shift', 'Alt']
    doubleClick: Optional[bool] = None            # Perform double click
    forceClick: Optional[bool] = None            # Force click even if not visible/actionable
    rightClick: Optional[bool] = None            # Perform right click
    
    # Input enhancements
    clearBeforeInput: Optional[bool] = None      # Clear input before typing (default: True)
    inputDelay: Optional[int] = None           # Delay between keystrokes in ms
    
    # Data extraction enhancements
    required: Optional[bool] = None             # Raise error if extraction returns None/empty
    defaultValue: Optional[str] = None          # Default value if extraction fails
    regex: Optional[str] = None                 # Regex pattern to extract from data
    regexGroup: Optional[int] = None            # Regex group to extract (default: 0)
    transform: Optional[str] = None             # JavaScript expression to transform data
    
    # Timeout configuration
    timeout: Optional[int] = None                # Step-specific timeout in ms
    
    # Navigation enhancements
    waitUntil: Optional[Literal["load", "domcontentloaded", "networkidle", "commit"]] = None
    
    # Human-like behavior
    randomDelay: Optional[Dict[str, int]] = None # {min: ms, max: ms} for random delay
    
    # Element state checks
    requireVisible: Optional[bool] = None        # Require element visible (default: True for click)
    requireEnabled: Optional[bool] = None       # Require element enabled
    
    # Skip/continue logic
    skipOnError: Optional[bool] = None          # Skip step if error occurs (default: False)
    continueOnEmpty: Optional[bool] = None      # Continue if element not found (default: True)
```

#### `RunOptions`

```python
@dataclass
class RunOptions:
    browser: Optional[dict] = None  # Playwright launch options
    onResult: Optional[Callable] = None
```

## Step Actions

### Navigate
Navigate to a URL.

```python
BaseStep(
    id="go_to_page",
    action="navigate",
    value="https://example.com"
)
```

### Input
Fill form fields.

```python
BaseStep(
    id="search",
    action="input",
    object_type="id",
    object="search-box",
    value="search term"
)
```

### Click
Click on elements.

```python
BaseStep(
    id="submit",
    action="click",
    object_type="class",
    object="submit-button"
)
```

### Data Extraction
Extract data from elements.

```python
BaseStep(
    id="get_title",
    action="data",
    object_type="tag",
    object="h1",
    key="title",
    data_type="text"
)
```

### ForEach Loop
Process multiple elements.

```python
BaseStep(
    id="process_items",
    action="foreach",
    object_type="class",
    object="item",
    subSteps=[
        BaseStep(
            id="get_item_title",
            action="data",
            object_type="tag",
            object="h2",
            key="title",
            data_type="text"
        )
    ]
)
```

### File Operations

#### Event-Based Download
```python
BaseStep(
    id="download_file",
    action="eventBaseDownload",
    object_type="class",
    object="download-link",
    value="./downloads/file.pdf",
    key="downloaded_file"
)
```

#### Download PDF/File
```python
BaseStep(
    id="download_pdf",
    action="downloadPDF",
    object_type="class",
    object="pdf-link",
    value="./output/document.pdf",
    key="pdf_file"
)
```

#### Save PDF
```python
BaseStep(
    id="save_pdf",
    action="savePDF",
    value="./output/page.pdf",
    key="pdf_file"
)
```

## Pagination

### Next Button Pagination
```python
PaginationConfig(
    strategy="next",
    nextButton=NextButtonConfig(
        object_type="class",
        object="next-page",
        wait=2000
    ),
    maxPages=10
)
```

### Scroll Pagination
```python
PaginationConfig(
    strategy="scroll",
    scroll=ScrollConfig(
        offset=800,
        delay=1500
    ),
    maxPages=5
)
```

### Pagination Strategies

#### paginationFirst
Paginate first, then collect data from each page:

```python
TabTemplate(
    tab="news",
    initSteps=[...],
    perPageSteps=[...],  # Collect data from each page
    pagination=PaginationConfig(
        strategy="next",
        nextButton=NextButtonConfig(...),
        paginationFirst=True  # Go to next page before collecting
    )
)
```

#### paginateAllFirst
Paginate through all pages first, then collect all data at once:

```python
TabTemplate(
    tab="articles",
    initSteps=[...],
    perPageSteps=[...],  # Collect all data after all pagination
    pagination=PaginationConfig(
        strategy="next",
        nextButton=NextButtonConfig(...),
        paginateAllFirst=True  # Load all pages first
    )
)
```

## Advanced Features

### Proxy Support
```python
from stepwright import run_scraper, RunOptions

results = await run_scraper(templates, RunOptions(
    browser={
        "proxy": {
            "server": "http://proxy-server:8080",
            "username": "user",
            "password": "pass"
        }
    }
))
```

### Custom Browser Options
```python
results = await run_scraper(templates, RunOptions(
    browser={
        "headless": False,
        "slow_mo": 1000,
        "args": ["--no-sandbox", "--disable-setuid-sandbox"]
    }
))
```

### Streaming Results
```python
async def process_result(result, index):
    print(f"Result {index}: {result}")
    # Process result immediately (e.g., save to database)
    await save_to_database(result)

await run_scraper_with_callback(
    templates, 
    process_result,
    RunOptions(browser={"headless": True})
)
```

### Data Placeholders
Use collected data in subsequent steps:

```python
BaseStep(
    id="get_title",
    action="data",
    object_type="id",
    object="page-title",
    key="page_title",
    data_type="text"
),
BaseStep(
    id="save_with_title",
    action="savePDF",
    value="./output/{{page_title}}.pdf",  # Uses collected page_title
    key="pdf_file"
)
```

### Index Placeholders
Use loop index in foreach steps:

```python
BaseStep(
    id="process_items",
    action="foreach",
    object_type="class",
    object="item",
    subSteps=[
        BaseStep(
            id="save_item",
            action="savePDF",
            value="./output/item_{{i}}.pdf",      # i = 0, 1, 2, ...
            # or
            value="./output/item_{{i_plus1}}.pdf" # i_plus1 = 1, 2, 3, ...
        )
    ]
)
```

## Error Handling

Steps can be configured to terminate on error:

```python
BaseStep(
    id="critical_step",
    action="click",
    object_type="id",
    object="important-button",
    terminateonerror=True  # Stop execution if this fails
)
```

Without `terminateonerror=True`, errors are logged but execution continues.

## Advanced Step Options

### Retry Logic

Automatically retry failed steps with configurable delays:

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

### Conditional Execution

Execute or skip steps based on JavaScript conditions:

```python
# Skip step if condition is true
BaseStep(
    id="optional_click",
    action="click",
    object_type="id",
    object="optional-button",
    skipIf="document.querySelector('.modal').classList.contains('hidden')"
)

# Execute only if condition is true
BaseStep(
    id="conditional_data",
    action="data",
    object_type="id",
    object="dynamic-content",
    key="content",
    onlyIf="document.querySelector('#dynamic-content') !== null"
)
```

### Wait for Selector

Wait for elements to appear before performing actions:

```python
BaseStep(
    id="click_after_load",
    action="click",
    object_type="id",
    object="target-button",
    waitForSelector="#loading-indicator",      # Wait for this selector
    waitForSelectorTimeout=5000,               # Timeout: 5 seconds
    waitForSelectorState="hidden"              # Wait until hidden
)
```

### Fallback Selectors

Provide multiple selector options for increased robustness:

```python
BaseStep(
    id="click_with_fallback",
    action="click",
    object_type="id",
    object="primary-button",                   # Try this first
    fallbackSelectors=[
        {"object_type": "class", "object": "btn-primary"},
        {"object_type": "class", "object": "submit-btn"},
        {"object_type": "xpath", "object": "//button[contains(text(), 'Submit')]"}
    ]
)
```

### Click Enhancements

Advanced click options for different interaction types:

```python
# Double click
BaseStep(
    id="double_click",
    action="click",
    object_type="id",
    object="item",
    doubleClick=True
)

# Right click (context menu)
BaseStep(
    id="right_click",
    action="click",
    object_type="id",
    object="context-menu-trigger",
    rightClick=True
)

# Click with modifier keys (Ctrl/Cmd+Click)
BaseStep(
    id="multi_select",
    action="click",
    object_type="class",
    object="item",
    clickModifiers=["Control"]  # or ["Meta"] for Mac
)

# Force click (click hidden elements)
BaseStep(
    id="force_click",
    action="click",
    object_type="id",
    object="hidden-button",
    forceClick=True
)
```

### Input Enhancements

More control over input behavior:

```python
# Clear input before typing (default: True)
BaseStep(
    id="clear_and_input",
    action="input",
    object_type="id",
    object="search-box",
    value="new search term",
    clearBeforeInput=True  # Clear existing value first
)

# Human-like typing with delays
BaseStep(
    id="human_like_input",
    action="input",
    object_type="id",
    object="form-field",
    value="slowly typed text",
    inputDelay=100  # 100ms delay between each character
)
```

### Data Extraction Enhancements

Advanced data extraction and transformation options:

```python
# Extract with regex
BaseStep(
    id="extract_price",
    action="data",
    object_type="id",
    object="price",
    key="price",
    regex=r"\$(\d+\.\d+)",        # Extract dollar amount
    regexGroup=1                   # Get first capture group
)

# Transform extracted data with JavaScript
BaseStep(
    id="transform_data",
    action="data",
    object_type="id",
    object="raw-data",
    key="processed",
    transform="value.toUpperCase().trim()"  # JavaScript transformation
)

# Required field with default value
BaseStep(
    id="get_required_data",
    action="data",
    object_type="id",
    object="important-field",
    key="important",
    required=True,                 # Raise error if not found
    defaultValue="N/A"            # Use if extraction fails
)

# Continue even if element not found
BaseStep(
    id="optional_data",
    action="data",
    object_type="id",
    object="optional-content",
    key="optional",
    continueOnEmpty=True           # Don't raise error if not found
)
```

### Element State Checks

Validate element state before actions:

```python
BaseStep(
    id="click_visible",
    action="click",
    object_type="id",
    object="button",
    requireVisible=True,           # Ensure element is visible
    requireEnabled=True            # Ensure element is enabled
)
```

### Random Delays

Add human-like random delays to actions:

```python
BaseStep(
    id="human_like_action",
    action="click",
    object_type="id",
    object="button",
    randomDelay={"min": 500, "max": 2000}  # Random delay between 500-2000ms
)
```

### Skip on Error

Skip steps that fail instead of stopping execution:

```python
BaseStep(
    id="optional_step",
    action="click",
    object_type="id",
    object="optional-button",
    skipOnError=True  # Continue even if this step fails
)
```

## Page Actions

### Reload Page

Reload the current page with optional wait conditions:

```python
BaseStep(
    id="reload",
    action="reload",
    waitUntil="networkidle"  # Wait for network to be idle
)
```

### Get Current URL

```python
BaseStep(
    id="get_url",
    action="getUrl",
    key="current_url"  # Store in collector
)
```

### Get Page Title

```python
BaseStep(
    id="get_title",
    action="getTitle",
    key="page_title"
)
```

### Get Meta Tags

```python
# Get specific meta tag
BaseStep(
    id="get_description",
    action="getMeta",
    object="description",  # Meta name or property
    key="meta_description"
)

# Get all meta tags
BaseStep(
    id="get_all_meta",
    action="getMeta",
    key="all_meta_tags"  # Returns dictionary of all meta tags
)
```

### Cookies Management

```python
# Get all cookies
BaseStep(
    id="get_cookies",
    action="getCookies",
    key="cookies"
)

# Get specific cookie
BaseStep(
    id="get_session_cookie",
    action="getCookies",
    object="session_id",
    key="session"
)

# Set cookie
BaseStep(
    id="set_cookie",
    action="setCookies",
    object="preference",
    value="dark_mode"
)
```

### LocalStorage & SessionStorage

```python
# Get localStorage value
BaseStep(
    id="get_storage",
    action="getLocalStorage",
    object="user_preference",
    key="preference"
)

# Set localStorage value
BaseStep(
    id="set_storage",
    action="setLocalStorage",
    object="theme",
    value="dark"
)

# Get all localStorage items
BaseStep(
    id="get_all_storage",
    action="getLocalStorage",
    key="all_storage"
)

# SessionStorage (same pattern)
BaseStep(
    id="get_session",
    action="getSessionStorage",
    object="temp_data",
    key="data"
)
```

### Viewport Operations

```python
# Get viewport size
BaseStep(
    id="get_viewport",
    action="getViewportSize",
    key="viewport"
)

# Set viewport size
BaseStep(
    id="set_viewport",
    action="setViewportSize",
    value="1920x1080"  # or "1920,1080" or "1920 1080"
)
```

### Screenshot

```python
# Full page screenshot
BaseStep(
    id="screenshot",
    action="screenshot",
    value="./screenshots/page.png",
    data_type="full"  # Full page, omit for viewport only
)

# Element screenshot
BaseStep(
    id="element_screenshot",
    action="screenshot",
    object_type="id",
    object="content-area",
    value="./screenshots/element.png",
    key="screenshot_path"
)
```

### Wait for Selector

Explicit wait for element state:

```python
BaseStep(
    id="wait_for_element",
    action="waitForSelector",
    object_type="id",
    object="dynamic-content",
    value="visible",      # visible, hidden, attached, detached
    wait=5000,            # Timeout in ms
    key="wait_result"     # Stores True/False
)
```

### Evaluate JavaScript

Execute custom JavaScript:

```python
BaseStep(
    id="custom_js",
    action="evaluate",
    value="() => document.querySelector('.counter').textContent",
    key="counter_value"
)
```

## Complete Example

```python
import asyncio
from pathlib import Path
from stepwright import (
    run_scraper,
    TabTemplate,
    BaseStep,
    PaginationConfig,
    NextButtonConfig,
    RunOptions
)

async def main():
    templates = [
        TabTemplate(
            tab="news_scraper",
            initSteps=[
                BaseStep(
                    id="navigate",
                    action="navigate",
                    value="https://news-site.com"
                ),
                BaseStep(
                    id="search",
                    action="input",
                    object_type="id",
                    object="search-box",
                    value="technology"
                )
            ],
            perPageSteps=[
                BaseStep(
                    id="collect_articles",
                    action="foreach",
                    object_type="class",
                    object="article",
                    subSteps=[
                        BaseStep(
                            id="get_title",
                            action="data",
                            object_type="tag",
                            object="h2",
                            key="title",
                            data_type="text"
                        ),
                        BaseStep(
                            id="get_content",
                            action="data",
                            object_type="tag",
                            object="p",
                            key="content",
                            data_type="text"
                        ),
                        BaseStep(
                            id="get_link",
                            action="data",
                            object_type="tag",
                            object="a",
                            key="link",
                            data_type="value"
                        )
                    ]
                )
            ],
            pagination=PaginationConfig(
                strategy="next",
                nextButton=NextButtonConfig(
                    object_type="id",
                    object="next-page",
                    wait=2000
                ),
                maxPages=5
            )
        )
    ]

    # Run scraper
    results = await run_scraper(templates, RunOptions(
        browser={"headless": True}
    ))

    # Process results
    for i, article in enumerate(results):
        print(f"\nArticle {i + 1}:")
        print(f"Title: {article.get('title')}")
        print(f"Content: {article.get('content')[:100]}...")
        print(f"Link: {article.get('link')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/lablnet/stepwright.git
cd stepwright

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_scraper.py

# Run specific test class
pytest tests/test_scraper.py::TestGetBrowser

# Run specific test
pytest tests/test_scraper.py::TestGetBrowser::test_create_browser_instance

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests only
pytest tests/test_integration.py
```

### Project Structure

```
stepwright/
├── src/
│   ├── __init__.py
│   ├── step_types.py      # Type definitions and dataclasses
│   ├── helpers.py         # Utility functions
│   ├── executor.py        # Core step execution logic
│   ├── parser.py          # Public API (run_scraper)
│   ├── scraper.py         # Low-level browser automation
│   ├── handlers/          # Action-specific handlers
│   │   ├── __init__.py
│   │   ├── data_handlers.py      # Data extraction handlers
│   │   ├── file_handlers.py      # File download/PDF handlers
│   │   ├── loop_handlers.py      # Foreach/open handlers
│   │   └── page_actions.py       # Page-related actions (reload, getUrl, etc.)
│   └── scraper_parser.py  # Backward compatibility
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── test_page.html     # Test HTML page
│   ├── test_page_enhanced.html  # Enhanced test page for new features
│   ├── test_scraper.py    # Core scraper tests
│   ├── test_parser.py     # Parser function tests
│   ├── test_new_features.py  # Tests for new features
│   └── test_integration.py # Integration tests
├── pyproject.toml         # Package configuration
├── setup.py               # Setup script
├── pytest.ini             # Pytest configuration
├── README.md              # This file
└── README_TESTS.md        # Detailed test documentation
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

## Module Organization

The codebase follows separation of concerns:

- **step_types.py**: All type definitions (BaseStep, TabTemplate, etc.)
- **helpers.py**: Utility functions (placeholder replacement, locator creation, condition evaluation)
- **executor.py**: Core execution logic (execute steps, handle pagination, retry logic)
- **parser.py**: Public API (run_scraper, run_scraper_with_callback)
- **scraper.py**: Low-level Playwright wrapper (navigate, click, get_data)
- **handlers/**: Action-specific handlers organized by functionality
  - **data_handlers.py**: Data extraction logic with transformations
  - **file_handlers.py**: File download and PDF operations
  - **loop_handlers.py**: Foreach loops and new tab/window handling
  - **page_actions.py**: Page-related actions (reload, getUrl, cookies, storage, etc.)
- **scraper_parser.py**: Backward compatibility wrapper

You can import from the main module or specific submodules:

```python
# From main module (recommended)
from stepwright import run_scraper, TabTemplate, BaseStep

# From specific modules
from stepwright.step_types import TabTemplate, BaseStep
from stepwright.parser import run_scraper
from stepwright.helpers import replace_data_placeholders
```

## Testing

See [README_TESTS.md](README_TESTS.md) for detailed testing documentation.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 Issues: [GitHub Issues](https://github.com/lablnet/stepwright/issues)
- 📖 Documentation: [README.md](README.md) and [README_TESTS.md](README_TESTS.md)
- 💬 Discussions: [GitHub Discussions](https://github.com/lablnet/stepwright/discussions)

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Inspired by declarative web scraping patterns
- Original TypeScript version: [framework-Island/stepwright](https://github.com/framework-Island/stepwright)

## Author

Muhammad Umer Farooq ([@lablnet](https://github.com/lablnet))

