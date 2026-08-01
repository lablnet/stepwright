# Pluggable Enterprise Storage Adapters

StepWright 2.0.0 features a **Pluggable Enterprise Storage Adapter Architecture** (`BaseStorageAdapter`). 

Just like StepWright's Pluggable Driver Architecture, the Storage Adapter system allows you to export scraped records directly to SQL databases, NoSQL document stores, Cloud Object Stores, Message Queues, or custom external sinks without writing manual boilerplate code.

---

## 🏗️ Supported Storage Adapters

StepWright includes 14 built-in storage adapters out of the box:

| Category | Adapter Class | Identifier | Description |
| :--- | :--- | :--- | :--- |
| **Relational DB** | `SQLiteAdapter` | `"sqlite"` | Built-in SQLite database writer (creates tables automatically) |
| **Relational DB** | `PostgreSQLAdapter` | `"postgres"` | PostgreSQL database stream writer |
| **Relational DB** | `MySQLAdapter` | `"mysql"` | MySQL database stream writer |
| **NoSQL DB** | `MongoDBAdapter` | `"mongo"` | MongoDB document collection writer |
| **NoSQL DB** | `DynamoDBAdapter` | `"dynamodb"` | AWS DynamoDB item writer |
| **Search Engine** | `ElasticsearchAdapter` | `"elasticsearch"` | Elasticsearch document indexer |
| **Cloud Storage** | `S3StorageAdapter` | `"s3"` | AWS S3 object bucket exporter |
| **Cloud Storage** | `GCSStorageAdapter` | `"gcs"` | Google Cloud Storage bucket exporter |
| **Cloud Storage** | `AzureBlobAdapter` | `"azure"` | Azure Blob Storage container exporter |
| **Message Queue** | `RabbitMQAdapter` | `"rabbitmq"` | RabbitMQ / AMQP message publisher |
| **Message Queue** | `KafkaAdapter` | `"kafka"` | Apache Kafka topic event publisher |
| **File Systems** | `JSONFileAdapter` | `"json"` | Local `.json` file exporter |
| **File Systems** | `CSVFileAdapter` | `"csv"` | Local `.csv` file exporter |
| **File Systems** | `XMLFileAdapter` | `"xml"` | Local `.xml` file exporter |

---

## 🚀 Basic Usage

```python
import asyncio
from stepwright import (
    TabTemplate,
    BaseStep,
    RunOptions,
    run_scraper,
    SQLiteAdapter,
    S3StorageAdapter,
)

async def main():
    # Instantiate enterprise storage adapters
    sqlite_db = SQLiteAdapter(db_path="scraped.db", table_name="articles")
    s3_cloud = S3StorageAdapter(bucket="company-data-lake", key_prefix="scraped_news/")

    template = TabTemplate(
        tab="storage_demo",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(id="title", action="data", object="h1", key="heading"),
            # Export data via SQLite Adapter
            BaseStep(
                id="save_db",
                action="writeData",
                key="heading",
                storage_adapter=sqlite_db,
            ),
            # Export data via S3 Adapter
            BaseStep(
                id="save_cloud",
                action="writeData",
                key="heading",
                storage_adapter=s3_cloud,
            ),
        ],
    )

    options = RunOptions(browser={"headless": True})
    results = await run_scraper([template], options)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🛠️ Creating Custom Storage Adapters

You can implement custom storage backends by extending `BaseStorageAdapter`:

```python
from stepwright import BaseStorageAdapter, register_adapter

class WebhookStorageAdapter(BaseStorageAdapter):
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def connect(self) -> None:
        pass

    def write(self, data, options=None) -> bool:
        print(f"📡 [WebhookStorageAdapter] Posting payload to {self.endpoint_url}")
        return True

    def close(self) -> None:
        pass

# Optional: Register string alias for the custom adapter
register_adapter("webhook", WebhookStorageAdapter)
```
