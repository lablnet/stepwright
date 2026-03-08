# Pagination & Scrolling

When scraping search results, products, or long articles, data is rarely contained on a single page. StepWright provides built-in mechanisms for automatically navigating multiple pages through `PaginationConfig`, eliminating the need to write complex looping logic in your scripts.

There are two primary strategies for pagination: **Next Button** (traditional clicking) and **Virtual Scroll** (infinite scrolling).

## The `PaginationConfig` Block
Instead of putting your pagination logic in a standard `action` step, attach it to your `TabTemplate`. 

StepWright controls the execution loop based on this logic:
```python
1. Run `initSteps` once.
2. Run `perPageSteps` to scrape the current page.
3. Execute `PaginationConfig` to navigate to the next chunk of data.
4. Repeat Steps 2 and 3 until `maxPages` is reached or the button/scroll limit disappears.
```

---

## Strategy 1: The "Next Button"

This is the standard strategy for classic numbered pages or "Load More" buttons.

### Core Implementation
```python
from stepwright import PaginationConfig, NextButtonConfig

pagination_settings = PaginationConfig(
    strategy="next",                          # Use traditional click navigation
    nextButton=NextButtonConfig(
        object_type="css",           
        object="button.pagination-next",      # The CSS selector for the next button
        wait=1000                             # Wait 1 second after clicking to let the DOM settle
    ),
    maxPages=5,                               # Stop after 5 pages 
    paginationFirst=False                     # If True, clicks Next *before* extracting the first page
)
```

### Fallback Selectors
If your website uses multiple different class names for the Next button depending on the page state, use the `waitForSelector` or `fallbackSelectors` natively inside your config, or use conditional logic within `perPageSteps` if you require manual navigation instead of `PaginationConfig`.

---

## Strategy 2: Virtual/Infinite Scrolling

Modern web applications often automatically load new rows of data dynamically as the user scrolls down the window (e.g., social media feeds or endless product grids).

StepWright has an explicit subset of configurations specifically for infinite scrolling: `ScrollConfig`.

### Core Implementation
```python
from stepwright import PaginationConfig, ScrollConfig

pagination_settings = PaginationConfig(
    strategy="scroll",                        # Tell the engine to scroll, not click
    scroll=ScrollConfig(
        offset=800,                           # Scroll down by exactly 800 pixels each iteration
        delay=1500                            # Give the network 1.5 seconds to fetch new items
    ),
    maxPages=10                               # Scroll 10 times max
)
```

### Scrolling Specific Containers
If the outer `window` itself does not have a scrollbar, but rather an inner `<div id="feed">` is scrolling:

```python
BaseStep(
    id="scroll_feed_div",
    action="virtualScroll",
    virtualScrollContainerType="id",
    virtualScrollContainer="feed",
    virtualScrollOffset=2000,
    virtualScrollDelay=500
)
```
*Note: This specific `virtualScroll` action can be used inside `perPageSteps` instead of relying on the global `PaginationConfig` if your layout requires custom logic (e.g., hovering an element before scrolling).*

---

## Configuration Execution Order (`paginationFirst`)

Sometimes a website lands you on a splash page or requires you to click "Load More" immediately before the first batch of actual data becomes visible.

By default, StepWright extracts the first page, and *then* paginates. You can reverse this by setting `paginationFirst=True`:

```python
pagination = PaginationConfig(
    strategy="next",
    nextButton=NextButtonConfig("class", "load-initial-data"),
    paginationFirst=True 
)
```
If you need to paginate *all* the way to the end of a list to load the entire DOM into memory before doing a massive, single-pass extraction, use `paginateAllFirst=True`.
