# tests/test_storage_adapters.py
# Comprehensive unit tests with MOCKS for every StepWright Enterprise Storage Adapter

import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest
from stepwright import (
    BaseStorageAdapter,
    JSONFileAdapter,
    CSVFileAdapter,
    XMLFileAdapter,
    SQLiteAdapter,
    PostgreSQLAdapter,
    MySQLAdapter,
    MongoDBAdapter,
    DynamoDBAdapter,
    ElasticsearchAdapter,
    S3StorageAdapter,
    GCSStorageAdapter,
    AzureBlobAdapter,
    RabbitMQAdapter,
    KafkaAdapter,
    get_adapter,
    register_adapter,
)


def test_file_adapters(tmp_path):
    """Test JSON, CSV, and XML file adapters"""
    json_file = str(tmp_path / "data.json")
    csv_file = str(tmp_path / "data.csv")
    xml_file = str(tmp_path / "data.xml")

    records = [{"id": 1, "name": "Test Record"}]

    # JSON File Adapter
    json_adp = JSONFileAdapter(file_path=json_file)
    assert json_adp.write(records) is True
    assert os.path.exists(json_file)

    # CSV File Adapter
    csv_adp = CSVFileAdapter(file_path=csv_file)
    assert csv_adp.write(records) is True
    assert os.path.exists(csv_file)

    # XML File Adapter
    xml_adp = XMLFileAdapter(file_path=xml_file)
    assert xml_adp.write(records) is True
    assert os.path.exists(xml_file)


def test_sqlite_adapter(tmp_path):
    """Test SQLite database adapter"""
    db_file = str(tmp_path / "test.db")
    sql_adp = SQLiteAdapter(db_path=db_file, table_name="scraped_items")

    records = [{"title": "Headline 1", "score": "100"}]
    assert sql_adp.write(records) is True

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT title, score FROM scraped_items;")
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0][0] == "Headline 1"


def test_postgres_adapter_mock():
    """Mock test for PostgreSQLAdapter"""
    adapter = PostgreSQLAdapter(dsn="postgresql://user:pass@localhost:5432/db", table_name="test_table")
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    adapter.conn = mock_conn

    records = [{"title": "PG Item"}]
    assert adapter.write(records) is True

    mock_cursor.execute.assert_called_once()
    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_mysql_adapter_mock():
    """Mock test for MySQLAdapter"""
    adapter = MySQLAdapter(connection_string="mysql://user:pass@localhost:3306/db", table_name="my_table")

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    adapter.conn = mock_conn

    records = [{"title": "MySQL Item"}]
    assert adapter.write(records) is True

    mock_cursor.execute.assert_called_once()
    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_mongodb_adapter_mock():
    """Mock test for MongoDBAdapter"""
    adapter = MongoDBAdapter(connection_uri="mongodb://localhost:27017", database="db", collection="col")

    mock_collection = MagicMock()
    adapter.collection = mock_collection

    records = [{"title": "Mongo Item"}]
    assert adapter.write(records) is True

    mock_collection.insert_many.assert_called_once_with([{"title": "Mongo Item"}])


def test_dynamodb_adapter_mock():
    """Mock test for DynamoDBAdapter"""
    adapter = DynamoDBAdapter(table_name="my_dynamo_table", region_name="us-west-2")

    mock_table = MagicMock()
    mock_batch = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_batch
    mock_ctx.__exit__.return_value = None
    mock_table.batch_writer.return_value = mock_ctx
    adapter.table = mock_table

    records = [{"id": "item1", "value": "test"}]
    assert adapter.write(records) is True

    mock_batch.put_item.assert_called_once_with(Item={"id": "item1", "value": "test"})


def test_elasticsearch_adapter_mock():
    """Mock test for ElasticsearchAdapter"""
    adapter = ElasticsearchAdapter(hosts=["http://localhost:9200"], index="my_index")

    mock_client = MagicMock()
    adapter.client = mock_client

    records = [{"doc": "text"}]
    assert adapter.write(records) is True

    mock_client.index.assert_called_once_with(index="my_index", body={"doc": "text"})


