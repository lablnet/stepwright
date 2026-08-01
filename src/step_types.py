# step_types.py
# Type definitions and dataclasses for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional, Union

# Type aliases
SelectorType = Literal["id", "class", "tag", "xpath"]
DataType = Literal["text", "html", "value", "default", "attribute", "custom"]
ClickModifier = Literal["Control", "Meta", "Shift", "Alt"]


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
        "reload",
        "getUrl",
        "getTitle",
        "getMeta",
        "getCookies",
        "setCookies",
        "getLocalStorage",
        "setLocalStorage",
        "getSessionStorage",
        "setSessionStorage",
        "getViewportSize",
        "setViewportSize",
        "screenshot",
        "waitForSelector",
        "evaluate",
        "hover",
        "dragAndDrop",
        "select",
        "uploadFile",
        "virtualScroll",
        "readData",
        "writeData",
        "custom",
        "intercept",
    ] = "navigate"
    value: Optional[str] = None
    key: Optional[str] = None
    data_type: Optional[DataType] = None
    wait: Optional[int] = None
    terminateonerror: Optional[bool] = None
    subSteps: Optional[List["BaseStep"]] = None
    autoScroll: Optional[bool] = None
    index_key: Optional[str] = (
        None  # custom index placeholder for loops (e.g., 'j', 'k')
    )
    callback: Optional[Callable] = None  # Generic callback for custom actions/formats

    # IFrame support
    frameSelector: Optional[str] = None
    frameSelectorType: Optional[SelectorType] = None

    # Virtual Scroll settings
    virtualScrollOffset: Optional[int] = None
    virtualScrollDelay: Optional[int] = None
    virtualScrollUniqueKey: Optional[str] = None
    virtualScrollLimit: Optional[int] = None
    virtualScrollContainer: Optional[str] = None
    virtualScrollContainerType: Optional[SelectorType] = None

    # Drag and Drop settings
    targetObject: Optional[str] = None
    targetObjectType: Optional[SelectorType] = None

    # Retry configuration
    retry: Optional[int] = None  # Number of retries on failure (default: 0)
    retryDelay: Optional[int] = None  # Delay between retries in ms (default: 1000)

    # Conditional execution
    skipIf: Optional[str] = (
        None  # JavaScript expression to evaluate - skip step if true
    )
    onlyIf: Optional[str] = (
        None  # JavaScript expression to evaluate - execute only if true
    )

    # Element waiting and state
    waitForSelector: Optional[str] = (
        None  # Wait for selector before action (can be different from object)
    )
    waitForSelectorTimeout: Optional[int] = (
        None  # Timeout for waitForSelector in ms (default: 30000)
    )
    waitForSelectorState: Optional[
        Literal["visible", "hidden", "attached", "detached"]
    ] = None  # State to wait for

    # Multiple selector fallbacks
    fallbackSelectors: Optional[List[Dict[str, str]]] = (
        None  # List of {object_type, object} to try if primary fails
    )

    # Click enhancements
    clickModifiers: Optional[List[ClickModifier]] = (
        None  # Modifier keys for click (Control, Meta, Shift, Alt)
    )
    doubleClick: Optional[bool] = None  # Perform double click instead of single
    forceClick: Optional[bool] = (
        None  # Force click even if element is not visible/actionable
    )
    rightClick: Optional[bool] = None  # Perform right click instead of left

    # Input enhancements
    clearBeforeInput: Optional[bool] = (
        None  # Clear input field before typing (default: True)
    )
    inputDelay: Optional[int] = (
        None  # Delay between keystrokes in ms (for human-like typing)
    )

    # Data extraction enhancements
    required: Optional[bool] = (
        None  # If true, raise error if data extraction returns None/empty
    )
    defaultValue: Optional[str] = (
        None  # Default value if extraction fails or returns None
    )
    regex: Optional[str] = None  # Regex pattern to extract/match from extracted data
    regexGroup: Optional[int] = (
        None  # Regex group to extract (default: 0 for full match)
    )
    transform: Optional[str] = None  # JavaScript expression to transform extracted data

    # Timeout configuration
    timeout: Optional[int] = None  # Step-specific timeout in ms (overrides default)

    # Navigation enhancements
    waitUntil: Optional[
        Literal["load", "domcontentloaded", "networkidle", "commit"]
    ] = None  # For navigate/reload actions

    # Human-like behavior
    randomDelay: Optional[Dict[str, int]] = (
        None  # {min: ms, max: ms} for random delay before action
    )

    # Element state checks before action
    requireVisible: Optional[bool] = (
        None  # Require element to be visible before action (default: True for click)
    )
    requireEnabled: Optional[bool] = None  # Require element to be enabled before action

    # Skip/continue logic
    skipOnError: Optional[bool] = (
        None  # Skip step if error occurs (default: False, opposite of terminateonerror)
    )
    continueOnEmpty: Optional[bool] = (
        None  # Continue execution even if element not found (default: True for some actions)
    )


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


