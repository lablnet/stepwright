# Validation & Debugging

StepWright provides built-in tools for static template format validation, data output verification, diagnostic debugging on failure, and step-level execution metrics tracking.

---

## 🔍 1. Template Format Validation (`validate_template_format`)

Before launching a browser session, you can statically validate your templates to catch syntax errors, missing mandatory parameters, or invalid action types early in your pipeline:

```python
from stepwright import TabTemplate, BaseStep, validate_template_format

template = TabTemplate(
    tab="search_products",
    steps=[
        BaseStep(id="nav", action="navigate", value="https://example.com"),
        BaseStep(id="search_box", action="input", object="#search"),
        BaseStep(id="submit", action="click", object="#search-btn"),
    ]
)

result = validate_template_format(template)

if not result.is_valid:
    print("❌ Template contains errors:")
    for err in result.errors:
        print(f"  - [{err.code}] {err.path}: {err.message}")
else:
    print("✅ Template format is valid!")
```

### What `validate_template_format` Checks
- **Action validity**: Ensures `step.action` is a recognized action type.
- **Required parameters**: Verifies mandatory fields for specific actions (e.g., `navigate` requires `value`, `input` requires `object`, `foreach` requires `subSteps`).
- **Selector types**: Validates `object_type` values (`id`, `class`, `tag`, `xpath`).
- **Nested structures**: Recursively inspects `initSteps`, `perPageSteps`, `subSteps`, `ParallelTemplate`, and `ParameterizedTemplate`.

---

## 📊 2. Expected Data Validation (`validate_template_data`)

Verify that your template flow extracts all required data keys into the results collector before executing the scraping workflow:

```python
from stepwright import validate_template_data

expected_output_keys = ["product_name", "price", "rating", "sku"]

result = validate_template_data(template, expected_output_keys)

if not result.is_valid:
    print("⚠️  Missing expected data keys in template:")
    for err in result.errors:
        print(f"  - {err.path}: {err.message}")
```

---

## 🐛 3. Debugging on Step Failure (`debug_on_failure`)

When developing or troubleshooting complex scraping flows, enable `debug_on_failure` in `RunOptions`. If a step fails, StepWright will print detailed diagnostic information including the active step ID, action type, target selector, value, current page URL, and failure error trace.

```python
from stepwright import run_scraper, RunOptions

options = RunOptions(
    debug_on_failure=True,
    browser={"headless": False}  # optional: run headed while debugging
)

results = await run_scraper([template], options)
```

---

## ⏱️ 4. Execution Metrics & Performance Tracking (`run_scraper_with_metrics`)

To monitor execution timing, step performance, and error counts across your workflows, enable `collect_metrics` or use `run_scraper_with_metrics`:

```python
from stepwright import run_scraper_with_metrics, RunOptions

options = RunOptions(collect_metrics=True)

results, metrics = await run_scraper_with_metrics([template], options)

print(f"⏱️  Total Duration: {metrics.total_duration_ms:.2f} ms")
print(f"📝 Steps Executed: {metrics.total_steps_executed}")
print(f"❌ Failed Steps: {metrics.failed_steps_count}")

for step_m in metrics.step_metrics:
    print(f"  - Step `{step_m.step_id}` ({step_m.action}): {step_m.duration_ms:.2f} ms [Success: {step_m.success}]")
```
