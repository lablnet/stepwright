# parser.py
# Public API for StepWright scraper
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .step_types import TabTemplate, RunOptions
from .executor import execute_tab
from .scraper import get_browser, _shutdown_playwright


async def run_scraper(
    templates: List[TabTemplate],
    options: Optional[RunOptions] = None,
) -> List[Dict[str, Any]]:
    """
    Execute a scraping template and return the gathered data.

    Args:
        templates: List of tab templates to execute
        options: Optional configuration for browser and callbacks

    Returns:
        List of collected data dictionaries
    """
    options = options or RunOptions()
    browser = await get_browser((options.browser or {"headless": True}))
    context = await browser.new_context()

    all_results: List[Dict[str, Any]] = []
    try:
        for tmpl in templates:
            page = await context.new_page()
            try:
                tab_results = await execute_tab(page, tmpl, options.onResult)
                all_results.extend(tab_results)
            finally:
                await page.close()
    finally:
        await context.close()
        await browser.close()
        await _shutdown_playwright()

    return all_results


async def run_scraper_with_callback(
    templates: List[TabTemplate],
    on_result: Callable[[Dict[str, Any], int], Any],
    options: Optional[RunOptions] = None,
) -> None:
    """
    Execute a scraping template with streaming results via callback for each result.

    Args:
        templates: List of tab templates to execute
        on_result: Callback function called for each result
        options: Optional configuration for browser
    """
    options = options or RunOptions()
    options.onResult = on_result

    browser = await get_browser((options.browser or {"headless": True}))
    context = await browser.new_context()

    try:
        for tmpl in templates:
            page = await context.new_page()
            try:
                await execute_tab(page, tmpl, options.onResult)
            finally:
                await page.close()
    finally:
        await context.close()
        await browser.close()
        await _shutdown_playwright()
