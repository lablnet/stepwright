# Contributing to StepWright

Thank you for your interest in contributing to StepWright! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Setting Up Development Environment

1. **Fork and Clone**

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/stepwright.git
cd stepwright
```

2. **Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. **Install in Development Mode**

```bash
# Install package with development dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

4. **Verify Installation**

```bash
# Run tests to verify everything works
pytest
```

## Development Workflow

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bugfix branch
git checkout -b fix/your-bugfix-name
```

### 2. Make Changes

- Write clean, readable code
- Follow Python conventions (PEP 8)
- Add docstrings to functions and classes
- Keep functions focused and small

### 3. Write Tests

- Add tests for new functionality
- Ensure existing tests still pass
- Aim for high test coverage

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### 4. Format and Lint

```bash
# Format code with black
black src/ tests/

# Check linting with flake8
flake8 src/ tests/

# Type checking (optional)
mypy src/
```

### 5. Commit Changes

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of feature"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Add detailed description after blank line if needed

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable names

### Example

```python
from typing import Optional, List, Dict, Any
from playwright.async_api import Page


async def extract_data(
    page: Page,
    selector: str,
    data_type: str = "text"
) -> Optional[str]:
    """
    Extract data from a page element.
    
    Args:
        page: Playwright page instance
        selector: CSS selector for the element
        data_type: Type of data to extract (text, html, value)
        
    Returns:
        Extracted data as string, or None if not found
    """
    try:
        element = page.locator(selector)
        if await element.count() == 0:
            return None
            
        if data_type == "text":
            return await element.text_content()
        elif data_type == "html":
            return await element.inner_html()
        else:
            return await element.input_value()
            
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None
```

## Testing

### Test Organization

Tests are organized by functionality:

- `test_scraper.py` - Core scraper functions
- `test_parser.py` - Parser and high-level API
- `test_integration.py` - End-to-end integration tests

### Writing Tests

```python
import pytest
from stepwright import run_scraper, TabTemplate, BaseStep


class TestMyFeature:
    """Tests for my new feature"""

    @pytest.mark.asyncio
    async def test_feature_works(self, test_page_url):
        """Should successfully execute my feature"""
        # Arrange
        templates = [
            TabTemplate(
                tab="test",
                steps=[
                    BaseStep(
                        id="test_step",
                        action="navigate",
                        value=test_page_url
                    )
                ]
            )
        ]
        
        # Act
        results = await run_scraper(templates)
        
        # Assert
        assert len(results) == 1
        assert "expected_key" in results[0]
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scraper.py

# Run specific test
pytest tests/test_scraper.py::TestNavigate::test_navigate_to_url

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # On Mac
xdg-open htmlcov/index.html  # On Linux
start htmlcov/index.html  # On Windows
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Detailed description if needed. Can span multiple lines
    and include examples.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this error occurs
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### Updating README

If your changes affect the public API or add new features:

1. Update `README.md` with examples
2. Update `README_TESTS.md` if adding tests
3. Add docstrings to new functions/classes

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted with black
- [ ] No linting errors
- [ ] Added tests for new functionality
- [ ] Updated documentation
- [ ] Commit messages are clear

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- List of specific changes

## Testing
- Description of testing performed

## Checklist
- [ ] Tests pass
- [ ] Code is formatted
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. Maintainer will review your PR
2. Address any requested changes
3. Once approved, PR will be merged

## Reporting Bugs

### Before Reporting

- Check existing issues
- Try latest version
- Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Step one
2. Step two
3. See error

**Expected behavior**
What you expected to happen

**Code example**
```python
# Minimal code to reproduce
```

**Environment**
- OS: [e.g. Ubuntu 22.04]
- Python version: [e.g. 3.10]
- StepWright version: [e.g. 0.1.0]
- Playwright version: [e.g. 1.40.0]

**Additional context**
Any other relevant information
```

## Feature Requests

We welcome feature requests! Please:

1. Check if feature already requested
2. Describe use case clearly
3. Provide examples if possible
4. Explain why feature would be useful

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Publishing others' private information
- Other unprofessional conduct

## Questions?

- Open an issue for questions
- Join discussions on GitHub
- Email: umer@lablnet.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- Release notes
- Contributors section
- Project documentation

Thank you for contributing to StepWright! 🎉
