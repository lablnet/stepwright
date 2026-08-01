# adapters/database/sqlite_adapter.py
# SQLite Database Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class SQLiteAdapter(BaseStorageAdapter):
    """
    Built-in SQLite database storage adapter.
    Creates target table dynamically if it does not exist.

    @since 2.0.0
    """

    def __init__(
        self,
        db_path: str = "scraped_data.db",
        table_name: str = "scraped_records",
    ) -> None:
        self.db_path = db_path
        self.table_name = table_name
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect to database
        self.connect()

        # get table_name from options or use default
        table = (options and options.get("table_name")) or self.table_name

        # convert single record to list
        raw_records = data if isinstance(data, list) else [data]
        if not raw_records:
            return True

        # normalize record items to dictionaries
        records = []
        for r in raw_records:
            if isinstance(r, dict):
                records.append(r)
            else:
                records.append({"value": str(r)})

        # extract table column names from sample record
        sample = records[0]
        columns = list(sample.keys())

        # ensure table exists dynamically
        col_defs = ", ".join([f'"{c}" TEXT' for c in columns])
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs});'
        self.conn.execute(create_sql)

        # construct parameterized insert SQL query
        placeholders = ", ".join(["?"] * len(columns))
        col_names = ", ".join([f'"{c}"' for c in columns])
        insert_sql = f'INSERT INTO "{table}" ({col_names}) VALUES ({placeholders});'

        # prepare row tuples for executemany
        rows = []
        for r in records:
            row = []
            for col in columns:
                val = r.get(col)
                if isinstance(val, (dict, list)):
                    row.append(json.dumps(val))
                elif val is None:
                    row.append(None)
                else:
                    row.append(str(val))
            rows.append(row)

        # execute batch insert and commit transaction
        self.conn.executemany(insert_sql, rows)
        self.conn.commit()
        return True

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None
