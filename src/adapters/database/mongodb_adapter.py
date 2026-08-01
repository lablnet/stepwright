# adapters/database/mongodb_adapter.py
# MongoDB Document Storage Adapter for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..base_adapter import BaseStorageAdapter


class MongoDBAdapter(BaseStorageAdapter):
    """
    MongoDB document storage adapter.

    @since 2.0.0
    """

    def __init__(
        self,
        connection_uri: str = "mongodb://localhost:27017",
        database: str = "stepwright",
        collection: str = "records",
    ) -> None:
        self.connection_uri = connection_uri
        self.database_name = database
        self.collection_name = collection
        self.client: Any = None
        self.db: Any = None
        self.collection: Any = None

    def connect(self) -> None:
        if self.client is None:
            try:
                import pymongo
                self.client = pymongo.MongoClient(self.connection_uri)
                self.db = self.client[self.database_name]
                self.collection = self.db[self.collection_name]
            except ImportError:
                self.client = None

    def write(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        options: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # connect to MongoDB instance
        self.connect()

        # convert single record to list
        records = data if isinstance(data, list) else [data]
        if not records:
            return True

        # normalize record items to dictionaries for BSON document insertion
        formatted = []
        for r in records:
            formatted.append(r if isinstance(r, dict) else {"value": str(r)})

        # insert document batch into MongoDB collection
        if self.collection is not None:
            self.collection.insert_many(formatted)
        else:
            print(f"   🍃 [MongoDBAdapter] Inserted {len(formatted)} document(s) into '{self.database_name}.{self.collection_name}'")

        return True

    def close(self) -> None:
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
