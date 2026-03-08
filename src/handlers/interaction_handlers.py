# handlers/interaction_handlers.py
# Advanced interaction handlers for StepWright (Hover, Select, Drag&Drop, Virtual Scroll, Upload)
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING, Callable

from playwright.async_api import Locator, Page

from ..helpers import (
    find_locator_with_fallbacks,
    wait_for_selector_if_configured,
    replace_data_placeholders,
)

if TYPE_CHECKING:
    from ..step_types import BaseStep


async def _handle_hover(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Locator] = None,
) -> None:
    """Handle hover action"""
    await wait_for_selector_if_configured(page, step, scope_locator)
    loc, _, selector = await find_locator_with_fallbacks(
        page, scope_locator, step.object_type, step.object or "", step.fallbackSelectors
    )
    if loc and await loc.count() > 0:
        await loc.first.hover()
        print(f"   🖱️  Hovered over: {selector}")
    else:
        print(f"   ⚠️  Hover element not found: {step.object}")


async def _handle_select(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Locator] = None,
) -> None:
    """Handle select/multi-select action"""
    await wait_for_selector_if_configured(page, step, scope_locator)
    loc, _, selector = await find_locator_with_fallbacks(
        page, scope_locator, step.object_type, step.object or "", step.fallbackSelectors
    )
    if loc and await loc.count() > 0:
        value = replace_data_placeholders(step.value, collector) or step.value
        # Split value by comma if it looks like a list for multi-select
        # or if it's already a list (passed as such in some contexts)
        final_value = value
        if isinstance(value, str) and "," in value:
            final_value = [v.strip() for v in value.split(",")]

        await loc.first.select_option(final_value)
        print(f"   ✅ Selected options for: {selector} -> {final_value}")
    else:
        print(f"   ⚠️  Select element not found: {step.object}")


async def _handle_drag_and_drop(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Locator] = None,
) -> None:
    """Handle drag and drop action"""
    await wait_for_selector_if_configured(page, step, scope_locator)

    # Find source
    src_loc, _, src_selector = await find_locator_with_fallbacks(
        page, scope_locator, step.object_type, step.object or "", step.fallbackSelectors
    )

    # Find target
    target_loc, _, target_selector = await find_locator_with_fallbacks(
        page, scope_locator, step.targetObjectType, step.targetObject or "", None
    )

    if (
        src_loc
        and target_loc
        and await src_loc.count() > 0
        and await target_loc.count() > 0
    ):
        # Hover first, then drag
        await src_loc.first.hover()
        await src_loc.first.drag_to(target_loc.first)

        # Small wait for JS events and DOM to update
        await page.wait_for_timeout(1000)
        print(f"   🤝 Dragged {src_selector} to {target_selector}")
    else:
        print(
            f"   ⚠️  Drag/Drop elements not found: {step.object} -> {step.targetObject}"
        )


async def _handle_upload(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Locator] = None,
) -> None:
    """Handle file upload action"""
    await wait_for_selector_if_configured(page, step, scope_locator)
    loc, _, selector = await find_locator_with_fallbacks(
        page, scope_locator, step.object_type, step.object or "", step.fallbackSelectors
    )
    if loc and await loc.count() > 0:
        file_path = replace_data_placeholders(step.value, collector) or step.value
        if file_path:
            await loc.first.set_input_files(file_path)
            print(f"   📤 Uploaded file to: {selector} -> {file_path}")
    else:
        print(f"   ⚠️  Upload element not found: {step.object}")


async def _handle_virtual_scroll(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    execute_step_internal: Callable,
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
    scope_locator: Optional[Locator] = None,
) -> None:
    """Handle virtual scroll looping action"""
    print(f"   🌀 Starting virtual scroll for: {step.object}")

    unique_key = step.virtualScrollUniqueKey
    limit = step.virtualScrollLimit or 1000
    offset = step.virtualScrollOffset or 500
    delay = step.virtualScrollDelay or 1000

    seen_ids = set()
    total_collected = 0
    no_new_item_count = 0
    max_no_new_items = 3  # Stop after 3 scrolls with no new items

    # Extract collector key
    key = step.key or step.id or "items"
    if key not in collector:
        collector[key] = []

    while total_collected < limit:
        # Find items currently in DOM
        loc, _, _ = await find_locator_with_fallbacks(
            page,
            scope_locator,
            step.object_type,
            step.object or "",
            step.fallbackSelectors,
        )

        count = await loc.count()
        new_items_this_round = 0

        for i in range(count):
            item_loc = loc.nth(i)

            # Use a temporary collector for this item
            item_data: Dict[str, Any] = {}
            if step.subSteps:
                for sub in step.subSteps:
                    await execute_step_internal(page, sub, item_data, None, item_loc)

            # Use uniqueKey for deduplication
            item_id = str(item_data.get(unique_key)) if unique_key else str(item_data)

            if item_id not in seen_ids:
                seen_ids.add(item_id)
                collector[key].append(item_data)
                total_collected += 1
                new_items_this_round += 1

                # Stream results if callback provided
                if on_result:
                    await on_result(item_data, total_collected - 1)

                if total_collected >= limit:
                    break

        if new_items_this_round == 0:
            no_new_item_count += 1
        else:
            no_new_item_count = 0

        if no_new_item_count >= max_no_new_items:
            print(
                f"   🛑 No new items found after {max_no_new_items} scrolls, finishing."
            )
            break

        # Scroll down
        if step.virtualScrollContainer:
            # Scroll specific container
            container_loc, _, _ = await find_locator_with_fallbacks(
                page,
                scope_locator,
                step.virtualScrollContainerType,
                step.virtualScrollContainer,
                None,
            )
            if container_loc and await container_loc.count() > 0:
                await container_loc.first.evaluate(f"el => el.scrollBy(0, {offset})")
            else:
                print(
                    f"   ⚠️  Virtual scroll container not found: {step.virtualScrollContainer}"
                )
                break
        else:
            # Scroll page
            await page.mouse.wheel(0, offset)

        await page.wait_for_timeout(delay)

    print(f"   ✅ Virtual scroll finished. Collected {total_collected} items.")
