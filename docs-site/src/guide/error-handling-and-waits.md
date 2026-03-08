# Error Handling & Waits

The web is unpredictable. Elements load slowly, A/B tests alter class names, and popups obscure content. StepWright provides declarative configurations to build resilient scrapers.

## Graceful Error Handling

By default, StepWright will swallow exceptions for steps that fail (like a missing element) and continue execution. You can strictly control this behavior:

```python
# Continue if the element doesn't exist (e.g., an optional promo banner)
BaseStep(
    id="optional", 
    action="click", 
    object="maybe-exists",
    terminateonerror=False # This is the default
)

# Stop the ENTIRE scraper if this fails
BaseStep(
    id="critical_login",
    action="click",
    object="submit-auth",
    terminateonerror=True
)
```

## Fallback Selectors

If a site frequently changes its DOM structure, provide `fallbackSelectors`. StepWright will try the primary selector, and if it fails, it will iterate through the fallbacks until it finds a match.

```python
BaseStep(
    id="click_with_fallback",
    action="click",
    object_type="id",
    object="primary-button",
    fallbackSelectors=[
        {"object_type": "class", "object": "btn-primary"},
        {"object_type": "xpath", "object": "//button[contains(text(), 'Submit')]"}
    ]
)
```

## Retries and Explicit Waits

Sometimes you just need to wait a bit longer or retry an interaction that got interrupted by a layout shift.

```python
# Retry logic
BaseStep(
    id="flaky_button",
    action="click",
    object="submit",
    retry=3,            # Attempt the click up to 3 times
    retryDelay=1000     # Wait 1000ms between attempts
)

# Explicit Wait AFTER an action executes
BaseStep(
    id="load",
    action="click",
    object="load-more",
    wait=2000           # Unconditionally pause for 2 seconds after clicking
)
```

## Smart Element Validation

Ensure elements are fully mounted and active before interacting to prevent race conditions.

```python
BaseStep(
    id="click_visible",
    action="click",
    requireVisible=True,
    requireEnabled=True
)
```
