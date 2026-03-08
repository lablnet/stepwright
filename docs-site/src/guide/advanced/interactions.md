# Complex Interactions

StepWright provides a variety of actions for handling the "messy" parts of the modern web, such as infinite scrolls and dynamic input fields.

## Infinite Lists via `virtualScroll`

When extracting lists where the DOM unmounts elements as they scroll out of view (virtualized views) or traditional infinite scrolling pages, standard `foreach` loops fail because they can't access missing elements. 

StepWright has `virtualScroll` to progressively scroll, extract data, and automatically deduplicate items.

```python
BaseStep(
    id="collect_virtual_items",
    action="virtualScroll",
    object_type="class",
    object="list-item",
    # Crucial for Deduplication
    virtualScrollUniqueKey="id",       
    virtualScrollLimit=100,             # Max items to collect
    virtualScrollOffset=500,            # Scroll increment in pixels
    virtualScrollDelay=1000,            # Delay in MS after scrolling
    # Container element if scrolling inside a specific div, not window
    virtualScrollContainer=".scroller", 
    virtualScrollContainerType="css",   
    key="items",
    subSteps=[
        BaseStep(id="name", action="data", object_type="tag", object="h3", key="name")
    ]
)
```

## Nesting Data in IFrames
Interacting inside IFrames requires defining the scope in the step definition.
```python
BaseStep(
    id="iframe_action",
    action="click",
    frameSelector="login-iframe",
    frameSelectorType="id",
    object_type="tag",
    object="button"
)
```

## Modifiers and Special Clicks
Simulate human desktop actions.

```python
# Double click
BaseStep(id="double", action="click", doubleClick=True)

# Right click (context menu)
BaseStep(id="right", action="click", rightClick=True)

# Ctrl/Cmd+Click (Open in new tab)
BaseStep(id="multi", action="click", clickModifiers=["Control"])

# Force click hidden elements
BaseStep(id="force", action="click", forceClick=True)
```

## File Uploads
If an input natively accepts files (`type="file"`), you can write to it locally.
```python
BaseStep(
    id="upload", 
    action="click", 
    object="#file-picker", 
    value="/path/to/local/file.png"
)
```

## Drag & Drop
```python
BaseStep(
    id="drag",
    action="click", # 'drag_and_drop' action wrapper
    object="#draggable",        # Source
    targetObject="#droppable",  # Target Box
    targetObjectType="css"
)
```
