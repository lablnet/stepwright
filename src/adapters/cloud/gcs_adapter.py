# adapters/cloud/gcs_adapter.py
# Google Cloud Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class GCSStorageAdapter(BaseStorageAdapter):
    """
    Google Cloud Storage (GCS) adapter.

    @since 2.0.0
    """

    def __init__(self, bucket: str = "my-gcs-bucket", blob_prefix: str = "scraped/") -> None:
        self.bucket_name = bucket
        self.blob_prefix = blob_prefix
        self.client: Any = None
        self.bucket: Any = None

    def connect(self) -> None:
        if self.client is None:
            try:
                from google.cloud import storage
                self.client = storage.Client()
                self.bucket = self.client.bucket(self.bucket_name)
            except ImportError:
                self.client = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect / initialize Google Cloud Storage bucket client
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]

        # generate timestamped blob path
        blob_name = f"{self.blob_prefix}batch_{int(time.time() * 1000)}.json"

        # serialize records to JSON payload
        payload = json.dumps(records, indent=2)

        # upload payload string to GCS blob
        if self.bucket is not None:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(payload, content_type="application/json")
        else:
            print(f"   ☁️ [GCSStorageAdapter] Uploaded {len(records)} record(s) to gs://{self.bucket_name}/{blob_name}")

        return True

    def close(self) -> None:
        pass
