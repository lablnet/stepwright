# examples/page_controls_and_actions.py
# Example demonstrating Page Controls & Additional Actions (press, type, dialog, mouseMove, waitForNavigation, setHeaders)

import asyncio
from pathlib import Path
from stepwright import (
    run_scraper,
    TabTemplate,
    BaseStep,
    RunOptions,
    validate_template_format,
)


async def main():
    # Path to local sample HTML file
    sample_html = Path(__file__).parent / "sample_page.html"
    file_url = f"file://{sample_html.resolve()}"

    template = TabTemplate(
        tab="page_controls_demo",
        steps=[
            # 1. Register alert dialog auto-accept handler
            BaseStep(
                id="setup_dialog",
                action="dialog",
                value="accept",
            ),
            # 2. Dynamically set extra HTTP headers
            BaseStep(
                id="set_headers",
                action="setHeaders",
                object="X-Client-App",
                value="StepWright/1.6.0",
            ),
            # 3. Navigate to local sample page
            BaseStep(
                id="nav",
                action="navigate",
                value=file_url,
            ),
            # 4. Smooth mouse move to input field
            BaseStep(
                id="mouse_move",
                action="mouseMove",
                object="#search",
            ),
            # 5. Type text with character delay (30ms)
            BaseStep(
                id="type_search",
                action="type",
                object="#search",
                value="StepWright Automation Engine",
                inputDelay=30,
            ),
            # 6. Press Enter key on input field
            BaseStep(
                id="press_enter",
                action="press",
                object="#search",
                value="Enter",
            ),
            # 7. Click button to trigger alert dialog
            BaseStep(
                id="click_alert_btn",
                action="click",
                object="#alert-btn",
            ),
            # 8. Extract heading & paragraph text into collector
            BaseStep(
                id="extract_heading",
                action="data",
                object="#page-title",
                key="heading",
            ),
            BaseStep(
                id="extract_desc",
                action="data",
                object="#desc",
                key="description",
            ),
        ],
    )

    # Validate template format before launching
    val_res = validate_template_format(template)
    print(f"✅ Template valid: {val_res.is_valid}\n")

    options = RunOptions(
        browser={"headless": True},
        collect_metrics=True,
    )

    print("🚀 Launching scraper with Page Controls & Actions...")
    results = await run_scraper([template], options)

    print("\n📊 Extracted Results:")
    for r in results:
        print(f" 📌 Heading:     '{r.get('heading')}'")
        print(f" 📝 Description: '{r.get('description')}'")


if __name__ == "__main__":
    asyncio.run(main())
