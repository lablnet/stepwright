# handlers/network_handlers.py
# Network and API request interception handlers for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from playwright.async_api import Page, Response

from ..step_types import BaseStep
from ..helpers import replace_data_placeholders


import asyncio


async def _handle_intercept(
    page: Page, step: BaseStep, collector: Dict[str, Any]
) -> None:
    """
    Handle network/API request interception.
    Registers a response listener on page matching pattern in step.object or step.value.
    Stores extracted body (json/text) into collector[key or step.id].

    @since 2.0.0
    """
    url_pattern = replace_data_placeholders(
        step.object or step.value or "", collector
    )
    if not url_pattern:
        raise ValueError(
            f"intercept step '{step.id}' requires a target URL pattern in 'object' or 'value'"
        )

    key = step.key or step.id or "intercepted_data"
    fmt = step.data_type or "json"
    target_method = (step.value if step.object else None) or None

    print(f"   📡 Registering network intercept listener for: {url_pattern}")

    def predicate(res: Response) -> bool:
        if target_method and res.request.method.upper() != target_method.upper():
            return False
        # Regex or string match
        if url_pattern.startswith("^") or "*" in url_pattern:
            pattern_regex = (
                url_pattern.replace(".", r"\.").replace("*", ".*")
                if not url_pattern.startswith("^")
                else url_pattern
            )
            return bool(re.search(pattern_regex, res.url, re.IGNORECASE))
        return url_pattern.lower() in res.url.lower()

    async def on_response(response: Response):
        if predicate(response):
            try:
                if fmt == "json":
                    try:
                        content = await response.json()
                    except Exception:
                        raw_text = await response.text()
                        try:
                            content = json.loads(raw_text)
                        except Exception:
                            content = raw_text
                elif fmt == "text":
                    content = await response.text()
                elif fmt == "bytes":
                    content = await response.body()
                else:
                    content = await response.text()

                if step.regex and content and isinstance(content, str):
                    from ..helpers import transform_data_regex

                    content = transform_data_regex(content, step.regex, step.regexGroup)

                collector[key] = content
                print(
                    f"   ✅ Intercepted response from {response.url} -> stored in collector['{key}']"
                )
            except Exception as e:
                print(f"   ⚠️ Intercept extraction failed: {e}")

    page.on("response", lambda res: asyncio.create_task(on_response(res)))


async def setup_resource_blocking(
    page: Page, block_resources: Optional[List[str]]
) -> None:
    """
    Set up route interception on page to abort requests for specified resource types.
    e.g. block_resources = ["image", "stylesheet", "font", "media", "script"]
    """
    if not block_resources:
        return

    blocked_types = {r.lower() for r in block_resources}
    print(f"   🛡️ Setting up resource blocking for types: {list(blocked_types)}")

    async def route_handler(route):
        req_type = route.request.resource_type.lower()
        if req_type in blocked_types:
            await route.abort()
        else:
            await route.continue_()

    await page.route("**/*", route_handler)
