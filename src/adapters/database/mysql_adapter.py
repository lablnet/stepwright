# adapters/database/mysql_adapter.py
# MySQL Database Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class MySQLAdapter(BaseStorageAdapter):
    """
    MySQL database storage adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        connection_string: str = "mysql://user:pass@localhost:3306/stepwright",
        table_name: str = "scraped_records",
    ) -> None:
        self.connection_string = connection_string
        self.table_name = table_name
        self.conn: Any = None

    def connect(self) -> None:
        if self.conn is None:
            try:
                import pymysql
                self.conn = pymysql.connect(host="localhost", user="user", password="pass", db="stepwright")
            except ImportError:
                self.conn = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect to MySQL database server
        self.connect()

        # get table_name from options or use default
        table = (options and options.get("table_name")) or self.table_name

        # convert single record to list
        records = data if isinstance(data, list) else [data]
        if not records:
            return True

        # extract table column names from sample record
        sample = records[0] if isinstance(records[0], dict) else {"value": str(records[0])}
        columns = list(sample.keys())

        if self.conn:
            with self.conn.cursor() as cur:
                # ensure table exists dynamically
                col_defs = ", ".join([f'`{c}` TEXT' for c in columns])
                cur.execute(f'CREATE TABLE IF NOT EXISTS `{table}` ({col_defs});')

                # construct parameterized insert SQL query
                placeholders = ", ".join(["%s"] * len(columns))
                col_names = ", ".join([f'`{c}`' for c in columns])
                insert_sql = f'INSERT INTO `{table}` ({col_names}) VALUES ({placeholders});'

                # prepare row tuples for executemany
                rows = []
                for r in records:
                    row = []
                    item = r if isinstance(r, dict) else {"value": str(r)}
                    for c in columns:
                        v = item.get(c)
                        row.append(json.dumps(v) if isinstance(v, (dict, list)) else v)
                    rows.append(row)

                # execute batch insert and commit transaction
                cur.executemany(insert_sql, rows)
                self.conn.commit()
        else:
            print(f"   🗄️ [MySQLAdapter] Outputted {len(records)} record(s) to table '{table}'")

        return True

    def close(self) -> None:
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
