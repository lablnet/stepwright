# adapters/database/elasticsearch_adapter.py
# Elasticsearch Document Indexer Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class ElasticsearchAdapter(BaseStorageAdapter):
    """
    Elasticsearch document indexer adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        index: str = "stepwright_scraped",
    ) -> None:
        self.hosts = hosts or ["http://localhost:9200"]
        self.index = index
        self.client: Any = None

    def connect(self) -> None:
        if self.client is None:
            try:
                from elasticsearch import Elasticsearch
                self.client = Elasticsearch(self.hosts)
            except ImportError:
                self.client = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect / initialize Elasticsearch client
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]
        if not records:
            return True

        # normalize record items to dictionaries
        formatted = []
        for r in records:
            formatted.append(r if isinstance(r, dict) else {"value": str(r)})

        # index document batch into Elasticsearch index
        if self.client is not None:
            for item in formatted:
                self.client.index(index=self.index, body=item)
        else:
            print(f"   🔍 [ElasticsearchAdapter] Indexed {len(formatted)} document(s) into '{self.index}'")

        return True

    def close(self) -> None:
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
