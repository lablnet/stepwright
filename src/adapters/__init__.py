# adapters/__init__.py
# Enterprise Storage Adapter Package for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from .base_adapter import BaseStorageAdapter

# File Adapters
from .files.json_adapter import JSONFileAdapter
from .files.csv_adapter import CSVFileAdapter
from .files.xml_adapter import XMLFileAdapter

# Database Adapters
from .database.sqlite_adapter import SQLiteAdapter
from .database.postgres_adapter import PostgreSQLAdapter
from .database.mysql_adapter import MySQLAdapter
from .database.mongodb_adapter import MongoDBAdapter
from .database.dynamodb_adapter import DynamoDBAdapter
from .database.elasticsearch_adapter import ElasticsearchAdapter

# Cloud Storage Adapters
from .cloud.s3_adapter import S3StorageAdapter
from .cloud.gcs_adapter import GCSStorageAdapter
from .cloud.azure_adapter import AzureBlobAdapter

# Queue & Stream Adapters
from .queue.rabbitmq_adapter import RabbitMQAdapter
from .queue.kafka_adapter import KafkaAdapter

_ADAPTER_REGISTRY: Dict[str, Type[BaseStorageAdapter]] = {
    "json": JSONFileAdapter,
    "csv": CSVFileAdapter,
    "xml": XMLFileAdapter,
    "sqlite": SQLiteAdapter,
    "postgres": PostgreSQLAdapter,
    "postgresql": PostgreSQLAdapter,
    "mysql": MySQLAdapter,
    "mongo": MongoDBAdapter,
    "mongodb": MongoDBAdapter,
    "dynamodb": DynamoDBAdapter,
    "elasticsearch": ElasticsearchAdapter,
    "s3": S3StorageAdapter,
    "gcs": GCSStorageAdapter,
    "azure": AzureBlobAdapter,
    "rabbitmq": RabbitMQAdapter,
    "kafka": KafkaAdapter,
}


def register_adapter(name: str, adapter_cls: Type[BaseStorageAdapter]) -> None:
    """
    Register a custom storage adapter class under a string name identifier.

    @since 2.0.0
    """
    if not issubclass(adapter_cls, BaseStorageAdapter):
        raise ValueError(f"Adapter class {adapter_cls} must subclass BaseStorageAdapter.")
    _ADAPTER_REGISTRY[name.lower()] = adapter_cls


def get_adapter(
    adapter: Union[str, BaseStorageAdapter, None] = None,
    **kwargs: Any,
) -> BaseStorageAdapter:
    """
    Get or resolve a storage adapter instance.

    :param adapter: Adapter name string (e.g. 'json', 'sqlite', 's3') or a BaseStorageAdapter instance
    :return: BaseStorageAdapter instance

    @since 2.0.0
    """
    if adapter is None or adapter == "json":
        return JSONFileAdapter(**kwargs)

    if isinstance(adapter, BaseStorageAdapter):
        return adapter

    if isinstance(adapter, str):
        key = adapter.lower()
        if key in _ADAPTER_REGISTRY:
            cls = _ADAPTER_REGISTRY[key]
            return cls(**kwargs)
        raise ValueError(f"Unknown storage adapter '{adapter}'. Registered adapters: {list(_ADAPTER_REGISTRY.keys())}")

    raise ValueError(f"Invalid storage adapter specification: {adapter}. Expected string identifier or BaseStorageAdapter instance.")


__all__ = [
    "BaseStorageAdapter",
    "JSONFileAdapter",
    "CSVFileAdapter",
    "XMLFileAdapter",
    "SQLiteAdapter",
    "PostgreSQLAdapter",
    "MySQLAdapter",
    "MongoDBAdapter",
    "DynamoDBAdapter",
    "ElasticsearchAdapter",
    "S3StorageAdapter",
    "GCSStorageAdapter",
    "AzureBlobAdapter",
    "RabbitMQAdapter",
    "KafkaAdapter",
    "get_adapter",
    "register_adapter",
]
