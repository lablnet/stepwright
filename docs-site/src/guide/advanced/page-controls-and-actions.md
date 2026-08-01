# Page Controls & Additional Actions

StepWright provides fine-grained user interaction and page control step actions (`press`, `type`, `dialog`, `mouseMove`, `waitForNavigation`, `setHeaders`).

---

## ⌨️ 1. Keyboard Key Press (`press`)

Send specific keyboard key events (e.g. `"Enter"`, `"Tab"`, `"Escape"`, `"Control+A"`, `"Backspace"`) directly to focused elements or the page:

```python
BaseStep(
    id="press_enter",
    action="press",
    object="input#search",  # Optional target selector
    value="Enter",           # Key name
)
```

---

## ✍️ 2. Typing with Delay (`type` / `clickAndType`)

Focus inputs, clear pre-existing content (`clearBeforeInput=True`), and type text with human-like character delays (`inputDelay`):

```python
BaseStep(
    id="type_search",
    action="type",
    object="input[name='q']",
    value="declarative web scraping",
    inputDelay=50,  # 50ms pause between keystrokes
)
```

---

## 💬 3. Dialog Auto-Handling (`dialog`)

Automatically accept or dismiss browser alert, confirm, or prompt popups:

```python
BaseStep(
    id="handle_alert",
    action="dialog",
    value="accept",  # "accept" or "dismiss"
    object="Optional prompt text input",
)
```

---

## 🖱️ 4. Mouse Movements (`mouseMove`)

Smoothly move the mouse cursor to a target DOM element (`object`) or specific pixel coordinates (`value="x,y"`):

```python
# Move mouse to element
BaseStep(
    id="hover_menu",
    action="mouseMove",
    object=".nav-dropdown",
)

# Or move to exact coordinates
BaseStep(
    id="move_coords",
    action="mouseMove",
    value="350,450",
)
```

---

## ⏳ 5. Navigation State Wait (`waitForNavigation`)

Explicitly pause execution until a page reaches a specific lifecycle load state (`"networkidle"`, `"domcontentloaded"`, `"load"`) or matches a target URL:

```python
BaseStep(
    id="wait_idle",
    action="waitForNavigation",
    value="networkidle",
)
```

---

## 🔑 6. Dynamic HTTP Headers (`setHeaders`)

Dynamically inject extra HTTP request headers into active browser tabs during step execution:

```python
BaseStep(
    id="set_token",
    action="setHeaders",
    object="Authorization",
    value="Bearer my_session_token",
)
```
