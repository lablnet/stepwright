# helpers.py
# Helper functions for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import asyncio
import pathlib
import random
import re
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from playwright.async_api import Locator, Page

from .step_types import SelectorType

if TYPE_CHECKING:
    from .step_types import BaseStep


def replace_index_placeholders(text: Optional[str], i: int) -> Optional[str]:
    """Replace index placeholders ({{ i }}, {{ i_plus1 }}) in text"""
    if not text:
        return text
    # Convert to string if it's not already a string
    text_str = str(text) if not isinstance(text, str) else text
    return (
        text_str.replace("{{ i }}", str(i))
        .replace("{{i}}", str(i))
        .replace("{{ i_plus1 }}", str(i + 1))
        .replace("{{i_plus1}}", str(i + 1))
    )


def replace_data_placeholders(text: Optional[str], collector: Dict[str, Any]) -> Optional[str]:
    """Replace data placeholders ({{ key }}) in text with values from collector"""
    if not text:
        return text

    def _repl(m: re.Match) -> str:
        key = m.group(1).strip()
        val = collector.get(key, m.group(0))
        if val is None:
            return m.group(0)
        # sanitize for filenames
        s = str(val).strip()
        s = re.sub(r"[^a-zA-Z0-9\s\-_]", "", s)
        s = re.sub(r"\s+", "_", s)
        return s

    return re.sub(r"\{\{\s*([^}]+)\s*\}\}", _repl, text)


def locator_for(context, type: Optional[SelectorType], selector: str) -> Locator:
    """
    Create a Playwright locator based on selector type.
    Context can be either a Page or a Locator (for scoped queries).
    """
    if not type:
        return context.locator(selector)
    if type == "id":
        return context.locator(f"#{selector}")
    if type == "class":
        return context.locator(f".{selector}")
    if type == "tag":
        return context.locator(selector)
    if type == "xpath":
        return context.locator(f"xpath={selector}")
    return context.locator(selector)


async def _ensure_dir(path_str: str) -> None:
    """Ensure directory exists for given file path"""
    pathlib.Path(path_str).parent.mkdir(parents=True, exist_ok=True)


async def maybe_await(x):
    """Await if coroutine, otherwise return as-is"""
    if asyncio.iscoroutine(x):
        return await x
    return x


def flatten_nested_foreach_results(item: Dict[str, Any]) -> Any:
    """
    Flatten nested foreach results into an array.
    
    If the item contains nested item_* keys (from nested foreach loops),
    flatten them into an array. Otherwise, return the item as-is.
    
    Args:
        item: Dictionary that may contain nested item_* keys
        
    Returns:
        Either a flattened array of items or the original item
    """
    # Check if item contains nested item_* keys (from nested foreach)
    nested_item_keys = [k for k in item.keys() if k.startswith("item_")]
    if nested_item_keys:
        # Flatten nested items into an array
        flattened_items = []
        for k in sorted(nested_item_keys, key=lambda x: int(x.split('_')[1])):
            if item[k] and len(item[k]) > 0:
                flattened_items.append(item[k])
        return flattened_items
    else:
        # No nested items, return item as is
        return item


async def evaluate_condition(page: Page, condition: str, collector: Dict[str, Any]) -> bool:
    """Evaluate JavaScript condition with collector data available"""
    try:
        # Replace collector placeholders in condition
        condition_with_data = replace_data_placeholders(condition, collector) or condition
        result = await page.evaluate(f"() => {condition_with_data}")
        return bool(result)
    except Exception as e:
        print(f"   ⚠️  Condition evaluation failed: {condition} - {e}")
        return False


async def find_locator_with_fallbacks(
    page: Page,
    scope_locator: Optional[Locator],
    object_type: Optional[SelectorType],
    object_selector: str,
    fallback_selectors: Optional[List[Dict[str, str]]],
) -> Tuple[Optional[Locator], Optional[str], Optional[str]]:
    """
    Try to find locator, using fallback selectors if primary fails.
    
    Returns:
        Tuple of (locator, used_object_type, used_object) or (None, None, None) if all fail
    """
    context = scope_locator if scope_locator else page
    
    # Try primary selector first
    loc = locator_for(context, object_type, object_selector)
    if await loc.count() > 0:
        return loc, object_type, object_selector
    
    # Try fallback selectors
    if fallback_selectors:
        for fallback in fallback_selectors:
            fb_type = fallback.get("object_type")
            fb_selector = fallback.get("object")
            if fb_type and fb_selector:
                fb_loc = locator_for(context, fb_type, fb_selector)
                if await fb_loc.count() > 0:
                    print(f"   ✅ Using fallback selector: {fb_type}={fb_selector}")
                    return fb_loc, fb_type, fb_selector
    
    return None, None, None


async def apply_random_delay(page: Page, random_delay: Optional[Dict[str, int]]) -> None:
    """Apply random delay before action if configured"""
    if random_delay:
        min_delay = random_delay.get("min", 0)
        max_delay = random_delay.get("max", 0)
        if max_delay > min_delay:
            delay = random.randint(min_delay, max_delay)
            await page.wait_for_timeout(delay)


def transform_data_regex(value: Any, regex: Optional[str], regex_group: Optional[int]) -> Any:
    """Apply regex extraction to data"""
    if not regex or not value:
        return value
    
    try:
        match = re.search(regex, str(value))
        if match:
            group_idx = regex_group if regex_group is not None else 0
            if group_idx < len(match.groups()) + 1:
                return match.group(group_idx)
            else:
                return match.group(0)
    except Exception as e:
        print(f"   ⚠️  Regex extraction failed: {e}")
    
    return value


async def wait_for_selector_if_configured(
    page: Page,
    step: "BaseStep",
    scope_locator: Optional[Locator],
) -> None:
    """Wait for selector if waitForSelector is configured in step"""
    if not step.waitForSelector:
        return
    
    wait_timeout = step.waitForSelectorTimeout or 30000
    wait_state = step.waitForSelectorState or "visible"
    
    try:
        wait_loc = locator_for(
            scope_locator if scope_locator else page,
            step.object_type,
            step.waitForSelector
        )
        await wait_loc.wait_for(state=wait_state, timeout=wait_timeout)
    except Exception:
        pass  # Continue even if wait fails


async def apply_transform(page: Page, value: Any, transform: Optional[str], collector: Dict[str, Any]) -> Any:
    """Apply JavaScript transformation to value"""
    if not transform or value is None:
        return value
    
    try:
        # Replace collector placeholders in transform expression
        transform_with_data = replace_data_placeholders(transform, collector) or transform
        # Evaluate transform with value available as 'value'
        result = await page.evaluate(f"(value) => {transform_with_data}", value)
        return result
    except Exception as e:
        print(f"   ⚠️  Transform failed: {e}")
        return value
