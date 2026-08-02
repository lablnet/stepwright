# step_types.py
# Type definitions and dataclasses for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Union

# Type aliases
SelectorType = Literal["id", "class", "tag", "xpath"]
DataType = Literal["text", "html", "value", "default", "attribute", "custom"]
ClickModifier = Literal["Control", "Meta", "Shift", "Alt"]


def _serialize_value(val: Any) -> Any:
    """Helper to serialize values to JSON-friendly data structures."""
    if val is None:
        return None
    if hasattr(val, "to_dict"):
        return val.to_dict()
    if isinstance(val, list):
        return [_serialize_value(item) for item in val if item is not None]
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items() if v is not None and not callable(v)}
    if callable(val):
        return None
    return val


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
        "press",
        "type",
        "dialog",
        "mouseMove",
        "waitForNavigation",
        "setHeaders",
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

    # Storage & Pipeline Options
    storage_adapter: Optional[Any] = None  # BaseStorageAdapter or list or string name

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

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for f in fields(self):
            val = getattr(self, f.name)
            if val is not None and not callable(val):
                result[f.name] = _serialize_value(val)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseStep:
        d = dict(data)
        if "subSteps" in d and d["subSteps"] is not None:
            d["subSteps"] = [BaseStep.from_dict(s) if isinstance(s, dict) else s for s in d["subSteps"]]
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in field_names}
        return cls(**filtered)

    def to_json(self, file_path: Optional[Union[str, Path]] = None, indent: int = 2) -> str:
        s = json.dumps(self.to_dict(), indent=indent)
        if file_path:
            Path(file_path).write_text(s, encoding="utf-8")
        return s

    @classmethod
    def from_json(cls, source: Union[str, Path]) -> BaseStep:
        p = Path(source) if isinstance(source, (str, Path)) else None
        if p and p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
        else:
            content = str(source)
        data = json.loads(content)
        return cls.from_dict(data)


@dataclass
class NextButtonConfig:
    """Configuration for next button pagination"""

    object_type: SelectorType
    object: str
    wait: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NextButtonConfig:
        field_names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in field_names})


@dataclass
class ScrollConfig:
    """Configuration for scroll-based pagination"""

    offset: Optional[int] = None
    delay: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScrollConfig:
        field_names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in field_names})


@dataclass
class PaginationConfig:
    """Configuration for pagination strategy"""

    strategy: Literal["next", "scroll"] = "next"
    nextButton: Optional[NextButtonConfig] = None
    scroll: Optional[ScrollConfig] = None
    maxPages: Optional[int] = None
    paginationFirst: Optional[bool] = None
    paginateAllFirst: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {}
        for f in fields(self):
            v = getattr(self, f.name)
            if v is not None:
                res[f.name] = _serialize_value(v)
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PaginationConfig:
        d = dict(data)
        if "nextButton" in d and isinstance(d["nextButton"], dict):
            d["nextButton"] = NextButtonConfig.from_dict(d["nextButton"])
        if "scroll" in d and isinstance(d["scroll"], dict):
            d["scroll"] = ScrollConfig.from_dict(d["scroll"])
        field_names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in field_names})


@dataclass
class ProxyConfig:
    """Configuration for HTTP/SOCKS5 proxy server"""

    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    bypass: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProxyConfig:
        field_names = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in field_names})


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

    # Stealth & Proxy Options
    stealth: bool = False
    proxy: Optional[Union[Dict[str, str], ProxyConfig]] = None
    proxy_pool: Optional[Any] = None  # ProxyPool instance or List of proxies
    proxy_rotation_strategy: Literal["round_robin", "random", "sticky"] = "round_robin"
    proxy_max_failures: int = 3
    proxy_cooldown_seconds: int = 300
    captcha_selector: Optional[str] = None
    on_captcha: Optional[Callable] = None

    # Storage & Pipeline Options
    storage_adapter: Optional[Any] = None  # BaseStorageAdapter or list or string name

    # Driver Architecture
    driver: Optional[Union[str, Any]] = "playwright"

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": "TabTemplate"}
        for f in fields(self):
            val = getattr(self, f.name)
            if val is not None and not callable(val):
                result[f.name] = _serialize_value(val)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TabTemplate:
        d = dict(data)
        d.pop("type", None)
        for key in ("initSteps", "perPageSteps", "steps"):
            if key in d and d[key] is not None:
                d[key] = [BaseStep.from_dict(s) if isinstance(s, dict) else s for s in d[key]]
        if "pagination" in d and isinstance(d["pagination"], dict):
            d["pagination"] = PaginationConfig.from_dict(d["pagination"])
        if "proxy" in d and isinstance(d["proxy"], dict):
            if "server" in d["proxy"]:
                d["proxy"] = ProxyConfig.from_dict(d["proxy"])
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in field_names}
        return cls(**filtered)

    def to_json(self, file_path: Optional[Union[str, Path]] = None, indent: int = 2) -> str:
        s = json.dumps(self.to_dict(), indent=indent)
        if file_path:
            Path(file_path).write_text(s, encoding="utf-8")
        return s

    @classmethod
    def from_json(cls, source: Union[str, Path]) -> TabTemplate:
        p = Path(source) if isinstance(source, (str, Path)) else None
        if p and p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
        else:
            content = str(source)
        data = json.loads(content)
        return cls.from_dict(data)