EngineType = Literal["chromium", "firefox", "webkit"]


@dataclass
class TabTemplate:
    """Template for a scraping tab/workflow"""

    tab: str
    initSteps: Optional[List[BaseStep]] = None
    perPageSteps: Optional[List[BaseStep]] = None
    steps: Optional[List[BaseStep]] = None
    pagination: Optional[PaginationConfig] = None

    # Per-template Engine & Emulation Overrides
    engine: Optional[EngineType] = None
    device: Optional[str] = None
    viewport: Optional[Dict[str, int]] = None
    user_agent: Optional[str] = None
    locale: Optional[str] = None
    timezone_id: Optional[str] = None
    geolocation: Optional[Dict[str, float]] = None
    permissions: Optional[List[str]] = None
    is_mobile: Optional[bool] = None
    has_touch: Optional[bool] = None

    # Network & Interception Options
    block_resources: Optional[List[str]] = None
    extra_http_headers: Optional[Dict[str, str]] = None


@dataclass
class ParallelTemplate:
    """Groups multiple templates to run concurrently"""

    templates: List[Union[TabTemplate, "ParallelTemplate", "ParameterizedTemplate"]]
    max_concurrency: Optional[int] = None
    rate_limit_delay_ms: Optional[int] = None


@dataclass
class ParameterizedTemplate:
    """Generates multiple concurrent tabs from one template using different values"""

    template: TabTemplate
    parameter_key: str  # The key to replace in steps (e.g., 'keyword')
    values: List[Any]  # The values to iterate over
    max_concurrency: Optional[int] = None
    rate_limit_delay_ms: Optional[int] = None


@dataclass
class ValidationError:
    """Represents a single validation error in a template or step"""

    path: str
    message: str
    code: str = "INVALID_STEP"


@dataclass
class ValidationResult:
    """Result of template format or data validation"""

    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]


@dataclass
class StepMetric:
    """Execution timing and status metrics for a single step"""

    step_id: str
    action: str
    duration_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class ExecutionMetrics:
    """Aggregated execution metrics for a scraping session"""

    total_duration_ms: float = 0.0
    total_steps_executed: int = 0
    failed_steps_count: int = 0
    step_metrics: List[StepMetric] = None

    def __post_init__(self):
        if self.step_metrics is None:
            self.step_metrics = []


@dataclass
class RunOptions:
    """Options for running the scraper"""

    browser: Optional[dict] = None  # passed to launch options
    onResult: Optional[Any] = None  # Callable[[Dict[str, Any], int], Any]
    debug_on_failure: bool = False  # Pause or print detailed diagnostics on failure
    collect_metrics: bool = False  # Track step execution metrics

    # Engine & Emulation Options
    engine: EngineType = "chromium"
    device: Optional[str] = None
    viewport: Optional[Dict[str, int]] = None
    user_agent: Optional[str] = None
    locale: Optional[str] = None
    timezone_id: Optional[str] = None
    geolocation: Optional[Dict[str, float]] = None
    permissions: Optional[List[str]] = None
    is_mobile: Optional[bool] = None
    has_touch: Optional[bool] = None

    # Concurrency & Rate Limiting
    max_concurrency: Optional[int] = None
    rate_limit_delay_ms: Optional[int] = None

    # Network & Interception Options
    block_resources: Optional[List[str]] = None
    extra_http_headers: Optional[Dict[str, str]] = None



