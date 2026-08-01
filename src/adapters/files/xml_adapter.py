# adapters/files/xml_adapter.py
# XML File Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class XMLFileAdapter(BaseStorageAdapter):
    """
    Storage adapter for exporting records to XML files.

    @since 2.0.0
    """

    def __init__(self, file_path: str = "output.xml", root_element: str = "data") -> None:
        self.file_path = file_path
        self.root_element = root_element

    def connect(self) -> None:
        folder = os.path.dirname(self.file_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        self.connect()
        # get file_path from options or use default
        target = (options and options.get("file_path")) or self.file_path
        
        # convert single record to list
        records = data if isinstance(data, list) else [data]

        # Create root element
        root = ET.Element(self.root_element)
        # Create item element for each record
        for r in records:
            item = ET.SubElement(root, "item")
            # Add key-value pairs as sub-elements
            if isinstance(r, dict):
                # Check if value is list or dict
                for k, v in r.items():
                    child = ET.SubElement(item, str(k))
                    child.text = "" if v is None else str(v)
            else:
                child = ET.SubElement(item, "value")
                child.text = str(r)

        # convert to tree
        tree = ET.ElementTree(root)
        # pretty print
        ET.indent(tree, space="  ", level=0)
        # write to file
        tree.write(target, encoding="utf-8", xml_declaration=True)
        return True

    def close(self) -> None:
        pass