def test_s3_storage_adapter_mock():
    """Mock test for S3StorageAdapter"""
    adapter = S3StorageAdapter(bucket="my-test-bucket", key_prefix="data/")

    mock_s3 = MagicMock()
    adapter.s3_client = mock_s3

    records = [{"key": "val"}]
    assert adapter.write(records) is True

    mock_s3.put_object.assert_called_once()
    call_kwargs = mock_s3.put_object.call_args[1]
    assert call_kwargs["Bucket"] == "my-test-bucket"
    assert call_kwargs["Key"].startswith("data/")


def test_gcs_storage_adapter_mock():
    """Mock test for GCSStorageAdapter"""
    adapter = GCSStorageAdapter(bucket="gcs-bucket", blob_prefix="exports/")

    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    adapter.bucket = mock_bucket

    records = [{"item": 1}]
    assert adapter.write(records) is True

    mock_bucket.blob.assert_called_once()
    mock_blob.upload_from_string.assert_called_once()


def test_azure_blob_adapter_mock():
    """Mock test for AzureBlobAdapter"""
    adapter = AzureBlobAdapter(container_name="azure-container")

    mock_container = MagicMock()
    mock_blob_client = MagicMock()
    mock_container.get_blob_client.return_value = mock_blob_client
    adapter.container_client = mock_container

    records = [{"azure": True}]
    assert adapter.write(records) is True

    mock_container.get_blob_client.assert_called_once()
    mock_blob_client.upload_blob.assert_called_once()


def test_rabbitmq_adapter_mock():
    """Mock test for RabbitMQAdapter"""
    adapter = RabbitMQAdapter(queue_name="scraped_queue")

    mock_channel = MagicMock()
    adapter.channel = mock_channel

    records = [{"msg": "hello"}]
    assert adapter.write(records) is True

    mock_channel.basic_publish.assert_called_once()


def test_kafka_adapter_mock():
    """Mock test for KafkaAdapter"""
    adapter = KafkaAdapter(topic="scraped_topic")

    mock_producer = MagicMock()
    adapter.producer = mock_producer

    records = [{"event": "scraped"}]
    assert adapter.write(records) is True

    mock_producer.send.assert_called_once_with("scraped_topic", {"event": "scraped"})
    mock_producer.flush.assert_called_once()


class CustomMockAdapter(BaseStorageAdapter):
    """Custom mock adapter for testing registration"""

    def __init__(self):
        self.logs = []

    def connect(self):
        pass

    def write(self, data, options=None):
        self.logs.append(data)
        return True

    def close(self):
        pass


def test_adapter_resolver_and_registration():
    """Test get_adapter resolution and register_adapter"""
    register_adapter("custom_mock", CustomMockAdapter)
    adp = get_adapter("custom_mock")
    assert isinstance(adp, CustomMockAdapter)
    assert adp.write({"test": 1}) is True
    assert len(adp.logs) == 1

    # Test resolving string aliases
    assert isinstance(get_adapter("json"), JSONFileAdapter)
    assert isinstance(get_adapter("csv"), CSVFileAdapter)
    assert isinstance(get_adapter("xml"), XMLFileAdapter)
    assert isinstance(get_adapter("sqlite"), SQLiteAdapter)
    assert isinstance(get_adapter("s3"), S3StorageAdapter)
    assert isinstance(get_adapter("postgres"), PostgreSQLAdapter)
    assert isinstance(get_adapter("mongo"), MongoDBAdapter)


def test_adapter_empty_records_and_close(tmp_path):
    """Test handling of empty records and close() method across adapters"""
    csv_file = str(tmp_path / "empty.csv")
    db_file = str(tmp_path / "empty.db")

    csv_adp = CSVFileAdapter(file_path=csv_file)
    assert csv_adp.write([]) is True
    csv_adp.close()

    sqlite_adp = SQLiteAdapter(db_path=db_file)
    assert sqlite_adp.write([]) is True
    sqlite_adp.close()

    pg_adp = PostgreSQLAdapter(dsn="postgresql://localhost/db")
    pg_adp.conn = MagicMock()
    assert pg_adp.write([]) is True
    pg_adp.close()

    mongo_adp = MongoDBAdapter(connection_uri="mongodb://localhost:27017")
    mongo_adp.collection = MagicMock()
    assert mongo_adp.write([]) is True
    mongo_adp.close()

    s3_adp = S3StorageAdapter(bucket="test")
    s3_adp.s3_client = MagicMock()
    assert s3_adp.write([]) is True
    s3_adp.close()
