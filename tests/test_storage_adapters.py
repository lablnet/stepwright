# tests/test_storage_adapters.py
# Comprehensive unit tests with MOCKS for every StepWright Enterprise Storage Adapter

import os
import sqlite3
import sys
import types
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


def test_xml_and_json_adapter_edge_cases(tmp_path):
    """Test XML and JSON adapter edge cases including non-dict items and JSON file reading"""
    import xml.etree.ElementTree as ET

    xml_path = str(tmp_path / "edge.xml")
    xml_adp = XMLFileAdapter(file_path=xml_path)

    # Primitive non-dict record elements
    records = ["simple_string", 456, True]
    assert xml_adp.write(records) is True

    # Test _indent directly
    root = ET.Element("root")
    c1 = ET.SubElement(root, "c1")
    c2 = ET.SubElement(c1, "c2")
    c2.text = "nested text"
    xml_adp._indent(root, level=1)
    xml_adp.close()

    # JSON File Adapter with existing non-list data
    json_path = str(tmp_path / "dict_only.json")
    with open(json_path, "w") as f:
        f.write('{"single": "object"}')

    json_adp = JSONFileAdapter(file_path=json_path)
    assert json_adp.write({"second": "object"}) is True
    json_adp.close()

    with open(json_path) as f:
        import json
        data = json.load(f)
        assert len(data) == 2


def test_kafka_and_es_and_azure_close_and_options():
    """Test close methods and fallback print outputs for message queue and cloud adapters"""
    # Kafka close with exception
    kafka_adp = KafkaAdapter(topic="t")
    mock_prod = MagicMock()
    mock_prod.close.side_effect = Exception("Close error")
    kafka_adp.producer = mock_prod
    kafka_adp.close()
    assert kafka_adp.producer is None

    # Elasticsearch close with exception
    es_adp = ElasticsearchAdapter(index="i")
    mock_client = MagicMock()
    mock_client.close.side_effect = Exception("Close error")
    es_adp.client = mock_client
    es_adp.close()
    assert es_adp.client is None

    # AzureBlob close
    az_adp = AzureBlobAdapter(container_name="c")
    az_adp.close()


def test_adapters_init_and_base_adapter_coverage():
    """Test registry validation and base adapter default methods"""
    import pytest
    from stepwright.adapters import register_adapter, get_adapter
    from stepwright.adapters.base_adapter import BaseStorageAdapter

    # Register invalid class raises ValueError
    class NonAdapter:
        pass

    with pytest.raises(ValueError, match="must subclass BaseStorageAdapter"):
        register_adapter("invalid", NonAdapter)  # type: ignore

    # Unknown adapter name
    with pytest.raises(ValueError, match="Unknown storage adapter"):
        get_adapter("unknown_adapter_xyz")

    # Invalid adapter spec type
    with pytest.raises(ValueError, match="Invalid storage adapter specification"):
        get_adapter(12345)  # type: ignore

    class MinimalAdapter(BaseStorageAdapter):
        def connect(self):
            pass
        def write(self, data, options=None):
            return True
        def close(self):
            pass

    adapter = MinimalAdapter()
    adapter.connect()
    assert adapter.write({"test": 1}) is True
    adapter.close()


