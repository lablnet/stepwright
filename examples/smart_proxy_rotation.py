# examples/smart_proxy_rotation.py
# Example demonstrating Smart Proxy Rotation & Auto-Healing Proxy Pool

import asyncio
from stepwright import (
    ProxyPool,
    ProxyConfig,
    TabTemplate,
    BaseStep,
    RunOptions,
    run_scraper,
    validate_template_format,
)


async def main():
    # Initialize ProxyPool with multiple proxies and round_robin rotation strategy
    proxy_pool = ProxyPool(
        proxies=[
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            ProxyConfig(server="http://proxy3.example.com:8080", username="user", password="pass"),
        ],
        strategy="round_robin",
        max_failures=2,
        cooldown_seconds=60,
    )

    print(f"📊 Initial Proxy Pool Stats: {proxy_pool.get_stats()}")

    # Define scraping templates
    template = TabTemplate(
        tab="proxy_rotation_demo",
        proxy_pool=proxy_pool,
        steps=[
            BaseStep(
                id="nav",
                action="navigate",
                value="https://example.com",
            ),
            BaseStep(
                id="extract_title",
                action="data",
                object="h1",
                key="title",
            ),
        ],
    )

    val_res = validate_template_format(template)
    print(f"✅ Template valid: {val_res.is_valid}")

    options = RunOptions(
        browser={"headless": True},
    )

    print("🚀 Launching scraper with ProxyPool...")
    results = await run_scraper([template], options)
    print(f"📊 Results: {results}")

    # Demonstrate proxy reporting & failure cooling
    print("\n⚠️ Simulating proxy failure reporting...")
    proxy_pool.report_failure("http://proxy1.example.com:8080", reason="HTTP 429 Too Many Requests")
    proxy_pool.report_failure("http://proxy1.example.com:8080", reason="HTTP 429 Too Many Requests")

    print(f"📊 Updated Proxy Pool Stats after failure threshold: {proxy_pool.get_stats()}")


if __name__ == "__main__":
    asyncio.run(main())
