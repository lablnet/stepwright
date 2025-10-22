# StepWright Quick Start Guide

Get up and running with StepWright in 5 minutes!

## Installation

```bash
pip install stepwright
playwright install chromium
```

## Your First Scraper

Create a file `my_scraper.py`:

```python
import asyncio
from stepwright import run_scraper, TabTemplate, BaseStep

async def main():
    # Define your scraping workflow
    templates = [
        TabTemplate(
            tab="quotes",
            steps=[
                # Navigate to website
                BaseStep(
                    id="navigate",
                    action="navigate",
                    value="https://quotes.toscrape.com"
                ),
                # Extract quotes using foreach loop
                BaseStep(
                    id="extract_quotes",
                    action="foreach",
                    object_type="class",
                    object="quote",
                    subSteps=[
                        BaseStep(
                            id="get_text",
                            action="data",
                            object_type="class",
                            object="text",
                            key="quote_text",
                            data_type="text"
                        ),
                        BaseStep(
                            id="get_author",
                            action="data",
                            object_type="class",
                            object="author",
                            key="author",
                            data_type="text"
                        )
                    ]
                )
            ]
        )
    ]
    
    # Run the scraper
    results = await run_scraper(templates)
    
    # Print results
    for i, quote in enumerate(results, 1):
        print(f"{i}. \"{quote['quote_text']}\" - {quote['author']}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_scraper.py
```

## Common Use Cases

### 1. Simple Data Extraction

```python
from stepwright import run_scraper, TabTemplate, BaseStep

templates = [
    TabTemplate(
        tab="simple",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(
                id="title",
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
print(results[0]["title"])
```

### 2. Form Interaction

```python
templates = [
    TabTemplate(
        tab="search",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(
                id="search",
                action="input",
                object_type="id",
                object="search-box",
                value="python"
            ),
            BaseStep(
                id="submit",
                action="click",
                object_type="id",
                object="search-button"
            ),
            BaseStep(
                id="results",
                action="data",
                object_type="class",
                object="results",
                key="search_results",
                data_type="text"
            )
        ]
    )
]
```

### 3. Pagination

```python
from stepwright import PaginationConfig, NextButtonConfig

templates = [
    TabTemplate(
        tab="paginated",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
        ],
        perPageSteps=[
            BaseStep(
                id="collect",
                action="foreach",
                object_type="class",
                object="item",
                subSteps=[
                    BaseStep(
                        id="get_name",
                        action="data",
                        object_type="tag",
                        object="h2",
                        key="name",
                        data_type="text"
                    )
                ]
            )
        ],
        pagination=PaginationConfig(
            strategy="next",
            nextButton=NextButtonConfig(
                object_type="class",
                object="next-page"
            ),
            maxPages=5
        )
    )
]
```

### 4. Save as PDF

```python
templates = [
    TabTemplate(
        tab="pdf",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(
                id="save",
                action="savePDF",
                value="./output/page.pdf",
                key="pdf_file"
            )
        ]
    )
]
```

### 5. Streaming Results

```python
from stepwright import run_scraper_with_callback

async def process_result(result, index):
    print(f"Processing result {index}: {result}")
    # Save to database, file, etc.

await run_scraper_with_callback(templates, process_result)
```

## Selector Types

StepWright supports multiple selector types:

```python
# By ID
BaseStep(object_type="id", object="my-id")

# By Class
BaseStep(object_type="class", object="my-class")

# By Tag
BaseStep(object_type="tag", object="h1")

# By XPath
BaseStep(object_type="xpath", object="//div[@class='content']")
```

## Data Types

Extract different types of data:

```python
# Text content
BaseStep(data_type="text")    # Inner text

# HTML content
BaseStep(data_type="html")    # Inner HTML

# Form values
BaseStep(data_type="value")   # Input value

# Default (inner text)
BaseStep(data_type="default")
```

## Actions Reference

| Action | Description | Example |
|--------|-------------|---------|
| `navigate` | Go to URL | `BaseStep(action="navigate", value="https://...") ` |
| `input` | Fill form field | `BaseStep(action="input", object="search", value="text")` |
| `click` | Click element | `BaseStep(action="click", object="button")` |
| `data` | Extract data | `BaseStep(action="data", object="h1", key="title")` |
| `foreach` | Loop elements | `BaseStep(action="foreach", object="item", subSteps=[...])` |
| `scroll` | Scroll page | `BaseStep(action="scroll", value="500")` |
| `savePDF` | Save as PDF | `BaseStep(action="savePDF", value="./file.pdf")` |
| `downloadPDF` | Download PDF | `BaseStep(action="downloadPDF", object="link", value="./file.pdf")` |

## Error Handling

```python
# Continue on error (default)
BaseStep(id="optional", action="click", object="maybe-exists")

# Stop on error
BaseStep(
    id="critical",
    action="click",
    object="must-exist",
    terminateonerror=True
)
```

## Wait Times

```python
# Wait after action (milliseconds)
BaseStep(
    id="load",
    action="click",
    object="load-button",
    wait=2000  # Wait 2 seconds
)
```

## Browser Options

```python
from stepwright import RunOptions

# Headless mode (default)
results = await run_scraper(templates, RunOptions(
    browser={"headless": True}
))

# Visible browser
results = await run_scraper(templates, RunOptions(
    browser={"headless": False}
))

# With proxy
results = await run_scraper(templates, RunOptions(
    browser={
        "proxy": {
            "server": "http://proxy:8080"
        }
    }
))

# Slow motion (for debugging)
results = await run_scraper(templates, RunOptions(
    browser={
        "headless": False,
        "slow_mo": 1000  # 1 second delay between actions
    }
))
```

## Tips & Tricks

### 1. Debug Mode

```python
# Run with visible browser and slow motion
results = await run_scraper(templates, RunOptions(
    browser={"headless": False, "slow_mo": 500}
))
```

### 2. Use Data Placeholders

```python
steps = [
    BaseStep(id="get_name", action="data", object="h1", key="name"),
    BaseStep(
        id="save",
        action="savePDF",
        value="./output/{{name}}.pdf"  # Uses extracted name
    )
]
```

### 3. Auto-scroll in ForEach

```python
BaseStep(
    action="foreach",
    object="item",
    autoScroll=True,  # Scroll to each item (default)
    subSteps=[...]
)
```

### 4. Conditional Steps

```python
# Steps gracefully handle missing elements
BaseStep(
    id="optional_banner",
    action="click",
    object="dismiss-banner",
    terminateonerror=False  # Continue if not found
)
```

## Next Steps

- Read the full [README.md](README.md) for complete API reference
- Check [README_TESTS.md](README_TESTS.md) for testing guide
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- View [PACKAGING.md](PACKAGING.md) for distribution info

## Examples

Check out complete examples in the `examples/` directory (coming soon):
- Basic web scraping
- E-commerce product extraction
- News article collection
- Form automation
- Multi-page pagination

## Getting Help

- 📖 Documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/lablnet/stepwright/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/lablnet/stepwright/discussions)

Happy scraping! 🚀

