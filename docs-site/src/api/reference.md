# API Reference Overview

Welcome to the StepWright API Reference. Here you'll find detailed parameter specifications for the core classes.

## Core Engines

StepWright primarily operates around a single function:
```python
async def run_scraper(
    templates: List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]], 
    options: RunOptions = RunOptions()
) -> List[Dict[str, Any]]: ...
```

To stream results in real-time before the entire browser session closes, use the callback variant:
```python
async def run_scraper_with_callback(
    templates: List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    on_result: Callable[[Dict[str, Any], int], Any],
    options: RunOptions = RunOptions()
) -> None: ...
```

To collect execution metrics and timing stats alongside the scraped data:
```python
async def run_scraper_with_metrics(
    templates: List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    options: RunOptions = RunOptions()
) -> Tuple[List[Dict[str, Any]], ExecutionMetrics]: ...
```

## Validation APIs

Validate template syntax, step configuration, and expected data output structure without starting a browser instance:

```python
def validate_template_format(
    templates: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate, List[...]]
) -> ValidationResult: ...

def validate_template_data(
    templates: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate, List[...]],
    expected_keys: List[str]
) -> ValidationResult: ...
```

## `RunOptions`
Global configuration applied to the Playwright browser and scraping session.
```python
@dataclass
class RunOptions:
    browser: Dict[str, Any] = field(default_factory=lambda: {"headless": True})
    onResult: Optional[Callable[[Dict[str, Any], int], Any]] = None
    debug_on_failure: bool = False  # Print detailed diagnostic log on step error
    collect_metrics: bool = False   # Track execution timing & step metrics
```

## Validation & Metrics Data Classes

```python
@dataclass
class ValidationError:
    path: str
    message: str
    code: str = "INVALID_STEP"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]

@dataclass
class StepMetric:
    step_id: str
    action: str
    duration_ms: float
    success: bool
    error: Optional[str] = None

@dataclass
class ExecutionMetrics:
    total_duration_ms: float = 0.0
    total_steps_executed: int = 0
    failed_steps_count: int = 0
    step_metrics: List[StepMetric] = field(default_factory=list)
```

## `TabTemplate`
The container for a sequential workflow running in a single browser context.
```python
@dataclass
class TabTemplate:
    tab: str                                 # Name identifier for this template
    steps: List['BaseStep']                  # Default sequential steps
    initSteps: Optional[List['BaseStep']]    # Steps pushed before pagination
    perPageSteps: Optional[List['BaseStep']] # Steps extracted per paginated loop
    pagination: Optional['PaginationConfig'] # Config for navigating subsequent pages
```

## `ParallelTemplate`
A wrapper that takes a generic list of templates and triggers them to run concurrently, each in their own Playwright `page` but sharing the same Browser profile.
```python
@dataclass
class ParallelTemplate:
    templates: List[Union['TabTemplate', 'ParameterizedTemplate']]
```

## `ParameterizedTemplate`
An expansion template. It clones the base `TabTemplate` for every entry in `values`, replacing placeholder syntax `{{parameter_key}}` before wrapping them in a concurrent `asyncio.gather` batch.
```python
@dataclass
class ParameterizedTemplate:
    template: 'TabTemplate'
    parameter_key: str
    values: List[str]
```

## `PaginationConfig`
How to handle paginated results correctly. If configured, StepWright will execute `perPageSteps`, click/scroll the `PaginationConfig`, and repeat until `maxPages` is reached.

```python
@dataclass
class PaginationConfig:
    strategy: Literal["next", "scroll"] = "next"
    nextButton: Optional[NextButtonConfig] = None
    scroll: Optional[ScrollConfig] = None
    maxPages: Optional[int] = None
    paginationFirst: Optional[bool] = None  # True: Paginate -> Extract
    paginateAllFirst: Optional[bool] = None # True: Paginate completely to end -> Then extract
```

## `NextButtonConfig`
Configuration for traditional "Next Page" button pagination.

```python
@dataclass
class NextButtonConfig:
    object_type: Literal["id", "class", "tag", "xpath", "css"]
    object: str
    wait: Optional[int] = None
```

## `ScrollConfig`
Configuration for standard scroll-to-bottom pagination loading.

```python
@dataclass
class ScrollConfig:
    offset: Optional[int] = None
    delay: Optional[int] = None
```
