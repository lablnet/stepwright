# Your First Scraper

Let's build a simple scraper to extract quotes from `quotes.toscrape.com`.

Create a file named `my_scraper.py` and add the following code:

```python
import asyncio
from stepwright import run_scraper, TabTemplate, BaseStep

async def main():
    # 1. Define your scraping workflow
    templates = [
        TabTemplate(
            tab="quotes",
            steps=[
                # Navigate to website
                BaseStep(
                    id="navigate",
                    action="navigate",
                    value="https://quotes.toscrape.com"
                ),
                
                # Extract quotes using a foreach loop
                BaseStep(
                    id="extract_quotes",
                    action="foreach",
                    object_type="class",
                    object="quote",
                    subSteps=[
                        BaseStep(
                            id="get_text",
                            action="data",
                            object_type="class",
                            object="text",
                            key="quote_text",
                            data_type="text"
                        ),
                        BaseStep(
                            id="get_author",
                            action="data",
                            object_type="class",
                            object="author",
                            key="author",
                            data_type="text"
                        )
                    ]
                )
            ]
        )
    ]
    
    # 2. Run the engine
    results = await run_scraper(templates)
    
    # 3. Print results (automatically aggregated!)
    for i, quote in enumerate(results, 1):
        print(f"{i}. \"{quote['quote_text']}\" - {quote['author']}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run the script from your terminal:

```bash
python my_scraper.py
```

## Understanding the Code

1. **`TabTemplate`**: We define a single "Tab" meaning this entire sequence will run inside one browser page.
2. **`navigate` action**: Instructs the browser to go to the URL. Remember, StepWright handles the `networkidle` waits for you.
3. **`foreach` action**: We tell StepWright to find every element with the class `quote` and loop over them.
4. **`data` action**: Inside the loop, we extract the inner text of the `.text` and `.author` elements, assigning them dictionary keys `quote_text` and `author`.

Notice how you didn't have to write any manual browser launching code, wait commands, or empty array initializations!
