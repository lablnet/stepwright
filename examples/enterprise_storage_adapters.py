# examples/enterprise_storage_adapters.py
# Example demonstrating Pluggable Enterprise Storage Adapters in StepWright

import asyncio
from stepwright import (
    TabTemplate,
    BaseStep,
    RunOptions,
    run_scraper,
    SQLiteAdapter,
    S3StorageAdapter,
    BaseStorageAdapter,
    register_adapter,
)


class CustomWebhookAdapter(BaseStorageAdapter):
    """Custom storage adapter extending BaseStorageAdapter"""

    def __init__(self, endpoint_url: str = "https://api.example.com/webhook"):
        self.endpoint_url = endpoint_url

    def connect(self) -> None:
        pass

    def write(self, data, options=None) -> bool:
        print(f"   🌐 [CustomWebhookAdapter] Posting data payload to {self.endpoint_url}")
        return True

    def close(self) -> None:
        pass


async def main():
    # Register custom adapter name
    register_adapter("webhook", CustomWebhookAdapter)

    # Instantiate adapters
    sqlite_adapter = SQLiteAdapter(db_path="scraped_data.db", table_name="articles")
    s3_adapter = S3StorageAdapter(bucket="my-company-data-lake", key_prefix="scraped_news/")
    custom_adapter = CustomWebhookAdapter(endpoint_url="https://hooks.slack.com/services/custom")

    # Define scraping workflow with multi-adapter exports
    template = TabTemplate(
        tab="storage_demo",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(id="title", action="data", object="h1", key="heading"),
            # Export via SQLite adapter
            BaseStep(
                id="save_db",
                action="writeData",
                key="heading",
                storage_adapter=sqlite_adapter,
            ),
            # Export via S3 adapter
            BaseStep(
                id="save_cloud",
                action="writeData",
                key="heading",
                storage_adapter=s3_adapter,
            ),
            # Export via custom webhook adapter
            BaseStep(
                id="save_webhook",
                action="writeData",
                key="heading",
                storage_adapter=custom_adapter,
            ),
        ],
    )

    options = RunOptions(browser={"headless": True})

    print("🚀 Launching scraper with Enterprise Storage Adapters...")
    results = await run_scraper([template], options)
    print(f"📊 Execution results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
