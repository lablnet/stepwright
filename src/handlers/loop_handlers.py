# loop_handlers.py
# Loop and tab handling for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import pathlib
from typing import Any, Callable, Dict, Optional

from playwright.async_api import Page

from ..step_types import BaseStep
from ..helpers import locator_for, replace_index_placeholders, flatten_nested_foreach_results, maybe_await


async def _handle_foreach(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    execute_step_fn: Callable,  # Will be execute_step from executor
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
) -> None:
    """Handle foreach loop action"""
    if not step.object:
        raise ValueError("foreach step requires object as locator")
    if not step.subSteps:
        raise ValueError("foreach step requires subSteps")

    loc_all = locator_for(page, step.object_type, step.object)
    try:
        await loc_all.first.wait_for(state="attached", timeout=step.wait or 5000)
    except Exception:
        pass

    count = await loc_all.count()
    print(f"   🔁 foreach found {count} items for selector {step.object}")

    for idx in range(count):
        current = loc_all.nth(idx)
        if step.autoScroll is not False:
            try:
                await current.scroll_into_view_if_needed()
            except Exception:
                pass

        # independent result per item
        item_collector: Dict[str, Any] = {}

        for s in step.subSteps or []:
            cloned = clone_step_with_index(s, idx)
            try:
                await execute_step_fn(page, cloned, item_collector, on_result, scope_locator=current)
            except Exception as e:
                print(f"⚠️  sub-step '{cloned.id}' failed: {e}")
                if cloned.terminateonerror:
                    raise

        collector[f"item_{idx}"] = item_collector

        if item_collector:
            print(f"   📋 Collected data for item {idx}: {list(item_collector.keys())}")
            # Call callback immediately for each foreach item (like TypeScript version)
            # Flatten nested foreach results into an array
            if on_result:
                try:
                    flattened_result = flatten_nested_foreach_results(item_collector)
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
                    str(pathlib.PurePosixPath(str(page.url))).rstrip("/") + "/" + href.lstrip("/")
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


def clone_step_with_index(step: BaseStep, idx: int) -> BaseStep:
    """Clone a step with index placeholders replaced"""
    cloned = BaseStep(**{**step.__dict__})
    # Only replace placeholders in string fields.
    if cloned.object and isinstance(cloned.object, str):
        cloned.object = replace_index_placeholders(cloned.object, idx)
    if cloned.value and isinstance(cloned.value, str):
        cloned.value = replace_index_placeholders(cloned.value, idx)
    if cloned.key and isinstance(cloned.key, str):
        cloned.key = replace_index_placeholders(cloned.key, idx)
    if cloned.subSteps:
        cloned.subSteps = [clone_step_with_index(s, idx) for s in cloned.subSteps]
    return cloned

