# step_types.py
# Type definitions and dataclasses for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Literal, Optional

# Type aliases
SelectorType = Literal["id", "class", "tag", "xpath"]
DataType = Literal["text", "html", "value", "default", "attribute"]


@dataclass
class BaseStep:
    """Represents a single scraping step/action"""

    id: str
    description: Optional[str] = None
    object_type: Optional[SelectorType] = None
    object: Optional[str] = None
    action: Literal[
        "navigate",
        "input",
        "click",
        "data",
        "scroll",
        "eventBaseDownload",
        "foreach",
        "open",
        "savePDF",
        "printToPDF",
        "downloadPDF",
        "downloadFile",
    ] = "navigate"
    value: Optional[str] = None
    key: Optional[str] = None
    data_type: Optional[DataType] = None
    wait: Optional[int] = None
    terminateonerror: Optional[bool] = None
    subSteps: Optional[List["BaseStep"]] = None
    autoScroll: Optional[bool] = None


@dataclass
class NextButtonConfig:
    """Configuration for next button pagination"""

    object_type: SelectorType
    object: str
    wait: Optional[int] = None


@dataclass
class ScrollConfig:
    """Configuration for scroll-based pagination"""

    offset: Optional[int] = None
    delay: Optional[int] = None


@dataclass
class PaginationConfig:
    """Configuration for pagination strategy"""

    strategy: Literal["next", "scroll"] = "next"
    nextButton: Optional[NextButtonConfig] = None
    scroll: Optional[ScrollConfig] = None
    maxPages: Optional[int] = None
    paginationFirst: Optional[bool] = None
    paginateAllFirst: Optional[bool] = None


@dataclass
class TabTemplate:
    """Template for a scraping tab/workflow"""

    tab: str
    initSteps: Optional[List[BaseStep]] = None
    perPageSteps: Optional[List[BaseStep]] = None
    steps: Optional[List[BaseStep]] = None
    pagination: Optional[PaginationConfig] = None


@dataclass
class RunOptions:
    """Options for running the scraper"""

    browser: Optional[dict] = None  # passed to chromium.launch
    onResult: Optional[Any] = None  # Callable[[Dict[str, Any], int], Any]
