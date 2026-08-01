# drivers/playwright_driver.py
# Playwright concrete driver implementation for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Union

from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
    Locator,
    FrameLocator,
)

from .base_driver import BaseDriver


class PlaywrightDriver(BaseDriver):
    """
    Default Playwright Driver implementation for StepWright.

    @since 2.0.0
    """

    def __init__(self) -> None:
        self._pw: Optional[Playwright] = None
        self._pw_loop: Optional[asyncio.AbstractEventLoop] = None
        self._browser: Optional[Browser] = None

    async def _get_pw(self) -> Playwright:
        """Get or initialize the Playwright manager instance for current event loop."""
        current_loop = asyncio.get_running_loop()
        if self._pw is not None and (self._pw_loop != current_loop or self._pw_loop.is_closed()):
            try:
                await self._pw.stop()
            except Exception:
                pass
            self._pw = None

        if self._pw is None:
            self._pw = await async_playwright().start()
            self._pw_loop = current_loop
        return self._pw

    async def launch(self, options: Optional[Dict[str, Any]] = None) -> Browser:
        pw = await self._get_pw()
        opts = options.copy() if options else {}
        engine = (opts.pop("engine", "chromium") or "chromium").lower()

        if engine == "firefox":
            self._browser = await pw.firefox.launch(**opts)
        elif engine == "webkit":
            self._browser = await pw.webkit.launch(**opts)
        else:
            self._browser = await pw.chromium.launch(**opts)
        return self._browser

    async def new_context(self, options: Optional[Dict[str, Any]] = None) -> BrowserContext:
        if self._browser is None:
            await self.launch()
        opts = options or {}
        return await self._browser.new_context(**opts)

    async def new_page(self, context: Any = None) -> Page:
        if context is None:
            context = await self.new_context()
        return await context.new_page()

    async def close_page(self, page: Any) -> None:
        if page:
            await page.close()

    async def close_context(self, context: Any) -> None:
        if context:
            await context.close()

    async def close_browser(self, browser: Any = None) -> None:
        target = browser or self._browser
        if target:
            await target.close()
            if target == self._browser:
                self._browser = None

    async def shutdown(self) -> None:
        await self.close_browser()
        if self._pw is not None:
            try:
                await self._pw.stop()
            except Exception:
                pass
            self._pw = None
            self._pw_loop = None

    async def goto(
        self, page: Any, url: str, wait_until: str = "networkidle", timeout: Optional[int] = None
    ) -> None:
        if not url:
            raise ValueError("Url is required")
        opts: Dict[str, Any] = {"wait_until": wait_until}
        if timeout is not None:
            opts["timeout"] = timeout
        await page.goto(url, **opts)

    async def reload(self, page: Any, options: Optional[Dict[str, Any]] = None) -> None:
        opts = options or {}
        await page.reload(**opts)

    async def get_title(self, page: Any) -> str:
        return await page.title()

    async def get_url(self, page: Any) -> str:
        return page.url

    async def wait_for_timeout(self, page: Any, milliseconds: int) -> None:
        await page.wait_for_timeout(milliseconds)

    async def wait_for_load_state(
        self, page: Any, state: str = "load", timeout: Optional[int] = None
    ) -> None:
        opts: Dict[str, Any] = {}
        if timeout is not None:
            opts["timeout"] = timeout
        await page.wait_for_load_state(state, **opts)

    async def locator(self, context: Any, selector: str) -> Locator:
        return context.locator(selector)

    async def click(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        opts = options or {}
        await locator.click(**opts)

    async def dblclick(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        opts = options or {}
        await locator.dblclick(**opts)

    async def check(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        opts = options or {}
        await locator.check(**opts)

    async def fill(self, locator: Any, value: str, options: Optional[Dict[str, Any]] = None) -> None:
        opts = options or {}
        await locator.fill(value, **opts)

    async def type(self, locator: Any, text: str, delay: int = 0) -> None:
        await locator.type(text, delay=delay)

    async def clear(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        await locator.fill("")

    async def hover(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        opts = options or {}
        await locator.hover(**opts)

    async def select_option(
        self, locator: Any, values: Union[str, List[str]], options: Optional[Dict[str, Any]] = None
    ) -> None:
        opts = options or {}
        await locator.select_option(values, **opts)

    async def drag_to(
        self, source_locator: Any, target_locator: Any, options: Optional[Dict[str, Any]] = None
    ) -> None:
        opts = options or {}
        await source_locator.drag_to(target_locator, **opts)

    async def set_input_files(
        self, locator: Any, files: Union[str, List[str]], options: Optional[Dict[str, Any]] = None
    ) -> None:
        opts = options or {}
        await locator.set_input_files(files, **opts)

    async def text_content(self, locator: Any) -> Optional[str]:
        return await locator.text_content()

    async def inner_html(self, locator: Any) -> str:
        return await locator.inner_html()

    async def inner_text(self, locator: Any) -> str:
        return await locator.inner_text()

    async def input_value(self, locator: Any) -> str:
        return await locator.input_value()

    async def get_attribute(self, locator: Any, name: str) -> Optional[str]:
        return await locator.get_attribute(name)

    async def count(self, locator: Any) -> int:
        return await locator.count()

    async def nth(self, locator: Any, index: int) -> Locator:
        return locator.nth(index)

    async def first(self, locator: Any) -> Locator:
        return locator.first

    async def scroll_into_view(self, locator: Any) -> None:
        await locator.scroll_into_view_if_needed()

    async def is_visible(self, locator: Any) -> bool:
        return await locator.is_visible()

    async def is_enabled(self, locator: Any) -> bool:
        return await locator.is_enabled()

    async def evaluate(self, context: Any, expression: str, arg: Any = None) -> Any:
        if arg is not None:
            return await context.evaluate(expression, arg)
        return await context.evaluate(expression)

    async def screenshot(self, page_or_locator: Any, options: Optional[Dict[str, Any]] = None) -> bytes:
        opts = options or {}
        return await page_or_locator.screenshot(**opts)

    async def wait_for_selector(
        self, context: Any, selector: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        opts = options or {}
        return await context.wait_for_selector(selector, **opts)

    async def frame_locator(self, context: Any, selector: str) -> FrameLocator:
        return context.frame_locator(selector)
