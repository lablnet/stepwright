# tests/test_custom_data.py
import pytest
import xml.etree.ElementTree as ET
from stepwright import run_scraper, TabTemplate, BaseStep, RunOptions


@pytest.mark.asyncio
async def test_custom_xml_reader_writer(tmp_path):
    """Test custom XML reader/writer callbacks for readData and writeData."""
    input_xml = tmp_path / "test_input.xml"
    output_xml = tmp_path / "test_output.xml"

    # Create simple XML
    root = ET.Element("data")
    item = ET.SubElement(root, "item")
    name = ET.SubElement(item, "name")
    name.text = "test_item"
    tree = ET.ElementTree(root)
    tree.write(input_xml)

    # custom reader
    def reader(path, step):
        t = ET.parse(path)
        r = t.getroot()
        res = []
        for i in r.findall("item"):
            res.append({"name": i.find("name").text})
        return res

    # custom writer
    def writer(path, data, step):
        r = ET.Element("results")
        for d in data:
            it = ET.SubElement(r, "scraped_item")
            it.text = d.get("name")
        t = ET.ElementTree(r)
        t.write(path)
        return True

    # template
    template = TabTemplate(
        tab="xml-test",
        steps=[
            # Read from XML
            BaseStep(
                id="load",
                action="readData",
                value=str(input_xml),
                data_type="custom",
                callback=reader,
                key="items",
            ),
            # Write to XML
            BaseStep(
                id="save",
                action="writeData",
                value=str(output_xml),
                data_type="custom",
                callback=writer,
                key="items",
            ),
        ],
    )

    await run_scraper([template], RunOptions(browser={"headless": True}))

    # Verify
    assert output_xml.exists()
    tree = ET.parse(output_xml)
    root = tree.getroot()
    assert root.find("scraped_item").text == "test_item"
    print("\n✅ Custom XML data flow test passed!")


@pytest.mark.asyncio
async def test_custom_action_hook():
    """Test the 'custom' action which executes a callback."""

    def hook(page, collector, step):
        # Calculate something using collector or page
        return f"processed {step.id}"

    template = TabTemplate(
        tab="hook-test",
        steps=[
            BaseStep(id="my-hook", action="custom", callback=hook, key="result_msg")
        ],
    )

    results = await run_scraper([template], RunOptions(browser={"headless": True}))

    # results from run_scraper are flattened, so check the key
    assert results[0]["result_msg"] == "processed my-hook"
    print("✅ Custom action hook test passed!")
