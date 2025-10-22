# StepWright Examples

This directory contains example scripts demonstrating various features of StepWright.

## Prerequisites

```bash
# Install StepWright
pip install stepwright

# Or for development
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Examples

### 1. Basic Example (`basic_example.py`)

A simple example demonstrating:
- Basic navigation
- Scrolling and waiting
- Data extraction with different selectors
- Headless browser configuration

**Run:**
```bash
python examples/basic_example.py
```

**Features:**
- Navigate to example.com
- Extract title and description
- Use tag and XPath selectors
- Headless mode with optimized args

### 2. Advanced Example (`advanced_example.py`)

An advanced example with:
- Pagination (multiple pages)
- ForEach loops for multiple items
- Initial setup steps
- Complex XPath selectors
- Streaming results option

**Run:**
```bash
python examples/advanced_example.py
```

**Features:**
- Scrape Hacker News articles
- Handle pagination (3 pages)
- Extract titles, links, scores, authors
- Support both batch and streaming modes

## Example Output

### Basic Example
```
🚀 Starting scraper...
✅ Scraping completed!
📊 Results: [
  {
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples..."
  }
]
```

### Advanced Example
```
🚀 Starting advanced scraper...
✅ Scraping completed!
📊 Found 90 articles
[
  {
    "title": "Example Article Title",
    "link": "https://example.com/article",
    "score": "123 points",
    "author": "username",
    "comments": "45 comments"
  },
  ...
]
```

## Running from Source

If you're developing or haven't installed the package:

```bash
# From project root
cd stepwright

# Run basic example
python examples/basic_example.py

# Run advanced example
python examples/advanced_example.py
```

## Customization

### Change Browser Mode

**Headless (default):**
```python
RunOptions(browser={'headless': True})
```

**Visible browser:**
```python
RunOptions(browser={'headless': False})
```

**With slow motion (for debugging):**
```python
RunOptions(browser={'headless': False, 'slow_mo': 1000})
```

### Add Proxy

```python
RunOptions(
    browser={
        'headless': True,
        'proxy': {
            'server': 'http://proxy-server:8080',
            'username': 'user',
            'password': 'pass'
        }
    }
)
```

### Stream Results

Uncomment the streaming section in `advanced_example.py`:

```python
async def on_result(result, index):
    print(f'Article {index + 1}: {result.get("title")}')
    # Process result immediately (e.g., save to database)

await run_scraper_with_callback(templates, on_result, options)
```

## Common Issues

### Import Error
```
ModuleNotFoundError: No module named 'stepwright'
```
**Solution:** Install the package or run from project root with correct path.

### Browser Not Found
```
Playwright executable not found
```
**Solution:** Run `playwright install chromium`

### Timeout Errors
**Solution:** Increase wait times or add more delays between actions.

## More Examples

Want to see more examples? Check out:
- Test files in `tests/` directory
- Documentation in `README.md`
- Quick start guide in `QUICKSTART.md`

## Contributing Examples

Have a great example? We'd love to see it!
1. Create a new example file
2. Add documentation
3. Test it works
4. Submit a pull request

See `CONTRIBUTING.md` for guidelines.

## Support

- 📖 Documentation: [README.md](../README.md)
- 🚀 Quick Start: [QUICKSTART.md](../QUICKSTART.md)
- 🐛 Issues: [GitHub Issues](https://github.com/lablnet/stepwright/issues)

