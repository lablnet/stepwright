# loop_handlers.py
# Loop and tab handling for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import pathlib
import re
from typing import Any, Callable, Dict, Optional

from playwright.async_api import Page

from ..step_types import BaseStep
from ..helpers import (
    locator_for,
    replace_index_placeholders,
    flatten_nested_foreach_results,
    maybe_await,
)


async def _handle_foreach(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    execute_step_fn: Callable,  # Will be execute_step from executor
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
) -> None:
    """Handle foreach loop action"""
    count = 0
    items_to_loop = []

    if step.object:
        loc_all = locator_for(page, step.object_type, step.object)
        try:
            await loc_all.first.wait_for(state="attached", timeout=step.wait or 5000)
        except Exception:
            pass
        count = await loc_all.count()
        items_to_loop = [
            (loc_all.nth(i), None) for i in range(count)
        ]  # (locator, data)
        print(f"   🔁 foreach found {count} items for selector {step.object}")
    elif step.value:
        # Check for list in collector via placeholder e.g. {{keywords}}
        placeholder_match = re.search(r"\{\{([\w\-]+)\}\}", step.value)
        if placeholder_match:
            placeholder_key = placeholder_match.group(1)
            actual_data = collector.get(placeholder_key)

            if isinstance(actual_data, list):
                items_to_loop = [(None, item) for item in actual_data]
                count = len(items_to_loop)
                print(f"   🔁 foreach found {count} items from source {step.value}")
            else:
                print(
                    f"   ⚠️  foreach source {step.value} (key: {placeholder_key}) is not a list or not found"
                )
                return
        else:
            print(
                f"   ⚠️  foreach step.value '{step.value}' does not contain a valid placeholder {{key}}"
            )
            return
    else:
        raise ValueError(
            "foreach step requires either 'object' (locator) or 'value' (data source)"
        )

    if not step.subSteps:
        raise ValueError("foreach step requires subSteps")

    for idx, (current_locator, current_data) in enumerate(items_to_loop):
        if current_locator and step.autoScroll is not False:
            try:
                await current_locator.scroll_into_view_if_needed()
            except Exception:
                pass

        # independent result per item
        # Create a separate collector for each iteration
        # Initialize with parent context (non-item_* keys) to preserve metadata
        item_collector: Dict[str, Any] = {}
        for k, v in collector.items():
            if not re.match(r"^item_\d+$", k):
                item_collector[k] = v

        # Use the specified index key or default to 'i'
        index_key = step.index_key or "i"

        for s in step.subSteps or []:
            cloned = clone_step_with_index(s, idx, index_key)

            # If we are looping over raw data, inject the current item into the collector
            if not step.object:
                item_collector["item"] = current_data
                if isinstance(current_data, dict):
                    item_collector.update(current_data)

            try:
                await execute_step_fn(
                    page,
                    cloned,
                    item_collector,
                    on_result,
                    scope_locator=current_locator,
                )
            except Exception as e:
                print(f"⚠️  sub-step '{cloned.id}' failed: {e}")
                if cloned.terminateonerror:
                    raise

        # Store the item collector
        if step.key:
            if step.key not in collector or not isinstance(collector[step.key], list):
                collector[step.key] = []

            # Flatten if there are nested item_* keys before storing under the key
            result_to_store = flatten_nested_foreach_results(item_collector)

            if isinstance(result_to_store, list):
                collector[step.key].extend(result_to_store)
            else:
                # If it's a single object, clean it of parent metadata before pushing
                # this keeps nested objects clean and avoids redundant data
                parent_keys = {
                    k for k in collector.keys() if not re.match(r"^item_\d+$", k)
                }
                cleaned_item: Dict[str, Any] = {}
                for k, v in item_collector.items():
                    if k not in parent_keys or k == index_key:
                        cleaned_item[k] = v
                collector[step.key].append(cleaned_item)
        else:
            collector[f"item_{idx}"] = item_collector

            if item_collector:
                print(
                    f"   📋 Collected data for item {idx}: {list(item_collector.keys())}"
                )
                # Call callback immediately for each foreach item (like TypeScript version)
                # Flatten nested foreach results into an array
                if on_result:
                    try:
                        flattened_result = flatten_nested_foreach_results(
                            item_collector
                        )
                        await maybe_await(on_result(flattened_result, idx))
                    except Exception as e:
                        print(f"   ⚠️  Callback failed for item {idx}: {e}")


async def _handle_open(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    execute_step_fn: Callable,  # Will be execute_step from executor
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
) -> None:
    """Handle open link/tab action"""
    if not step.object:
        raise ValueError("open step requires object locator")
    if not step.subSteps:
        raise ValueError("open step needs subSteps")

    print(f"   🔗 Opening link/tab from selector {step.object}")
    try:
        link_loc = locator_for(page, step.object_type, step.object)
        if await link_loc.count() == 0:
            print(f"   ⚠️  Element not found: {step.object} - skipping open")
            return

        href = await link_loc.get_attribute("href")
        ctx = page.context
        new_page: Optional[Page] = None

        if href:
            if not href.startswith("http"):
                href = str(pathlib.PurePosixPath(href))
                href = (
                    str(pathlib.PurePosixPath(str(page.url))).rstrip("/")
                    + "/"
                    + href.lstrip("/")
                )
            new_page = await ctx.new_page()
            await new_page.goto(href, wait_until="networkidle")
        else:
            page_promise = ctx.wait_for_event("page")
            try:
                await link_loc.click(modifiers=["Meta"])
            except Exception:
                await link_loc.click()
            new_page = await page_promise
            await new_page.wait_for_load_state("networkidle")

        inner = dict(collector)  # pass parent data in
        for s in step.subSteps:
            cloned = BaseStep(**{**s.__dict__})
            try:
                await execute_step_fn(new_page, cloned, inner, on_result)
            except Exception as e:
                print(f"   ⚠️  Sub-step in open failed: {e}")
                if cloned.terminateonerror:
                    raise

        collector.update(inner)
        print("   🔙 Closed child tab")
        await new_page.close()
    except Exception as e:
        print(f"   ⚠️  Open action failed for {step.object}: {e}")
        if step.terminateonerror:
            raise


def clone_step_with_index(step: BaseStep, idx: int, char: str = "i") -> BaseStep:
    """Clone a step with index placeholders replaced"""
    cloned = BaseStep(**{**step.__dict__})
    # Only replace placeholders in string fields.
    if cloned.object and isinstance(cloned.object, str):
        cloned.object = replace_index_placeholders(cloned.object, idx, char)
    if cloned.value and isinstance(cloned.value, str):
        cloned.value = replace_index_placeholders(cloned.value, idx, char)
    if cloned.key and isinstance(cloned.key, str):
        cloned.key = replace_index_placeholders(cloned.key, idx, char)
    if cloned.subSteps:
        cloned.subSteps = [clone_step_with_index(s, idx, char) for s in cloned.subSteps]
    return cloned
