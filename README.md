<div align="center">
  <img src="https://raw.githubusercontent.com/lablnet/stepwright/main/docs-site/src/public/logo.png" alt="StepWright Logo" width="120" />
</div>

<h1 align="center">StepWright</h1>

<p align="center">
  <strong>A declarative, step-by-step approach to web automation and data extraction with Playwright.</strong>
</p>

<p align="center">
  <a href="https://github.com/lablnet/stepwright/actions">
    <img src="https://github.com/lablnet/stepwright/actions/workflows/tests.yml/badge.svg" alt="Tests" />
  </a>
  <a href="https://codecov.io/gh/lablnet/stepwright">
    <img src="https://codecov.io/gh/lablnet/stepwright/branch/main/graph/badge.svg" alt="Coverage" />
  </a>
  <a href="https://pypi.org/project/stepwright/">
    <img src="https://img.shields.io/pypi/v/stepwright.svg" alt="PyPI version" />
  </a>
</p>

## Overview

StepWright completely abstracts away the complexity of raw browser automation scripts. Instead of writing imperative `page.locator(...).click()` commands buried deep in `try/except` loops, StepWright allows you to define **declarative scraping workflows** using dictionaries or Python Dataclasses.

## 📚 Documentation

We have moved our documentation to a modern, searchable VitePress website to better accommodate Advanced Data Flows, Parallelism strategies, and complex interactions!

👉 **[Read the Official StepWright Documentation](https://stepwright.lablnet.com/)**

## Installation

```bash
pip install stepwright
playwright install chromium
```

## Quick Look

```python
import asyncio
from stepwright import run_scraper, TabTemplate, BaseStep

async def main():
    flow = TabTemplate(
        tab="search",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://news.ycombinator.com"),
            BaseStep(
                id="extract",
                action="foreach",
                object=".athing",
                subSteps=[
                    BaseStep(id="title", action="data", object=".titleline", key="title")
                ]
            )
        ]
    )
    
    results = await run_scraper([flow])
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

<hr/>

*Developed with ❤️ by Muhammad Umer Farooq (@lablnet)*
