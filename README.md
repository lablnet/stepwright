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
        "printToPDF", "downloadPDF", "downloadFile"
    ] = "navigate"
    value: Optional[str] = None
    key: Optional[str] = None
    data_type: Optional[DataType] = None        # 'text' | 'html' | 'value' | 'default' | 'attribute'
    wait: Optional[int] = None
    terminateonerror: Optional[bool] = None
    subSteps: Optional[List["BaseStep"]] = None
    autoScroll: Optional[bool] = None
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
│   └── scraper_parser.py  # Backward compatibility
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── test_page.html     # Test HTML page
│   ├── test_scraper.py    # Core scraper tests
│   ├── test_parser.py     # Parser function tests
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
- **helpers.py**: Utility functions (placeholder replacement, locator creation)
- **executor.py**: Core execution logic (execute steps, handle pagination)
- **parser.py**: Public API (run_scraper, run_scraper_with_callback)
- **scraper.py**: Low-level Playwright wrapper (navigate, click, get_data)
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

