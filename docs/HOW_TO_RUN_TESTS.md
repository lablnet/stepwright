# How to Run Tests - StepWright

Complete guide to running tests for StepWright package.

## Quick Start

```bash
# Install and run tests
pip install -e ".[dev]"
playwright install chromium
pytest
```

## Installation

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Verify Python version (3.8+ required)
python --version
```

### 2. Install Package

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# This installs:
# - stepwright package (editable)
# - playwright
# - pytest
# - pytest-asyncio
# - pytest-cov
# - black, flake8, mypy
```

### 3. Install Playwright Browsers

```bash
# Install Chromium browser
playwright install chromium

# Or install all browsers
playwright install
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with extra verbose output (show test names)
pytest -vv

# Run quietly (less output)
pytest -q
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/test_scraper.py

# Run single test class
pytest tests/test_scraper.py::TestGetBrowser

# Run single test method
pytest tests/test_scraper.py::TestGetBrowser::test_create_browser_instance

# Run multiple specific files
pytest tests/test_scraper.py tests/test_parser.py

# Run tests matching pattern
pytest -k "navigate"  # Runs tests with "navigate" in name
pytest -k "test_get"  # Runs tests starting with "test_get"
```

### Test by Category

```bash
# Core scraper functions
pytest tests/test_scraper.py

# Parser and high-level API
pytest tests/test_parser.py

# Integration tests
pytest tests/test_integration.py
```

## Test Output Options

### Verbose Modes

```bash
# Standard output
pytest

# Verbose (show test names)
pytest -v

# Extra verbose (show test docstrings)
pytest -vv

# Show print statements
pytest -s

# Combine options
pytest -vv -s
```

### Output Formats

```bash
# Default format
pytest

# Show test summary
pytest --tb=short

# Show only failures
pytest --tb=line

# No traceback
pytest --tb=no

# Show locals in traceback
pytest -l
```

## Coverage Reports

### Basic Coverage

```bash
# Run tests with coverage
pytest --cov=src

# With HTML report
pytest --cov=src --cov-report=html

# Open HTML report
# On Mac:
open htmlcov/index.html
# On Linux:
xdg-open htmlcov/index.html
# On Windows:
start htmlcov/index.html
```

### Coverage Options

```bash
# Show missing lines
pytest --cov=src --cov-report=term-missing

# Coverage for specific module
pytest --cov=src/parser

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80

# Generate multiple report formats
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

## Test Filtering

### By Markers

```bash
# Run only async tests
pytest -m asyncio

# Run only slow tests (if marked)
pytest -m slow

# Run all except slow tests
pytest -m "not slow"
```

### By Path

```bash
# Run tests in directory
pytest tests/

# Run tests in specific subdirectory
pytest tests/integration/
```

### By Name Pattern

```bash
# Tests containing "browser"
pytest -k browser

# Tests containing "scraper" but not "parser"
pytest -k "scraper and not parser"

# Multiple patterns
pytest -k "test_get or test_create"
```

## Debugging Tests

### Stop on First Failure

```bash
# Stop at first failure
pytest -x

# Stop after N failures
pytest --maxfail=3
```

### Debug Failed Tests

```bash
# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Show locals for failing tests
pytest -l

# Drop into debugger on failure
pytest --pdb
```

### Verbose Debugging

```bash
# Show all output
pytest -vv -s

# Show which tests will run (don't execute)
pytest --collect-only

# Show fixtures being used
pytest --fixtures
```

## Performance

### Timing Tests

```bash
# Show slowest N tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Time limit per test (requires pytest-timeout)
pytest --timeout=30
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPU count)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

## Configuration

### pytest.ini

The project includes `pytest.ini` with default configuration:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --strict-markers --tb=short
```

### Override Configuration

```bash
# Override settings from command line
pytest --tb=long  # Override traceback mode
pytest tests/test_scraper.py  # Override test path
```

## Common Test Scenarios

### 1. Quick Test Run (Before Commit)

```bash
# Fast check
pytest -x --lf
```

### 2. Full Test Suite

```bash
# Complete test run with coverage
pytest --cov=src --cov-report=html -v
```

### 3. Debug Failing Test

```bash
# Verbose output with debugger
pytest tests/test_scraper.py::TestNavigate::test_navigate_to_url -vv -s --pdb
```

### 4. Integration Tests Only

```bash
# Run integration tests with slower timeout
pytest tests/test_integration.py -v --timeout=60
```

### 5. Continuous Integration

```bash
# Run everything with coverage and XML output
pytest --cov=src --cov-report=xml --cov-report=term -v
```

## Test Structure

### Test Files

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_page.html           # Test HTML page
├── test_scraper.py          # Core functions (9 test classes, 20+ tests)
├── test_parser.py           # Parser API (4 test classes, 15+ tests)
└── test_integration.py      # End-to-end (1 test class, 5+ tests)
```

