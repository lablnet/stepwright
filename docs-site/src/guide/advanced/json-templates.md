# JSON Templates & Storage

StepWright allows you to export declarative scraping templates as JSON files, load templates dynamically from disk or dictionaries, and execute scraping directly from JSON template files without writing scraper workflows in Python code.

---

## 💡 Why Use JSON Templates?

- **Code Separation**: Store and manage scraper definitions as clean JSON config files separate from Python application code.
- **Dynamic Workflows**: Load, construct, or update scraping templates from database entries, CMS systems, or remote API endpoints.
- **Portability**: Share scraper templates across different microservices, environments, or non-Python tools.

---

## 📤 Exporting Templates to JSON

Any StepWright template (`TabTemplate`, `ParallelTemplate`, `ParameterizedTemplate`) or `BaseStep` can be converted into a dictionary or exported to a JSON file.

### Using `save_template` or `to_json()`

```python
from stepwright import TabTemplate, BaseStep, PaginationConfig, NextButtonConfig, save_template

template = TabTemplate(
    tab="product_catalog",
    steps=[
        BaseStep(id="s1", action="navigate", value="https://example.com/products"),
        BaseStep(id="s2", action="data", object_type="css", object="h2.title", key="name", data_type="text"),
        BaseStep(id="s3", action="data", object_type="css", object="span.price", key="price", data_type="text"),
    ],
    pagination=PaginationConfig(
        strategy="next",
        nextButton=NextButtonConfig(object_type="css", object="a.next-page"),
        maxPages=5,
    )
)

# Option 1: Save directly to a file
save_template(template, "product_catalog.json")

# Option 2: Use the dataclass instance method
template.to_json("product_catalog.json")

# Option 3: Get JSON string in memory
json_string = template.to_json()
```

---

## 📥 Loading & Importing JSON Templates

You can load templates from JSON files, JSON strings, or dictionaries using `load_template()`. StepWright automatically detects whether the file contains a `TabTemplate`, `ParallelTemplate`, `ParameterizedTemplate`, or a list of templates.

```python
from stepwright import load_template, TabTemplate

# Load from a JSON file path
template = load_template("product_catalog.json")

# Or load from a dictionary
template_dict = {
    "tab": "news_scraper",
    "steps": [
        {"id": "s1", "action": "navigate", "value": "https://news.example.com"},
        {"id": "s2", "action": "data", "object_type": "tag", "object": "h1", "key": "headline", "data_type": "text"}
    ]
}
template = load_template(template_dict)
```

---

## 🚀 Direct Execution from JSON Files

You can pass JSON file paths, JSON strings, or raw dictionaries directly to `run_scraper()` or `run_scraper_with_metrics()`:

```python
import asyncio
from stepwright import run_scraper

async def main():
    # Execute scraper directly from a JSON template file
    results = await run_scraper("product_catalog.json")
    print(f"Scraped {len(results)} items!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📦 Storing Multiple Templates in JSON

StepWright supports storing single templates, lists of templates, or concurrent multi-tab workflows inside JSON.

### 1. Storing Multiple Templates in a JSON Array

Create a JSON file (`multi_templates.json`) containing an array of template objects:

```json
[
  {
    "type": "TabTemplate",
    "tab": "category_a",
    "steps": [
      {
        "id": "nav_a",
        "action": "navigate",
        "value": "https://example.com/category-a"
      },
      {
        "id": "get_a",
        "action": "data",
        "object_type": "css",
        "object": ".item-title",
        "key": "title",
        "data_type": "text"
      }
    ]
  },
  {
    "type": "TabTemplate",
    "tab": "category_b",
    "steps": [
      {
        "id": "nav_b",
        "action": "navigate",
        "value": "https://example.com/category-b"
      },
      {
        "id": "get_b",
        "action": "data",
        "object_type": "css",
        "object": ".item-title",
        "key": "title",
        "data_type": "text"
      }
    ]
  }
]
```

Run both templates directly:
```python
results = await run_scraper("multi_templates.json")
```

### 2. Parallel JSON Templates (`ParallelTemplate`)

Define multiple workflows to run concurrently in parallel tabs:

```json
{
  "type": "ParallelTemplate",
  "max_concurrency": 3,
  "templates": [
    {
      "tab": "site_news",
      "steps": [
        {"id": "n1", "action": "navigate", "value": "https://example.com/news"},
        {"id": "d1", "action": "data", "object_type": "css", "object": ".article", "key": "headline"}
      ]
    },
    {
      "tab": "site_blogs",
      "steps": [
        {"id": "n2", "action": "navigate", "value": "https://example.com/blog"},
        {"id": "d2", "action": "data", "object_type": "css", "object": ".post-title", "key": "title"}
      ]
    }
  ]
}
```

### 3. Parameterized JSON Templates (`ParameterizedTemplate`)

Define a template with variable placeholders and iterate over parameter values in parallel:

```json
{
  "type": "ParameterizedTemplate",
  "parameter_key": "category",
  "values": ["electronics", "books", "fashion"],
  "max_concurrency": 2,
  "template": {
    "tab": "search_{{category}}",
    "steps": [
      {
        "id": "s1",
        "action": "navigate",
        "value": "https://example.com/search?q={{category}}"
      },
      {
        "id": "s2",
        "action": "data",
        "object_type": "css",
        "object": ".product-name",
        "key": "name",
        "data_type": "text"
      }
    ]
  }
}
```

Execution:
```python
results = await run_scraper("parameterized_search.json")
```

---

## 🛠️ API Summary

| Function / Method | Description |
| :--- | :--- |
| `load_template(source)` | Loads a template from JSON file path, string, dict, or template object |
| `save_template(template, path)` | Writes a template object or list to a JSON file on disk |
| `template_to_json(template)` | Converts a template object or list to a JSON string or file |
| `template_from_json(source)` | Parses a template from a JSON string or file |
| `parse_template_from_dict(d)` | Auto-detects and constructs `TabTemplate`, `ParallelTemplate`, or `ParameterizedTemplate` |
| `tmpl.to_dict()` | Dataclass instance method returning a JSON-friendly dict |
| `tmpl.to_json(file_path=None)` | Dataclass instance method returning or saving JSON |
| `TabTemplate.from_dict(d)` | Constructs a `TabTemplate` from a dictionary |
| `TabTemplate.from_json(src)` | Constructs a `TabTemplate` from a JSON file or string |