def test_db_and_cloud_active_connections_mock():
    """Test active connection write and close paths for MySQL, Postgres, Mongo, DynamoDB, S3, GCS, RabbitMQ"""
    # MySQL with active conn mock
    my_adp = MySQLAdapter()
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    my_adp.conn = mock_conn
    assert my_adp.write([{"col1": "val1", "col2": [1, 2]}]) is True
    my_adp.close()
    mock_conn.close.assert_called_once()

    # Postgres with active conn mock
    pg_adp = PostgreSQLAdapter()
    mock_pg_conn = MagicMock()
    mock_pg_cur = MagicMock()
    mock_pg_conn.cursor.return_value.__enter__.return_value = mock_pg_cur
    pg_adp.conn = mock_pg_conn
    assert pg_adp.write([{"col1": "val1"}]) is True
    pg_adp.close()
    mock_pg_conn.close.assert_called_once()

    # DynamoDB with active client & table mock
    dyn_adp = DynamoDBAdapter()
    mock_table = MagicMock()
    mock_batch = MagicMock()
    mock_table.batch_writer.return_value.__enter__.return_value = mock_batch
    dyn_adp.table = mock_table
    assert dyn_adp.write([{"id": "1", "data": "test"}]) is True
    dyn_adp.close()


    # S3 close with active client
    s3_adp = S3StorageAdapter()
    mock_s3 = MagicMock()
    s3_adp.s3_client = mock_s3
    s3_adp.close()

    # GCS close with active client
    gcs_adp = GCSStorageAdapter()
    mock_gcs = MagicMock()
    gcs_adp.gcs_client = mock_gcs
    gcs_adp.close()

    # RabbitMQ close with active connection
    rmq_adp = RabbitMQAdapter()
    mock_rmq_conn = MagicMock()
    rmq_adp.connection = mock_rmq_conn
    rmq_adp.close()
    mock_rmq_conn.close.assert_called_once()


