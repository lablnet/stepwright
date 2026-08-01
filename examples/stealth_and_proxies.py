# examples/stealth_and_proxies.py
# Example demonstrating Stealth Anti-Bot Evasion, Proxy Configuration, and CAPTCHA hooks

import asyncio
from stepwright import (
    run_scraper,
    TabTemplate,
    BaseStep,
    RunOptions,
    ProxyConfig,
    validate_template_format,
)


def handle_captcha_challenge(page, collector):
    print("   🚨 Custom CAPTCHA handler invoked!")
    collector["captcha_handled"] = True


async def main():
    # 1. Define stealth workflow template with Proxy and CAPTCHA detection hook
    template = TabTemplate(
        tab="stealth_demo",
        stealth=True,  # Enables automated fingerprint evasion scripts
        # Proxy configuration (HTTP or SOCKS5 with authentication)
        proxy=ProxyConfig(
            server="http://my-proxy-server:8080",
            username="my_username",
            password="my_password",
        ),
        captcha_selector=".g-recaptcha",
        on_captcha=handle_captcha_challenge,
        steps=[
            BaseStep(
                id="nav",
                action="navigate",
                value="https://nowsecure.nl",
            ),
            BaseStep(
                id="title",
                action="getTitle",
                key="page_title",
            ),
        ],
    )

    # Validate template format before running
    res = validate_template_format(template)
    print(f"✅ Template validation result: {res.is_valid}")

    # 2. Configure global stealth options
    options = RunOptions(
        stealth=True,
        browser={"headless": True},
        collect_metrics=True,
    )

    print("🚀 Launching scraper with Stealth & Anti-Bot Evasion...")
    results = await run_scraper([template], options)
    print(f"📊 Execution results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
