# examples/json_template_demo.py
"""
Example demonstrating JSON template export, loading, and execution in StepWright.
"""

import asyncio
from pathlib import Path
from stepwright import (
    TabTemplate,
    BaseStep,
    load_template,
    save_template,
    template_to_json,
    run_scraper,
)


async def main():
    # 1. Define sample local HTML page for demonstration
    sample_html = (Path(__file__).parent / "sample_page.html").resolve()

    # 2. Create a TabTemplate in Python
    template = TabTemplate(
        tab="demo_tab",
        steps=[
            BaseStep(
                id="step_nav",
                action="navigate",
                value=f"file://{sample_html}",
            ),
            BaseStep(
                id="step_title",
                action="data",
                object_type="tag",
                object="h1",
                key="heading",
                data_type="text",
            ),
        ],
    )

    # 3. Export template to a JSON file
    json_path = Path("demo_template.json")
    save_template(template, json_path)
    print(f"✅ Template successfully exported to: {json_path.resolve()}")

    # Print out JSON content
    json_str = template_to_json(template)
    print("\n--- Exported JSON Template ---")
    print(json_str)
    print("------------------------------\n")

    # 4. Load template from JSON file
    loaded_template = load_template(json_path)
    print(f"✅ Loaded template '{loaded_template.tab}' with {len(loaded_template.steps)} step(s).")

    # 5. Execute scraping by passing the JSON file path directly to run_scraper
    print("\n🚀 Executing scraper directly from JSON template file...")
    results = await run_scraper(str(json_path))
    print(f"🎉 Scraping finished! Results: {results}")

    # Clean up generated JSON file
    if json_path.exists():
        json_path.unlink()


if __name__ == "__main__":
    asyncio.run(main())
