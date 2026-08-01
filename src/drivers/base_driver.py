# drivers/base_driver.py
# Abstract Base Class for StepWright Browser Drivers
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseDriver(ABC):
    """
    Abstract Base Class for StepWright Browser Drivers.

    Any custom driver (Playwright, Selenium, Pyppeteer, HTTP/Requests) must
    implement this contract to be pluggable into StepWright workflows.

    @since 2.0.0
    """

    @abstractmethod
    async def launch(self, options: Optional[Dict[str, Any]] = None) -> Any:
        """Launch or initialize the browser instance."""
        pass

    @abstractmethod
    async def new_context(self, options: Optional[Dict[str, Any]] = None) -> Any:
        """Create a new browser context with given context options."""
        pass

    @abstractmethod
    async def new_page(self, context: Any = None) -> Any:
        """Create a new page in the given or default context."""
        pass

    @abstractmethod
    async def close_page(self, page: Any) -> None:
        """Close page instance."""
        pass

    @abstractmethod
    async def close_context(self, context: Any) -> None:
        """Close browser context."""
        pass

    @abstractmethod
    async def close_browser(self, browser: Any = None) -> None:
        """Close browser instance."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown driver singleton / resources."""
        pass

    @abstractmethod
    async def goto(
        self, page: Any, url: str, wait_until: str = "networkidle", timeout: Optional[int] = None
    ) -> None:
        """Navigate page to URL."""
        pass

    @abstractmethod
    async def reload(self, page: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Reload page."""
        pass

    @abstractmethod
    async def get_title(self, page: Any) -> str:
        """Get page title."""
        pass

    @abstractmethod
    async def get_url(self, page: Any) -> str:
        """Get current page URL."""
        pass

    @abstractmethod
    async def wait_for_timeout(self, page: Any, milliseconds: int) -> None:
        """Wait for timeout in milliseconds."""
        pass

    @abstractmethod
    async def wait_for_load_state(
        self, page: Any, state: str = "load", timeout: Optional[int] = None
    ) -> None:
        """Wait for page load state ('load', 'domcontentloaded', 'networkidle')."""
        pass

    @abstractmethod
    async def locator(self, context: Any, selector: str) -> Any:
        """Create locator in page or parent locator context."""
        pass

    @abstractmethod
    async def click(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Click on element/locator."""
        pass

    @abstractmethod
    async def dblclick(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Double click on element/locator."""
        pass

    @abstractmethod
    async def check(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Check checkbox/radio element."""
        pass

    @abstractmethod
    async def fill(self, locator: Any, value: str, options: Optional[Dict[str, Any]] = None) -> None:
        """Fill input field."""
        pass

    @abstractmethod
    async def type(self, locator: Any, text: str, delay: int = 0) -> None:
        """Type text into input field character by character."""
        pass

    @abstractmethod
    async def clear(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Clear input field."""
        pass

    @abstractmethod
    async def hover(self, locator: Any, options: Optional[Dict[str, Any]] = None) -> None:
        """Hover mouse cursor over element."""
        pass

    @abstractmethod
    async def select_option(
        self, locator: Any, values: Union[str, List[str]], options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Select option(s) in select dropdown."""
        pass

    @abstractmethod
    async def drag_to(
        self, source_locator: Any, target_locator: Any, options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Drag source locator onto target locator."""
        pass

    @abstractmethod
    async def set_input_files(
        self, locator: Any, files: Union[str, List[str]], options: Optional[Dict[str, Any]] = None
    ) -> None:
        """Set input file paths."""
        pass

    @abstractmethod
    async def text_content(self, locator: Any) -> Optional[str]:
        """Get text content of locator."""
        pass

    @abstractmethod
    async def inner_html(self, locator: Any) -> str:
        """Get inner HTML of locator."""
        pass

    @abstractmethod
    async def inner_text(self, locator: Any) -> str:
        """Get inner text of locator."""
        pass

    @abstractmethod
    async def input_value(self, locator: Any) -> str:
        """Get input value of locator."""
        pass

    @abstractmethod
    async def get_attribute(self, locator: Any, name: str) -> Optional[str]:
        """Get attribute value of locator."""
        pass

    @abstractmethod
    async def count(self, locator: Any) -> int:
        """Count matching elements for locator."""
        pass

    @abstractmethod
    async def nth(self, locator: Any, index: int) -> Any:
        """Get nth element locator."""
        pass

    @abstractmethod
    async def first(self, locator: Any) -> Any:
        """Get first element locator."""
        pass

    @abstractmethod
    async def scroll_into_view(self, locator: Any) -> None:
        """Scroll element into view."""
        pass

    @abstractmethod
    async def is_visible(self, locator: Any) -> bool:
        """Check if locator element is visible."""
        pass

    @abstractmethod
    async def is_enabled(self, locator: Any) -> bool:
        """Check if locator element is enabled."""
        pass

    @abstractmethod
    async def evaluate(self, context: Any, expression: str, arg: Any = None) -> Any:
        """Evaluate JavaScript expression in page or locator context."""
        pass

    @abstractmethod
    async def screenshot(self, page_or_locator: Any, options: Optional[Dict[str, Any]] = None) -> bytes:
        """Take screenshot of page or locator."""
        pass

    @abstractmethod
    async def wait_for_selector(
        self, context: Any, selector: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Wait for selector in context."""
        pass

    @abstractmethod
    async def frame_locator(self, context: Any, selector: str) -> Any:
        """Create frame locator in context."""
        pass
