import pytest
import pathlib
import os
from stepwright import run_scraper, TabTemplate, BaseStep


@pytest.mark.asyncio
async def test_advanced_features():
    html_path = pathlib.Path(__file__).parent / "advanced_demo.html"
    url = f"file://{html_path.absolute()}"
    test_file_path = "/tmp/test_upload.txt"

    # Ensure test file exists
    if not os.path.exists(test_file_path):
        with open(test_file_path, "w") as f:
            f.write("test content")

    templates = [
        TabTemplate(
            tab="advanced-test",
            steps=[
                # 1. Navigation
                BaseStep(id="home", action="navigate", value=url),
                # 2. Hover test
                BaseStep(
                    id="hover", action="hover", object_type="id", object="hover-target"
                ),
                BaseStep(
                    id="check-hover",
                    action="data",
                    object_type="id",
                    object="secret-text",
                    key="hover_content",
                ),
                # 3. Multi-Select test
                BaseStep(
                    id="select-colors",
                    action="select",
                    object_type="id",
                    object="colors",
                    value="red,green",
                ),
                BaseStep(
                    id="check-select",
                    action="data",
                    object_type="id",
                    object="selection-result",
                    key="selection_text",
                ),
                # 4. Drag and Drop test
                BaseStep(
                    id="drag",
                    action="dragAndDrop",
                    object_type="id",
                    object="drag-source",
                    targetObject="drop-target",
                    targetObjectType="id",
                ),
                BaseStep(
                    id="check-drag",
                    action="data",
                    object_type="id",
                    object="drag-status",
                    key="drag_status",
                ),
                # 5. File Upload test
                BaseStep(
                    id="upload",
                    action="uploadFile",
                    object_type="id",
                    object="file-input",
                    value=test_file_path,
                ),
                BaseStep(
                    id="check-upload",
                    action="data",
                    object_type="id",
                    object="file-status",
                    key="upload_status",
                ),
                # 6. IFrame test
                BaseStep(
                    id="iframe-click",
                    action="click",
                    frameSelector="test-iframe",
                    frameSelectorType="id",
                    object_type="id",
                    object="iframe-btn",
                ),
                BaseStep(
                    id="iframe-data",
                    action="data",
                    frameSelector="test-iframe",
                    frameSelectorType="id",
                    object_type="id",
                    object="iframe-btn",
                    key="iframe_btn_text",
                ),
                # 7. Virtual Scroll test
                BaseStep(
                    id="vscroll",
                    action="virtualScroll",
                    object_type="class",
                    object="virtual-item",
                    virtualScrollUniqueKey="id",
                    virtualScrollLimit=30,
                    virtualScrollOffset=200,
                    virtualScrollDelay=100,
                    virtualScrollContainer="virtual-scroll-container",
                    virtualScrollContainerType="id",
                    key="vitems",
                    subSteps=[
                        BaseStep(
                            id="vname",
                            action="data",
                            object_type="tag",
                            object="strong",
                            key="name",
                        ),
                        BaseStep(
                            id="vid",
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

    results = await run_scraper(templates)

    assert len(results) > 0
    res = results[0]

    # Assert Hover
    assert "Secret content" in res.get("hover_content", "")

    # Assert Multi-Select
    assert "red, green" in res.get("selection_text", "").lower()

    # Assert Drag and Drop
    assert "Dropped successfully" in res.get("drag_status", "")

    # Assert File Upload
    assert "test_upload.txt" in res.get("upload_status", "")

    # Assert IFrame
    assert "Clicked!" in res.get("iframe_btn_text", "")

    # Assert Virtual Scroll
    vitems = res.get("vitems", [])
    assert len(vitems) >= 30
    # Check for some items that would require scrolling (demo has 200px height, 40px per item = 5 visible)
    # 30 items certainly requires scrolling
    assert any("29" in item["id"] for item in vitems)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_advanced_features())
