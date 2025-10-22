# scraper.py
# Port of scraper.ts to Python (async Playwright)
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import asyncio
from typing import Literal, Optional

from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    Page,
    Locator,
)

SelectorType = Literal["id", "class", "tag", "xpath"]

# Internal singleton Playwright manager so get_browser() matches TS ergonomics
_pw: Optional[Playwright] = None


async def get_browser(params: Optional[dict] = None) -> Browser:
    """
    Get the browser (Chromium) instance.

    :param params: Launch options passed to chromium.launch(**params)
    :return: Browser
    """
    global _pw
    if _pw is None:
        _pw = await async_playwright().start()
    launch_params = params or {}
    browser = await _pw.chromium.launch(**launch_params)
    return browser


async def _shutdown_playwright() -> None:
    """Stop the singleton Playwright manager (used by higher-level runners)."""
    global _pw
    if _pw is not None:
        await _pw.stop()
        _pw = None


async def _wait(wait: int) -> None:
    """Wait for the given time in ms."""
    if wait and wait > 0:
        await asyncio.sleep(wait / 1000.0)


async def navigate(page: Page, url: str, wait: int = 0) -> Page:
    """
    Navigate to the given URL and optionally wait N ms.

    :param page: Playwright Page
    :param url: URL to navigate
    :param wait: extra wait in ms
    :return: page
    """
    if not url:
        raise ValueError("Url is required")
    await page.goto(url, wait_until="networkidle")
    if wait > 0:
        await _wait(wait)
    return page


async def elem(page: Page, type: SelectorType, selector: str, wait: int = 0) -> Locator:
    """
    Get Locator by selector type.

    :param page: Page
    :param type: 'id' | 'class' | 'tag' | 'xpath'
    :param selector: selector string
    :param wait: optional wait in ms before returning
    :return: Locator
    """
    if not selector:
        raise ValueError("Selector is required")

    if type == "id":
        element = page.locator(f"#{selector}")
    elif type == "class":
        element = page.locator(f".{selector}")
    elif type == "tag":
        element = page.locator(selector)
    elif type == "xpath":
        element = page.locator(f"xpath={selector}")
    else:
        raise ValueError("Invalid selector type")

    if wait > 0:
        await page.wait_for_timeout(wait)

    # Locator is always returned; Playwright returns a Locator even if not present yet
    return element


async def input(
    page: Page,
    type: SelectorType,
    selector: str,
    value: str,
    wait: int = 0,
) -> Page:
    """
    Type into the given selector.

    :return: page
    """
    element = await elem(page, type, selector, wait)
    await element.type(value)
    return page


async def click(page: Page, type: SelectorType, selector: str) -> Page:
    """
    Click the given selector.

    :return: page
    """
    element = await elem(page, type, selector)
    await element.click()
    return page


async def double_click(page: Page, type: SelectorType, selector: str) -> Page:
    """
    Double click the given selector.

    :return: page
    """
    element = await elem(page, type, selector)
    await element.dblclick()
    return page


async def click_check_box(page: Page, type: SelectorType, selector: str) -> Page:
    """
    Click/check a checkbox.

    :return: page
    """
    element = await elem(page, type, selector)
    await element.check()
    return page


async def get_data(
    page: Page,
    type: SelectorType,
    selector: str,
    data_type: Literal["text", "html", "value", "default", "attribute"] = "default",
    wait: int = 0,
    attribute_name: Optional[str] = None,
) -> str:
    """
    Extract data from the selector.

    Supports attribute extraction from xpath with '/@attr' suffix or via attribute_name arg.

    :return: string value ('' if missing)
    """
    final_selector = selector
    final_attr_name = attribute_name

    if data_type == "attribute":
        # e.g., //div/@href
        import re

        m = re.search(r"/@(\w+)$", selector)
        if m:
            final_attr_name = m.group(1)
            final_selector = re.sub(r"/@\w+$", "", selector)
        if not final_attr_name:
            raise ValueError(
                "Attribute name is required for attribute data type. Use selector like //element/@attribute "
                "or pass attribute_name."
            )

    element = await elem(page, type, final_selector, wait)

    if data_type == "text":
        val = await element.text_content()
        return val or ""
    elif data_type == "html":
        return await element.inner_html()
    elif data_type == "value":
        return await element.input_value()
    elif data_type == "attribute":
        val = await element.get_attribute(final_attr_name)  # type: ignore[arg-type]
        return val or ""
    else:
        # 'default' => inner_text (similar to TS)
        return await element.inner_text()


# Convenience exports mirroring TS
__all__ = [
    "get_browser",
    "navigate",
    "elem",
    "input",
    "click",
    "double_click",
    "click_check_box",
    "get_data",
    "_shutdown_playwright",
]