### Test Classes

Each test file contains multiple test classes:

```python
# test_scraper.py
class TestGetBrowser:        # Browser creation tests
class TestNavigate:          # Navigation tests
class TestElem:              # Element selection tests
class TestInput:             # Form input tests
class TestClick:             # Click interaction tests
class TestGetData:           # Data extraction tests
...

# test_parser.py
class TestRunScraper:        # Main API tests
class TestRunScraperWithCallback:  # Streaming tests
class TestDataPlaceholders:  # Placeholder tests

# test_integration.py
class TestCompleteNewsScrapingScenario:  # Full workflows
```

## Expected Output

### Successful Run

```bash
$ pytest
================================ test session starts =================================
platform darwin -- Python 3.10.0, pytest-8.0.0, pluggy-1.4.0
rootdir: /path/to/stepwright
plugins: asyncio-0.21.0, cov-4.1.0
collected 40 items

tests/test_scraper.py::TestGetBrowser::test_create_browser_instance PASSED    [  2%]
tests/test_scraper.py::TestGetBrowser::test_custom_launch_options PASSED      [  5%]
tests/test_scraper.py::TestNavigate::test_navigate_to_url PASSED              [  7%]
...
tests/test_integration.py::TestCompleteNewsScrapingScenario::test_scrape... PASSED [100%]

================================ 40 passed in 45.23s =================================
```

### With Coverage

```bash
$ pytest --cov=src --cov-report=term-missing
================================ test session starts =================================
...
---------- coverage: platform darwin, python 3.10.0 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/__init__.py            15      0   100%
src/step_types.py          25      0   100%
src/helpers.py             35      2    94%   45-46
src/executor.py           215     18    92%   123, 234-245
src/parser.py              28      1    96%   67
src/scraper.py             85      5    94%   112-115
-----------------------------------------------------
TOTAL                     403     26    94%

================================ 40 passed in 45.23s =================================
```

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError

```bash
# Problem: Can't import stepwright
# Solution: Install in editable mode
pip install -e .
```

#### 2. Playwright Not Installed

```bash
# Problem: Playwright executable not found
# Solution: Install browsers
playwright install chromium
```

#### 3. Async Test Errors

```bash
# Problem: Async tests not running
# Solution: Install pytest-asyncio
pip install pytest-asyncio
```

#### 4. Test Page Not Found

```bash
# Problem: tests/test_page.html not found
# Solution: Ensure you're in project root
cd /path/to/stepwright
pytest
```

#### 5. Import Errors in Tests

```bash
# Problem: Can't import modules in tests
# Solution: Check sys.path manipulation in tests
# tests/conftest.py handles this automatically
```

### Get Help

```bash
# Show pytest help
pytest --help

# Show available fixtures
pytest --fixtures

# Show available markers
pytest --markers

# Version information
pytest --version
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          playwright install chromium
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

1. **Run tests before committing**
   ```bash
   pytest -x --lf
   ```

2. **Check coverage regularly**
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

3. **Use verbose mode for debugging**
   ```bash
   pytest -vv -s
   ```

4. **Test in clean environment periodically**
   ```bash
   python -m venv test_env
   source test_env/bin/activate
   pip install -e ".[dev]"
   pytest
   ```

5. **Write tests for new features**
   - Add tests before implementing features (TDD)
   - Maintain >80% coverage
   - Test both success and failure cases

## Summary

**Basic workflow:**
```bash
# Setup (once)
pip install -e ".[dev]"
playwright install chromium

# Development (repeatedly)
# 1. Make changes
# 2. Run tests
pytest
# 3. Check coverage
pytest --cov=src --cov-report=html
# 4. Fix any failures
# 5. Commit

# Before merging
pytest --cov=src --cov-report=term-missing -v
```

Happy testing! 🧪

