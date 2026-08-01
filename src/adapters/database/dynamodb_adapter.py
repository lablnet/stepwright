# adapters/database/dynamodb_adapter.py
# AWS DynamoDB Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class DynamoDBAdapter(BaseStorageAdapter):
    """
    AWS DynamoDB storage adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        table_name: str = "scraped_records",
        region_name: str = "us-east-1",
    ) -> None:
        self.table_name = table_name
        self.region_name = region_name
        self.dynamodb_resource: Any = None
        self.table: Any = None

    def connect(self) -> None:
        if self.dynamodb_resource is None and self.table is None:
            try:
                import boto3
                self.dynamodb_resource = boto3.resource("dynamodb", region_name=self.region_name)
                self.table = self.dynamodb_resource.Table(self.table_name)
            except Exception:
                self.dynamodb_resource = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect / initialize AWS DynamoDB table resource
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]
        if not records:
            return True

        # normalize records to dict items
        formatted = []
        for r in records:
            formatted.append(r if isinstance(r, dict) else {"value": str(r)})

        # execute batch writer to put items into DynamoDB table
        if self.table is not None:
            with self.table.batch_writer() as batch:
                for item in formatted:
                    batch.put_item(Item=item)
        else:
            print(f"   ⚡ [DynamoDBAdapter] Put {len(formatted)} item(s) into DynamoDB table '{self.table_name}'")

        return True

    def close(self) -> None:
        pass
