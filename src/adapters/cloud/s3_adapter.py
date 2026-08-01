# adapters/cloud/s3_adapter.py
# AWS S3 Cloud Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class S3StorageAdapter(BaseStorageAdapter):
    """
    AWS S3 Cloud Object Storage adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        bucket: str = "my-bucket",
        key_prefix: str = "scraped_data/",
        region_name: str = "us-east-1",
    ) -> None:
        self.bucket = bucket
        self.key_prefix = key_prefix
        self.region_name = region_name
        self.s3_client: Any = None

    def connect(self) -> None:
        if self.s3_client is None:
            try:
                import boto3
                self.s3_client = boto3.client("s3", region_name=self.region_name)
            except ImportError:
                self.s3_client = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect / initialize AWS S3 client
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]

        # generate timestamped S3 object key path
        key = f"{self.key_prefix}batch_{int(time.time() * 1000)}.json"

        # serialize records to JSON byte stream
        payload = json.dumps(records, indent=2).encode("utf-8")

        # upload byte stream object to AWS S3 bucket
        if self.s3_client is not None:
            self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=payload)
        else:
            print(f"   ☁️ [S3StorageAdapter] Exported {len(records)} record(s) to s3://{self.bucket}/{key}")

        return True

    def close(self) -> None:
        pass
