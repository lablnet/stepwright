# examples/custom_data_flow.py
"""
StepWright Custom Data Flow Example
-----------------------------------
This example demonstrates how to integrate non-standard file formats (like XML)
using custom reader and writer callbacks.
"""

import asyncio
import pathlib
import xml.etree.ElementTree as ET
from stepwright import run_scraper, TabTemplate, BaseStep, RunOptions


# 1. Define custom reader and writer callbacks
def xml_reader(path, step):
    """Parses an XML file and returns a list of dictionaries for StepWright."""
    print(f"📊 Custom Reader reading from: {path}")
    tree = ET.parse(path)
    root = tree.getroot()

    items = []
    for el in root.findall(".//item"):
        items.append(
            {
                "id": el.find("id").text if el.find("id") is not None else "unknown",
                "name": el.find("name").text
                if el.find("name") is not None
                else "unknown",
                "url": el.find("url").text
                if el.find("url") is not None
                else "https://example.com",
            }
        )
    return items


def xml_writer(path, data, step):
    """Serializes the collector results back into a custom XML format."""
    print(f"💾 Custom Writer saving to: {path}")
    root = ET.Element("results")

    # data is usually the list from the key specified in writeData
    for entry in data:
        item_el = ET.SubElement(root, "scraped_item")
        for k, v in entry.items():
            child = ET.SubElement(item_el, k)
            child.text = str(v)

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return True


async def main():
    # Setup paths
    data_dir = pathlib.Path("./data")
    data_dir.mkdir(exist_ok=True)

    input_xml = data_dir / "input_seeds.xml"
    output_xml = data_dir / "processed_results.xml"

    # Create dummy input XML
    with open(input_xml, "w") as f:
        f.write("""<?xml version="1.0"?>
<seeds>
    <item>
        <id>001</id>
        <name>Electronics</name>
        <url>file://dummy_path?category=electronics</url>
    </item>
    <item>
        <id>002</id>
        <name>Books</name>
        <url>file://dummy_path?category=books</url>
    </item>
</seeds>
""")

    # 2. Define Template with custom data handlers
    template = TabTemplate(
        tab="xml-flow",
        steps=[
            # Load from XML using custom reader
            BaseStep(
                id="load-seeds",
                action="readData",
                value=str(input_xml),
                data_type="custom",
                callback=xml_reader,
                key="seed_queue",
            ),
            # Loop over items from XML
            BaseStep(
                id="process-items",
                action="foreach",
                value="{{seed_queue}}",
                subSteps=[
                    # Just simulate processing with a custom action
                    BaseStep(
                        id="process-hook",
                        action="custom",
                        callback=lambda page, coll, step: {
                            "processed_at": asyncio.get_event_loop().time(),
                            "original_name": coll.get("name"),
                        },
                        key="metadata",
                    )
                ],
                key="final_results",
            ),
            # Save results back to XML using custom writer
            BaseStep(
                id="save-xml",
                action="writeData",
                value=str(output_xml),
                data_type="custom",
                callback=xml_writer,
                key="final_results",
            ),
        ],
    )

    print("🚀 Starting Custom Data Flow...")
    await run_scraper([template], RunOptions(browser={"headless": True}))

    if output_xml.exists():
        print(f"✨ Custom XML file created: {output_xml}")
        with open(output_xml, "r") as f:
            print("\nPreview of output XML:")
            print(f.read()[:500])


if __name__ == "__main__":
    asyncio.run(main())