@dataclass
class ParallelTemplate:
    """Groups multiple templates to run concurrently"""

    templates: List[Union[TabTemplate, "ParallelTemplate", "ParameterizedTemplate"]]
    max_concurrency: Optional[int] = None
    rate_limit_delay_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": "ParallelTemplate"}
        for f in fields(self):
            val = getattr(self, f.name)
            if val is not None and not callable(val):
                result[f.name] = _serialize_value(val)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ParallelTemplate:
        d = dict(data)
        d.pop("type", None)
        if "templates" in d and isinstance(d["templates"], list):
            d["templates"] = [parse_template_from_dict(t) if isinstance(t, dict) else t for t in d["templates"]]
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in field_names}
        return cls(**filtered)

    def to_json(self, file_path: Optional[Union[str, Path]] = None, indent: int = 2) -> str:
        s = json.dumps(self.to_dict(), indent=indent)
        if file_path:
            Path(file_path).write_text(s, encoding="utf-8")
        return s

    @classmethod
    def from_json(cls, source: Union[str, Path]) -> ParallelTemplate:
        p = Path(source) if isinstance(source, (str, Path)) else None
        if p and p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
        else:
            content = str(source)
        data = json.loads(content)
        return cls.from_dict(data)


@dataclass
class ParameterizedTemplate:
    """Generates multiple concurrent tabs from one template using different values"""

    template: TabTemplate
    parameter_key: str  # The key to replace in steps (e.g., 'keyword')
    values: List[Any]  # The values to iterate over
    max_concurrency: Optional[int] = None
    rate_limit_delay_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": "ParameterizedTemplate"}
        for f in fields(self):
            val = getattr(self, f.name)
            if val is not None and not callable(val):
                result[f.name] = _serialize_value(val)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ParameterizedTemplate:
        d = dict(data)
        d.pop("type", None)
        if "template" in d and isinstance(d["template"], dict):
            d["template"] = TabTemplate.from_dict(d["template"])
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in field_names}
        return cls(**filtered)

    def to_json(self, file_path: Optional[Union[str, Path]] = None, indent: int = 2) -> str:
        s = json.dumps(self.to_dict(), indent=indent)
        if file_path:
            Path(file_path).write_text(s, encoding="utf-8")
        return s

    @classmethod
    def from_json(cls, source: Union[str, Path]) -> ParameterizedTemplate:
        p = Path(source) if isinstance(source, (str, Path)) else None
        if p and p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
        else:
            content = str(source)
        data = json.loads(content)
        return cls.from_dict(data)


def parse_template_from_dict(data: Dict[str, Any]) -> Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]:
    """Auto-detect template type from dict and instantiate appropriate template class."""
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data)}")

    t_type = data.get("type")
    if t_type == "TabTemplate":
        return TabTemplate.from_dict(data)
    if t_type == "ParallelTemplate":
        return ParallelTemplate.from_dict(data)
    if t_type == "ParameterizedTemplate":
        return ParameterizedTemplate.from_dict(data)

    if "templates" in data:
        return ParallelTemplate.from_dict(data)
    if "parameter_key" in data and "template" in data:
        return ParameterizedTemplate.from_dict(data)
    if "tab" in data:
        return TabTemplate.from_dict(data)

    raise ValueError(
        "Could not determine template type from dictionary. "
        "Ensure 'type' or 'tab'/'templates'/'parameter_key' field is present."
    )



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

    # Stealth & Proxy Options
    stealth: bool = False
    proxy: Optional[Union[Dict[str, str], ProxyConfig]] = None
    proxy_pool: Optional[Any] = None  # ProxyPool instance or List of proxies
    proxy_rotation_strategy: Literal["round_robin", "random", "sticky"] = "round_robin"
    proxy_max_failures: int = 3
    proxy_cooldown_seconds: int = 300
    captcha_selector: Optional[str] = None
    on_captcha: Optional[Callable] = None

    # Storage & Pipeline Options
    storage_adapter: Optional[Any] = None  # BaseStorageAdapter or list or string name

    # Driver Architecture
    driver: Union[str, Any] = "playwright"




