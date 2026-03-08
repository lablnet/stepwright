# What is StepWright?

**StepWright** is a powerful Python library built on top of [Microsoft Playwright](https://playwright.dev/python/) that abstracts away the complexity of raw browser automation scripts. 

Instead of writing imperative `page.locator(...).click()` commands buried deep in loops, StepWright allows you to define **declarative scraping workflows** using dictionaries or Dataclasses.

## Why StepWright?

### The Problem
Traditional web scraping scripts quickly become a monolithic mess of `try/except` blocks, `time.sleep()`, and deeply nested loops when dealing with pagination, infinite scrolls, or robust error handling.

### The Solution
StepWright separates **what** you want to extract from **how** to extract it. By defining your flow as a series of abstract `BaseStep` instructions, the underlying execution engine handles:

- **Automatic Waiting & Retries**: Never write a manual `wait_for_selector` again.
- **Robust Fallbacks**: Provide arrays of selectors (ID, Class, XPath) and let the engine find the element.
- **Complex Navigations**: Built-in handlers for IFrames, Virtual Scrolling, and multi-tab workflows.
- **Performance**: Natively supports parallel execution of scraping scenarios.

## Core Concepts

```mermaid
graph TD
    A([run_scraper]) --> B(TabTemplate)
    B --> C[BaseStep: navigate]
    B --> D[BaseStep: foreach]
    D --> E[BaseStep: data]
    E -.->|Updates| F[((Collector dictionary))]
    F --> G([Final Results Array])
    
    classDef step fill:#3eaf7c,stroke:#fff,stroke-width:2px,color:#fff;
    class C,D,E step;
```

### `TabTemplate`
A sequence of actions executed sequentially in a single Browser Tab. Think of this as one specific "Scraping Job".

### `BaseStep`
The fundamental unit of instruction. A step can represent an action (`click`, `input`, `navigate`), a logic controller (`foreach`), or an extraction command (`data`).

### `Collector`
An internal dictionary automatically managed by StepWright. As `BaseStep`s extract data from the page, the data is pushed into the active collector and aggregated hierarchically.
