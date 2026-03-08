# Step Actions

The `BaseStep` is an extensive Dataclass governing what the engine should do and how to handle errors.

## Base Properties
```python
@dataclass
class BaseStep:
    id: str             # Unique identifier for the step (optional, but highly recommended)
    action: str         # The instruction type (navigate, data, click, readData)
    key: str = ""       # Dictionary key to store results inside the collector
    description: str = "" # Human-readable description of this step
```

## Element Locators
When targeting specific DOM elements (used for `click`, `data`, `input`).
```python
object_type: str = "css"  # 'id', 'class', 'tag', 'name', 'xpath', 'css'
object: str = ""          # The exact string/selector
fallbackSelectors: list = [] # List of dicts: [{"object_type": "class", "object": "alt"}]
```

## Action Matrix

| Action Name | Description | Required Arguments |
|:------------|:------------|:-------------------|
| `navigate` | Open URL in the active tab | `value="https://..."` |
| `data` | Extract text/attributes | `object_type`, `object`, `key` |
| `input` | Type into a text field | `object_type`, `object`, `value="type this string"` |
| `click` | Basic or complex interaction | `object_type`, `object` |
| `foreach` | Iterate Elements or Arrays | `object` OR `value="{{list_key}}"` + `subSteps=[...]` |
| `readData` | Load seeds from disk | `value="file.csv"`, `data_type="csv"`, `key` |
| `writeData` | Save results to disk | `value="output.json"`, `data_type="json"`, `key` |
| `custom` | Execute Python Closure | `callback=my_func` |
| `evaluate` | Execute JavaScript string | `value="() => window.innerWidth"`, `key` |
| `waitForSelector` | Explicit wait block | `object_type`, `object`, `value="visible"` |
| `screenshot` | Capture element/page | `value="./path.png"` |
| `savePDF` | Generate PDF (Headless only)| `value="./page.pdf"` |
| `uploadFile` | Upload a local file | `object`, `value="/path/file.png"` |
| `dragAndDrop` | Drag elements | `object` (source), `targetObject` (destination) |
| `getUrl` | Current page URL | `key="url"` |
| `getCookies` | Request cookies | `key="cookies"` |

## Error Resilience

```python
retry: int = 0                  # How many times to attempt the action if it fails
retryDelay: int = 1000          # Wait (ms) before retrying
terminateonerror: bool = False  # If True, abort the entire workflow on exception
skipOnError: bool = False       # If True, swallow exceptions gracefully
continueOnEmpty: bool = False   # For Data steps, do not fail if extraction returns empty/None
timeout: int = 30000            # Step-specific timeout in ms 
```

## Assertions & Modifiers

```python
skipIf: str = ""                # JavaScript condition. If true, step resolves immediately.
onlyIf: str = ""                # JavaScript condition. Must evaluate to true to run.
requireVisible: bool = False    # Refuse interaction until element is visually mounted
requireEnabled: bool = False    # Refuse interaction until element is interactable
```

## Click Enhancements

```python
clickModifiers: list = []       # e.g., ["Control", "Shift"]
doubleClick: bool = False       # Trigger double click
forceClick: bool = False        # Bypass actionability checks (hidden elements)
rightClick: bool = False        # Trigger context menu
```

## Input Enhancements

```python
clearBeforeInput: bool = True   # Automatically clear text boxes before typing
inputDelay: int = 0             # Delay between keystrokes in ms (mimic humans)
```

## Data Extraction Options

```python
required: bool = False          # Raise error if data returns None/empty
defaultValue: str = ""          # Provide default if extraction fails
regex: str = ""                 # Regex pattern to run against extracted string
regexGroup: int = 0             # Regex capture group index to return
transform: str = ""             # JS string to evaluate on result: "value.toUpperCase()"
```

## IFrame Handling
```python
frameSelector: str = ""         # The selector string for the iframe
frameSelectorType: str = "css"  # The type of selector for the iframe
```

## Next/Scroll Pagination Hooks
See `PaginationConfig`.
```python
virtualScrollOffset: int = 0    # Pixel increment to scroll
virtualScrollDelay: int = 1000  # Delay between virtual scrolls
virtualScrollUniqueKey: str = ""# ID mapping to dedup elements
virtualScrollLimit: int = 0     # Hard limit on iterations
virtualScrollContainer: str = ""# CSS Selector for overflowing div (if not window)
```
