"""
Setup script for stepwright package.

For modern installations, use pyproject.toml.
This file exists for backward compatibility.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="stepwright",
    version="0.1.3",
    author="Muhammad Umer Farooq",
    author_email="umer@lablnet.com",
    description="A powerful web scraping library built with Playwright",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lablnet/stepwright",
    project_urls={
        "Bug Tracker": "https://github.com/lablnet/stepwright/issues",
        "Documentation": "https://github.com/lablnet/stepwright#readme",
        "Source Code": "https://github.com/lablnet/stepwright",
    },
    packages=["stepwright"],
    package_dir={"stepwright": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="web scraping playwright automation data-extraction",
    include_package_data=True,
)