def test_adapters_import_error_fallbacks_and_exceptions(monkeypatch):
    """Test connect() ImportError fallbacks and close() exception handling across all adapters"""
    import builtins
    real_import = builtins.__import__

    # Function to simulate missing libraries
    def mock_import(name, *args, **kwargs):
        if name in ("azure.storage.blob", "google.cloud", "pymongo", "pymysql", "psycopg2", "pika", "kafka"):
            raise ImportError(f"No module named '{name}'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    # Cloud adapters ImportError
    az = AzureBlobAdapter()
    az.connect()
    assert az.blob_service_client is None
    assert az.write({"a": 1}) is True

    gcs = GCSStorageAdapter()
    gcs.connect()
    assert gcs.client is None
    assert gcs.write({"a": 1}) is True


    # Database adapters ImportError
    mongo = MongoDBAdapter()
    mongo.connect()
    assert mongo.client is None
    assert mongo.write({"a": 1}) is True

    mysql = MySQLAdapter()
    mysql.connect()
    assert mysql.conn is None
    assert mysql.write({"a": 1}) is True

    pg = PostgreSQLAdapter()
    pg.connect()
    assert pg.conn is None
    assert pg.write({"a": 1}) is True

    # Queue adapters ImportError
    rmq = RabbitMQAdapter()
    rmq.connect()
    assert rmq.connection is None
    assert rmq.write({"a": 1}) is True

    kafka = KafkaAdapter()
    kafka.connect()
    assert kafka.producer is None
    assert kafka.write({"a": 1}) is True

    # Close with exception in conn.close()
    mysql_err = MySQLAdapter()
    mock_err_conn = MagicMock()
    mock_err_conn.close.side_effect = Exception("Close failed")
    mysql_err.conn = mock_err_conn
    mysql_err.close()

    pg_err = PostgreSQLAdapter()
    mock_err_pg = MagicMock()
    mock_err_pg.close.side_effect = Exception("Close failed")
    pg_err.conn = mock_err_pg
    pg_err.close()

    rmq_err = RabbitMQAdapter()
    mock_err_rmq = MagicMock()
    mock_err_rmq.close.side_effect = Exception("Close failed")
    rmq_err.connection = mock_err_rmq
    rmq_err.close()


def test_adapter_successful_connect_paths_with_fake_modules(monkeypatch):
    """Cover optional dependency success branches without requiring external services."""
    # boto3 for S3 and DynamoDB
    boto3 = types.ModuleType("boto3")
    boto3_client = MagicMock()
    dynamo_table = MagicMock()
    dynamo_resource = MagicMock()
    dynamo_resource.Table.return_value = dynamo_table
    boto3.client = MagicMock(return_value=boto3_client)
    boto3.resource = MagicMock(return_value=dynamo_resource)
    monkeypatch.setitem(sys.modules, "boto3", boto3)

    s3 = S3StorageAdapter(bucket="b")
    s3.connect()
    assert s3.s3_client is boto3_client
    s3.write({"x": 1})
    boto3_client.put_object.assert_called_once()

    dyn = DynamoDBAdapter(table_name="t")
    dyn.connect()
    assert dyn.table is dynamo_table
    dyn.write(["primitive"])
    dynamo_table.batch_writer.return_value.__enter__.return_value.put_item.assert_called_with(Item={"value": "primitive"})

    # Azure Blob from nested modules
    azure = types.ModuleType("azure")
    azure_storage = types.ModuleType("azure.storage")
    azure_blob = types.ModuleType("azure.storage.blob")
    blob_service = MagicMock()
    blob_service.get_container_client.return_value = MagicMock()
    azure_blob.BlobServiceClient = MagicMock()
    azure_blob.BlobServiceClient.from_connection_string = MagicMock(return_value=blob_service)
    monkeypatch.setitem(sys.modules, "azure", azure)
    monkeypatch.setitem(sys.modules, "azure.storage", azure_storage)
    monkeypatch.setitem(sys.modules, "azure.storage.blob", azure_blob)

    az = AzureBlobAdapter(container_name="c", connection_string="UseDevelopmentStorage=true")
    az.connect()
    assert az.container_client is blob_service.get_container_client.return_value

    # Google Cloud Storage nested import
    google = types.ModuleType("google")
    google_cloud = types.ModuleType("google.cloud")
    storage = types.ModuleType("google.cloud.storage")
    gcs_client = MagicMock()
    storage.Client = MagicMock(return_value=gcs_client)
    google_cloud.storage = storage
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.cloud", google_cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.storage", storage)

    gcs = GCSStorageAdapter(bucket="bucket")
    gcs.connect()
    assert gcs.bucket is gcs_client.bucket.return_value

    # MongoDB
    pymongo = types.ModuleType("pymongo")
    mongo_client = MagicMock()
    pymongo.MongoClient = MagicMock(return_value=mongo_client)
    monkeypatch.setitem(sys.modules, "pymongo", pymongo)

    mongo = MongoDBAdapter(database="db", collection="col")
    mongo.connect()
    assert mongo.collection is mongo_client.__getitem__.return_value.__getitem__.return_value
    mongo.write(["value"])
    mongo.collection.insert_many.assert_called_with([{"value": "value"}])

    # Elasticsearch
    elasticsearch = types.ModuleType("elasticsearch")
    es_client = MagicMock()
    elasticsearch.Elasticsearch = MagicMock(return_value=es_client)
    monkeypatch.setitem(sys.modules, "elasticsearch", elasticsearch)

    es = ElasticsearchAdapter(index="idx")
    es.connect()
    assert es.client is es_client
    es.write(["doc"])
    es_client.index.assert_called_with(index="idx", body={"value": "doc"})

    # RabbitMQ
    pika = types.ModuleType("pika")
    rmq_conn = MagicMock()
    pika.BlockingConnection = MagicMock(return_value=rmq_conn)
    pika.ConnectionParameters = MagicMock(return_value="params")
    pika.BasicProperties = MagicMock(return_value="props")
    monkeypatch.setitem(sys.modules, "pika", pika)

    rmq = RabbitMQAdapter(queue_name="q")
    rmq.connect()
    assert rmq.channel is rmq_conn.channel.return_value
    rmq.write({"a": 1})
    rmq.channel.queue_declare.assert_called_with(queue="q", durable=True)
    rmq.channel.basic_publish.assert_called_once()

    # Kafka
    kafka_mod = types.ModuleType("kafka")
    producer = MagicMock()
    kafka_mod.KafkaProducer = MagicMock(return_value=producer)
    monkeypatch.setitem(sys.modules, "kafka", kafka_mod)

    kafka = KafkaAdapter(topic="topic", bootstrap_servers="host:9092")
    kafka.connect()
    assert kafka.producer is producer
    kafka.write({"event": 1})
    producer.send.assert_called_with("topic", {"event": 1})
