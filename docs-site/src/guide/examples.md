# Examples & Use Cases

StepWright was built to tackle real-world scraping scenarios. We maintain a collection of ready-to-run examples in the root of the StepWright GitHub repository.

You can browse the raw source code for all examples here:  
**[👉 StepWright / examples Directory](https://github.com/lablnet/stepwright/tree/main/examples)**

---

## 🚀 Basic Example
**File:** [`basic_example.py`](https://github.com/lablnet/stepwright/blob/main/examples/basic_example.py)

A straightforward introduction to sequential scraping. It demonstrates how to set up a `TabTemplate`, use standard `navigate`, `input`, and `click` actions, and easily extract data targets from a single product page into the central collector.

## 🔁 Pagination & Nested Loops
**File:** [`nested_loops.py`](https://github.com/lablnet/stepwright/blob/main/examples/nested_loops.py)

Shows how to handle multi-page navigation architectures. It uses `PaginationConfig` combined with nested `foreach` block lists to dig deep into multi-tiered website layouts (e.g., Categories -> Items -> Inner Details).

## ⚡ Parallel Search Engine Showcase
**File:** [`parallel_scraping_showcase.py`](https://github.com/lablnet/stepwright/blob/main/examples/parallel_scraping_showcase.py)

The ultimate example of high-performance concurrent scraping. It utilizes `ParameterizedTemplate` to instantly launch 5 parallel tabs, simultaneously searching completely different keywords on Wikipedia, extracting the results, and merging them all flawlessly.

## 🗄️ Custom Data Pipeline Flows
**File:** [`custom_data_flow.py`](https://github.com/lablnet/stepwright/blob/main/examples/custom_data_flow.py)

Demonstrates the data-engineering aspect of StepWright 1.1.0. This script reads an input `.csv` file directly from disk using `readData`, iterates over its contents directly in the StepWright workflow, processes HTML, and exports via `writeData` straight back to a `.json` dump.

## 🖱️ Advanced Element Interactions
**File:** [`advanced_interactions.py`](https://github.com/lablnet/stepwright/blob/main/examples/advanced_interactions.py)

A deep dive into complex UI mechanics. Demonstrates double clicks, drag-and-drop operations, hover states, clearing text inputs, intercepting downloads, manipulating IFrames, and taking targeted element screenshots.

## 🛠️ Complete Complex Workflow
**File:** [`advanced_example.py`](https://github.com/lablnet/stepwright/blob/main/examples/advanced_example.py)

A kitchen-sink example demonstrating nearly everything tying together: multiple templates, custom Python step closures, complex fallback selectors, conditional logic (`skipIf`), dynamic JavaScript evaluation, and detailed console metrics.
