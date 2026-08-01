# adapters/files/csv_adapter.py
# CSV File Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import csv
import os
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class CSVFileAdapter(BaseStorageAdapter):
    """
    Storage adapter for appending records to CSV files.

    @since 2.0.0
    """

    def __init__(self, file_path: str = "output.csv") -> None:
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
        self.connect()
        # get file_path from options or use default
        target = (options and options.get("file_path")) or self.file_path
        # convert single record to list
        records = data if isinstance(data, list) else [data]
        # check if records is empty
        if not records:
            return True

        # get fieldnames
        fieldnames = list(records[0].keys()) if isinstance(records[0], dict) else ["value"]
        # check if file exists
        file_exists = os.path.exists(target) and os.path.getsize(target) > 0

        # open file in append mode
        with open(target, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            # write header if file is empty
            if not file_exists:
                writer.writeheader()
            # write records
            for r in records:
                row = r if isinstance(r, dict) else {"value": str(r)}
                writer.writerow(row)
        return True

    def close(self) -> None:
        pass
