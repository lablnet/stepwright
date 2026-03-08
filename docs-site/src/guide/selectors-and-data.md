# Selectors & Data

StepWright supports a variety of ways to target DOM elements and extract specific types of data.

## Selector Types

When defining a `BaseStep` that interacts with the DOM (`click`, `input`, `data`), you generally provide an `object_type` and an `object` (the string signature).

```python
# By ID
BaseStep(object_type="id", object="my-id", action="click")

# By Class
BaseStep(object_type="class", object="my-class", action="click")

# By Tag
BaseStep(object_type="tag", object="h1", action="click")

# By XPath (Very powerful for complex DOM traversal)
BaseStep(object_type="xpath", object="//div[@class='content']", action="click")

# By general CSS Selector (Recommended for advanced users)
BaseStep(object_type="css", object="div.container > ul > li:nth-child(2)", action="click")
```

## Data Types

When using the `action="data"`, you can specify what part of the element you want to extract using `data_type`.

```python
# 1. Inner text content (Default)
BaseStep(action="data", data_type="text", key="title")    

# 2. Raw HTML content
BaseStep(action="data", data_type="html", key="html_blob")    

# 3. Form input values (e.g. from an <input> tag)
BaseStep(action="data", data_type="value", key="search_term")   

# 4. Element Attributes
BaseStep(
    action="data", 
    data_type="attribute", 
    value="href", # Specific attribute to extract 
    key="link_url"
)
```
