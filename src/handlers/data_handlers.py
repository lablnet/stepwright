# handlers/data_handlers.py
# Data extraction handlers for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from playwright.async_api import Locator, Page

from ..step_types import BaseStep
from ..helpers import (
    locator_for,
    wait_for_selector_if_configured,
    find_locator_with_fallbacks,
    transform_data_regex,
    apply_transform,
)


async def _handle_data_extraction(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Locator] = None,
) -> None:
    """Handle data extraction action with all enhancements"""
    check_selector = step.object or ""
    if step.data_type == "attribute" and re.search(r"/@\w+$", check_selector):
        check_selector = re.sub(r"/@\w+$", "", check_selector)

    # Wait for selector if configured
    await wait_for_selector_if_configured(page, step, scope_locator)

    # Find locator with fallbacks
    loc, used_type, used_selector = await find_locator_with_fallbacks(
        page,
        scope_locator,
        step.object_type,
        check_selector,
        step.fallbackSelectors
    )

    if not loc or await loc.count() == 0:
        key = step.key or step.id or "data"
        if step.required:
            raise ValueError(f"Required element not found: {check_selector}")
        val = step.defaultValue
        collector[key] = val
        if step.continueOnEmpty is False:
            raise ValueError(f"Element not found: {check_selector}")
        print(f"   ⚠️  Element not found: {check_selector} - using default")
        return

    # Extract data from the scoped locator
    if step.data_type == "text":
        val = await loc.first.text_content()
    elif step.data_type == "html":
        val = await loc.first.inner_html()
    elif step.data_type == "value":
        val = await loc.first.input_value()
    elif step.data_type == "attribute":
        attr_match = re.search(r"/@(\w+)$", step.object or "")
        if attr_match:
            attr_name = attr_match.group(1)
            val = await loc.first.get_attribute(attr_name)
        else:
            val = await loc.first.text_content()
    else:  # default
        val = await loc.first.text_content()

    # Apply regex extraction
    if val:
        val = transform_data_regex(val, step.regex, step.regexGroup)
    
    # Apply JavaScript transformation
    if val is not None:
        val = await apply_transform(page, val, step.transform, collector)

    # Validate required field
    if step.required and (val is None or val == ""):
        raise ValueError(f"Required data field is empty: {step.key or step.id}")

    # Use default value if extraction failed
    if val is None or val == "":
        val = step.defaultValue

    # Wait after extraction if configured
    if step.wait and step.wait > 0:
        await page.wait_for_timeout(step.wait)

    key = step.key or step.id or "data"
    collector[key] = val
    print(f"Step Data: {key}: {val}")

