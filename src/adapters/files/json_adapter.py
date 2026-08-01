# adapters/files/json_adapter.py
# JSON File Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class JSONFileAdapter(BaseStorageAdapter):
    """
    Storage adapter for exporting records to JSON files.

    @since 2.0.0
    """

    def __init__(self, file_path: str = "output.json") -> None:
        self.file_path = file_path

    def connect(self) -> None:
        folder = os.path.dirname(self.file_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect / prepare output directory
        self.connect()

        # get file_path from options or use default
        target = (options and options.get("file_path")) or self.file_path

        # convert single record to list
        records = data if isinstance(data, list) else [data]

        existing = []
        # check if file exists and has content
        if os.path.exists(target) and os.path.getsize(target) > 0:
            try:
                # read existing data from file
                with open(target, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    # if existing data is not a list, convert to list
                    if not isinstance(existing, list):
                        existing = [existing]
            except Exception:
                existing = []

        # append new records to existing list
        existing.extend(records)

        # write updated records list to JSON file
        with open(target, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
        return True

    def close(self) -> None:
        pass
