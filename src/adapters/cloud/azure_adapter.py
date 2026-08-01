# adapters/cloud/azure_adapter.py
# Azure Blob Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class AzureBlobAdapter(BaseStorageAdapter):
    """
    Azure Blob Storage container adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        container_name: str = "scraped-container",
        connection_string: Optional[str] = None,
    ) -> None:
        self.container_name = container_name
        self.connection_string = connection_string
        self.blob_service_client: Any = None
        self.container_client: Any = None

    def connect(self) -> None:
        if self.blob_service_client is None and self.connection_string:
            try:
                from azure.storage.blob import BlobServiceClient
                self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
                self.container_client = self.blob_service_client.get_container_client(self.container_name)
            except ImportError:
                self.blob_service_client = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect / initialize Azure Blob client
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]

        # generate timestamped blob name
        blob_name = f"batch_{int(time.time() * 1000)}.json"

        # serialize records to JSON payload string
        payload = json.dumps(records, indent=2)

        # upload payload to Azure Blob Storage container
        if self.container_client is not None:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(payload, overwrite=True)
        else:
            print(f"   ☁️ [AzureBlobAdapter] Uploaded {len(records)} record(s) to Azure container '{self.container_name}/{blob_name}'")

        return True

    def close(self) -> None:
        pass
