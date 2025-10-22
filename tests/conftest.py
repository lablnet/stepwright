# conftest.py
# Pytest configuration and shared fixtures
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
import sys
from pathlib import Path

# Add src to path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def test_page_html_path(test_data_dir):
    """Return the path to test HTML page"""
    return test_data_dir / "test_page.html"


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "asyncio: mark test as an async test")
