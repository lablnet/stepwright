# Installation

Getting up and running with StepWright takes less than a minute.

## Requirements
- Python 3.8+

## Installing the Package

Install StepWright via pip. This will automatically pull in the core Microsoft Playwright dependency.

```bash
pip install stepwright
```

## Installing Browsers

Since StepWright drives real web browsers under the hood, you need to install the browser binaries provided by Playwright. For most scraping tasks, Chromium is sufficient.

```bash
playwright install chromium
```

> **Note:** If you need to test against Firefox or WebKit, you can run `playwright install` to download all supported browsers.

---

That's it! Let's write [Your First Scraper](./first-scraper).
