# StepWright Test Suite

Comprehensive test suite for StepWright web scraping framework.

## Project Structure

The codebase has been refactored following separation of concerns:

```
src/
├── step_types.py     # Type definitions and dataclasses
├── helpers.py        # Utility functions (placeholders, locators)
├── executor.py       # Core step execution logic
├── parser.py         # Public API (run_scraper functions)
├── scraper.py        # Low-level browser automation
└── scraper_parser.py # Backward compatibility wrapper

tests/
├── __init__.py
├── conftest.py       # Pytest configuration and fixtures
├── test_page.html    # Test HTML page
├── test_scraper.py   # Tests for core scraper functions
├── test_parser.py    # Tests for parser functions
└── test_integration.py # Integration tests
```

## Separation of Concerns

### 1. **step_types.py** - Type Definitions
- `BaseStep`: Single scraping step/action
- `NextButtonConfig`: Next button pagination config
- `ScrollConfig`: Scroll-based pagination config
- `PaginationConfig`: Pagination strategy
- `TabTemplate`: Scraping workflow template
- `RunOptions`: Scraper execution options
- Type aliases: `SelectorType`, `DataType`

### 2. **helpers.py** - Utility Functions
- `replace_index_placeholders()`: Replace {{ i }}, {{ i_plus1 }} in strings
- `replace_data_placeholders()`: Replace {{ key }} with collector values
- `locator_for()`: Create Playwright locator from selector type
- `_ensure_dir()`: Ensure directory exists for file operations
- `maybe_await()`: Helper for awaiting coroutines conditionally

### 3. **executor.py** - Core Execution Logic
- `execute_step()`: Execute a single scraping step
- `execute_step_list()`: Execute list of steps sequentially
- `execute_tab()`: Execute complete tab template with pagination
- `clone_step_with_index()`: Clone step with index placeholders
- Private handlers: `_handle_event_download()`, `_handle_foreach()`, etc.

### 4. **parser.py** - Public API
- `run_scraper()`: Execute templates and return collected data
- `run_scraper_with_callback()`: Execute with streaming results

### 5. **scraper.py** - Low-Level Browser Automation
- Browser management: `get_browser()`
- Navigation: `navigate()`
- Element interaction: `elem()`, `click()`, `input()`
- Data extraction: `get_data()`

## Test Suite

### Test Categories

#### 1. **test_scraper.py** - Core Scraper Tests
Tests for low-level browser automation functions:
- Browser creation and configuration
- Page navigation
- Element selection (by ID, class, tag, XPath)
- User interactions (input, click, double-click, checkbox)
- Data extraction (text, HTML, value, attributes)

#### 2. **test_parser.py** - Parser Function Tests
Tests for high-level scraping operations:
- Basic navigation and data extraction
- Form input and submission
- Foreach loops
- Pagination (next button and scroll)
- PDF generation
- File downloads
- Proxy and browser configuration
- Data placeholder replacement

#### 3. **test_integration.py** - Integration Tests
End-to-end scenarios:
- Complete news scraping with pagination
- Streaming results with real-time processing
- Complex form interactions
- File operations and downloads
- Custom browser configurations

## Running Tests

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Install Playwright browsers
playwright install chromium
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Core scraper tests
pytest tests/test_scraper.py

# Parser function tests
pytest tests/test_parser.py

# Integration tests
pytest tests/test_integration.py
```

### Run Specific Test Classes

```bash
pytest tests/test_scraper.py::TestGetBrowser
pytest tests/test_parser.py::TestRunScraper
pytest tests/test_integration.py::TestCompleteNewsScrapingScenario
```

### Run Specific Tests

```bash
pytest tests/test_scraper.py::TestNavigate::test_navigate_to_url
pytest tests/test_parser.py::TestRunScraper::test_basic_navigation_and_data_extraction
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=src --cov-report=html
```

## Test Fixtures

### Global Fixtures (conftest.py)
- `test_data_dir`: Path to test data directory
- `test_page_html_path`: Path to test HTML page

### Per-Test Fixtures
- `browser`: Playwright browser instance (module scope)
- `page`: Playwright page instance (function scope)
- `test_page_url`: File URL to test HTML page
- `tmp_path`: Temporary directory for file operations

