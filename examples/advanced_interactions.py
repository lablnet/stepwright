import asyncio
import pathlib
from stepwright import run_scraper, TabTemplate, BaseStep, RunOptions


async def run_advanced_demo():
    # Path to our demo HTML file
    demo_file = pathlib.Path(__file__).parent.parent / "tests" / "advanced_demo.html"
    url = f"file://{demo_file.absolute()}"

    # Path to a dummy file to upload
    upload_file = "/tmp/demo_upload.txt"
    with open(upload_file, "w") as f:
        f.write("Hello StepWright!")

    templates = [
        TabTemplate(
            tab="advanced-demo",
            steps=[
                # 1. Navigate to demo page
                BaseStep(id="nav", action="navigate", value=url),
                # 2. Hover over an element to reveal secret text
                BaseStep(
                    id="hover", action="hover", object_type="id", object="hover-target"
                ),
                BaseStep(
                    id="get-hover",
                    action="data",
                    object_type="id",
                    object="secret-text",
                    key="hover_data",
                ),
                # 3. Handle Multi-Select (comma separated values)
                BaseStep(
                    id="select",
                    action="select",
                    object_type="id",
                    object="colors",
                    value="red,yellow",
                ),
                BaseStep(
                    id="get-select",
                    action="data",
                    object_type="id",
                    object="selection-result",
                    key="selection_result",
                ),
                # 4. Drag one element into another
                BaseStep(
                    id="drag",
                    action="dragAndDrop",
                    object_type="id",
                    object="drag-source",
                    targetObject="drop-target",
                    targetObjectType="id",
                    wait=1000,  # Wait for animation/JS
                ),
                BaseStep(
                    id="get-drag",
                    action="data",
                    object_type="id",
                    object="drag-status",
                    key="drag_status",
                ),
                # 5. IFrame Support: Interact with elements inside a frame
                BaseStep(
                    id="iframe-input",
                    action="input",
                    frameSelector="test-iframe",
                    frameSelectorType="id",
                    object_type="id",
                    object="iframe-input",
                    value="Hello from StepWright!",
                ),
                BaseStep(
                    id="iframe-click",
                    action="click",
                    frameSelector="test-iframe",
                    frameSelectorType="id",
                    object_type="id",
                    object="iframe-btn",
                ),
                BaseStep(
                    id="get-iframe-state",
                    action="data",
                    frameSelector="test-iframe",
                    frameSelectorType="id",
                    object_type="id",
                    object="iframe-btn",
                    key="iframe_btn_text",
                ),
                # 6. Virtual Scroll: Collect 15 items from an infinite-scroll-like list
                BaseStep(
                    id="vscroll",
                    action="virtualScroll",
                    object_type="class",
                    object="virtual-item",
                    virtualScrollUniqueKey="id",
                    virtualScrollLimit=15,
                    virtualScrollOffset=150,
                    virtualScrollDelay=500,
                    virtualScrollContainer="virtual-scroll-container",
                    virtualScrollContainerType="id",
                    key="collected_items",
                    subSteps=[
                        BaseStep(
                            id="item-name",
                            action="data",
                            object_type="tag",
                            object="strong",
                            key="name",
                        ),
                        BaseStep(
                            id="item-id",
                            action="data",
                            object_type="class",
                            object="id",
                            key="id",
                        ),
                    ],
                ),
            ],
        )
    ]

    print("🚀 Starting Advanced Demo...")
    results = await run_scraper(templates, RunOptions(browser={"headless": True}))

    print("\n📊 Results Summary:")
    res = results[0]
    print(f"- Hover revealed: {res.get('hover_data')}")
    print(f"- Selection: {res.get('selection_result')}")
    print(f"- Drag & Drop: {res.get('drag_status')}")
    print(f"- IFrame Button Text: {res.get('iframe_btn_text')}")
    print(f"- Virtual Scroll items collected: {len(res.get('collected_items', []))}")
    print("\nFirst 3 virtual items:")
    for item in res.get("collected_items", [])[:3]:
        print(f"  > {item['name']} (ID: {item['id']})")


if __name__ == "__main__":
    asyncio.run(run_advanced_demo())
