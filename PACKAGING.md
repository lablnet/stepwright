# Packaging and Distribution Guide

This guide explains how to build, test, and publish the StepWright package to PyPI.

## Package Structure

```
stepwright/
├── src/                    # Source code (mapped to 'stepwright' package)
│   ├── __init__.py        # Package entry point
│   ├── step_types.py      # Type definitions
│   ├── helpers.py         # Utility functions
│   ├── executor.py        # Execution logic
│   ├── parser.py          # Public API
│   ├── scraper.py         # Browser automation
│   └── scraper_parser.py  # Backward compatibility
├── tests/                 # Test suite
├── pyproject.toml         # Modern package configuration
├── setup.py               # Backward compatible setup
├── MANIFEST.in            # Additional files to include
├── LICENSE                # MIT License
├── README.md              # Main documentation
└── README_TESTS.md        # Test documentation
```

## Development Installation

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/lablnet/stepwright.git
cd stepwright

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### 2. Verify Installation

```bash
# Test import
python -c "import stepwright; print(stepwright.__version__)"

# Run tests
pytest
```

## Building the Package

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info src/*.egg-info
```

### 3. Build Distribution

```bash
# Build both wheel and source distribution
python -m build
```

This creates:
- `dist/stepwright-0.1.1-py3-none-any.whl` (wheel)
- `dist/stepwright-0.1.1.tar.gz` (source distribution)

### 4. Check Distribution

```bash
# Check package contents
twine check dist/*

# List wheel contents
unzip -l dist/stepwright-0.1.0-py3-none-any.whl
```

## Testing the Package

### 1. Test in Clean Environment

```bash
# Create new virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/stepwright-0.1.0-py3-none-any.whl

# Test import and usage
python -c "from stepwright import run_scraper, TabTemplate, BaseStep; print('Success!')"

# Deactivate and remove
deactivate
rm -rf test_env/
```

### 2. Test from Source Distribution

```bash
# Create new environment
python -m venv test_env2
source test_env2/bin/activate

# Install from source
pip install dist/stepwright-0.1.0.tar.gz

# Test
python -c "import stepwright; print(stepwright.__version__)"

# Cleanup
deactivate
rm -rf test_env2/
```

## Publishing to PyPI

### 1. Test on TestPyPI First

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps stepwright

# Test with dependencies
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple stepwright
```

### 2. Publish to PyPI

```bash
# Upload to PyPI (production)
twine upload dist/*

# Or with username/password
twine upload -u __token__ -p pypi-TOKEN dist/*
```

### 3. Verify Installation

```bash
# Install from PyPI
pip install stepwright

# Test
python -c "import stepwright; print(stepwright.__version__)"
```

## Version Management

### Update Version

1. Edit version in `pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

2. Edit version in `setup.py`:
```python
setup(
    version="0.2.0",
    ...
)
```

3. Edit version in `src/__init__.py`:
```python
__version__ = "0.2.0"
```

4. Create git tag:
```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Incompatible API changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

## Pre-release Checklist

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black src/ tests/`)
- [ ] No linting errors (`flake8 src/ tests/`)
- [ ] Documentation is updated (README.md, README_TESTS.md)
- [ ] Version numbers updated (pyproject.toml, setup.py, __init__.py)
- [ ] CHANGELOG.md updated (if exists)
- [ ] Git commit and tag created
- [ ] Package builds without errors (`python -m build`)
- [ ] Package passes checks (`twine check dist/*`)
- [ ] Tested in clean environment
- [ ] Tested on TestPyPI

## PyPI Configuration

### Setup .pypirc

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-TEST-TOKEN
```

Permissions: `chmod 600 ~/.pypirc`

### Get API Tokens

1. **PyPI**: https://pypi.org/manage/account/token/
2. **TestPyPI**: https://test.pypi.org/manage/account/token/

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Check package
        run: twine check dist/*
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add `PYPI_API_TOKEN` to GitHub Secrets.

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Problem: Module not found after installation
# Solution: Check package structure
pip show stepwright
python -c "import stepwright; print(stepwright.__file__)"
```

#### Missing Files in Distribution

```bash
# Problem: Files missing from wheel/sdist
# Solution: Update MANIFEST.in and rebuild
python -m build
unzip -l dist/stepwright-*.whl
```

#### Version Conflicts

```bash
# Problem: Wrong version installed
# Solution: Uninstall and reinstall
pip uninstall stepwright
pip install stepwright --no-cache-dir
```

#### PyPI Upload Errors

```bash
# Problem: File already exists on PyPI
# Solution: Increment version number
# You cannot re-upload the same version

# Problem: Invalid credentials
# Solution: Check API token in ~/.pypirc
twine upload --verbose dist/*
```

## Best Practices

1. **Always test locally first**
   ```bash
   pip install -e .
   pytest
   ```

2. **Test on TestPyPI before production**
   ```bash
   twine upload --repository testpypi dist/*
   ```

3. **Use virtual environments for testing**
   ```bash
   python -m venv clean_env
   ```

4. **Keep dependencies minimal**
   - Only include essential dependencies
   - Document optional dependencies

5. **Version management**
   - Follow semantic versioning
   - Update all version references
   - Create git tags

6. **Documentation**
   - Keep README updated
   - Include examples
   - Document breaking changes

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [twine Documentation](https://twine.readthedocs.io/)

## Support

For packaging questions:
- Open an issue on GitHub
- Email: umer@lablnet.com

