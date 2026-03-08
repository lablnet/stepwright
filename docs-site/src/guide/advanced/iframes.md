# Navigating IFrames

Modern web applications frequently embed third-party content (like payment gateways, complex captchas, or external video players) using `<iframe>` elements. 

By default, DOM selectors (like `id` or `css` chains) cannot cross the boundary from the main page into an `iframe`. If you try to extract text from a paragraph inside an iframe using a normal `BaseStep`, the Playwright engine will crash, claiming the element does not exist.

StepWright provides two straightforward parameters—`frameSelector` and `frameSelectorType`—to safely bridge this gap.

---

## Interacting Within an IFrame

If you need to click a button, type into an input field, or extract data that lives inside an embedded frame, you must provide the locator for the `iframe` itself alongside the standard `object` locator.

### Example: Extracting Data

Imagine an embedded article viewer:
```html
<!-- Main Page -->
<div id="container">
    <iframe name="article-viewer" src="...">
        <!-- Inside the IFrame! -->
        <h1 class="title">Hidden Secrets of Web Automaton</h1>
    </iframe>
</div>
```

To extract that `h1.title`:

```python
from stepwright import BaseStep

BaseStep(
    id="extract_iframe_title",
    action="data",
    
    # 1. Target the actual element you want
    object_type="class",
    object="title",
    key="article_title",
    
    # 2. Tell StepWright where the element is housed
    frameSelectorType="name",
    frameSelector="article-viewer"
)
```

StepWright handles the Playwright `page.frame_locator()` context-switching for you behind the scenes.

---

## Deep Actions Inside IFrames

The `frameSelector` logic supports all interactive actions as well, such as filling out an embedded payment or login form.

```python
# Type into an embedded username field
BaseStep(
    id="fill_embedded_login",
    action="input",
    
    object_type="id",
    object="username-input",
    value="admin",
    
    frameSelectorType="css",
    frameSelector="iframe#auth-module"
)
```

### Dealing with Nested IFrames
If the architecture is wildly complex (an iframe inside an iframe), it is often cleaner to write a raw Custom Callback that utilizes native Playwright locators rather than passing deeply chained `frameSelector` strings.

```python
def deep_iframe_interaction(page, collector, step):
    # Native playwright access
    frame = page.frame_locator('#parent').frame_locator('#child')
    text = frame.locator('p.content').text_content()
    collector['deepMsg'] = text

BaseStep(id="nested", action="custom", callback=deep_iframe_interaction)
```
