# executor.py
# Core execution logic for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import pathlib
import re
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse, urljoin, urlencode, parse_qs

from playwright.async_api import Page
from playwright.async_api import async_playwright

from .step_types import BaseStep, PaginationConfig, TabTemplate
from .helpers import (
    locator_for,
    replace_index_placeholders,
    replace_data_placeholders,
    _ensure_dir,
    maybe_await,
    flatten_nested_foreach_results,
    evaluate_condition,
    find_locator_with_fallbacks,
    apply_random_delay,
    transform_data_regex,
    apply_transform,
    wait_for_selector_if_configured,
)
from .scraper import (
    navigate,
    input as input_action,
    click as click_action,
)
from .handlers import (
    # Data handlers
    _handle_data_extraction,
    # File handlers
    _handle_event_download,
    _handle_save_pdf,
    _handle_download_pdf,
    # Loop handlers
    _handle_foreach,
    _handle_open,
    clone_step_with_index,
    # Page action handlers
    _handle_reload,
    _handle_get_url,
    _handle_get_title,
    _handle_get_meta,
    _handle_get_cookies,
    _handle_set_cookies,
    _handle_get_local_storage,
    _handle_set_local_storage,
    _handle_get_session_storage,
    _handle_set_session_storage,
    _handle_get_viewport_size,
    _handle_set_viewport_size,
    _handle_screenshot,
    _handle_wait_for_selector,
    _handle_evaluate,
)


async def execute_step(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
    scope_locator: Optional[Any] = None,  # Locator to scope searches within
) -> None:
    """Execute a single scraping step"""
    print(f"➡️  Step `{step.id}` ({step.action})")

    # Check conditional execution
    if step.skipIf:
        if await evaluate_condition(page, step.skipIf, collector):
            print(f"   ⏭️  Skipping step (skipIf condition true)")
            return
    
    if step.onlyIf:
        if not await evaluate_condition(page, step.onlyIf, collector):
            print(f"   ⏭️  Skipping step (onlyIf condition false)")
            return

    # Apply random delay if configured
    await apply_random_delay(page, step.randomDelay)

    # Retry wrapper
    retry_count = step.retry or 0
    retry_delay = step.retryDelay or 1000
    
    for attempt in range(retry_count + 1):
        try:
            await _execute_step_internal(page, step, collector, on_result, scope_locator)
            return  # Success, exit retry loop
        except Exception as e:
            if attempt < retry_count:
                print(f"   🔄 Retry {attempt + 1}/{retry_count} after {retry_delay}ms: {e}")
                await page.wait_for_timeout(retry_delay)
            else:
                raise  # Re-raise on final attempt


async def _execute_step_internal(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
    scope_locator: Optional[Any] = None,
) -> None:
    """Internal step execution (called by retry wrapper)"""
    try:
        if step.action == "navigate":
            await navigate(page, step.value or "")

        elif step.action == "input":
            # Wait for selector if configured
            await wait_for_selector_if_configured(page, step, scope_locator)

            # Find locator with fallbacks
            loc, used_type, used_selector = await find_locator_with_fallbacks(
                page,
                scope_locator,
                step.object_type,
                step.object or "",
                step.fallbackSelectors
            )
            
            if not loc or await loc.count() == 0:
                if step.continueOnEmpty is False:
                    raise ValueError(f"Input element not found: {step.object}")
                print(f"   ⚠️  Input element not found: {step.object}")
                return
            
            # Clear if configured
            if step.clearBeforeInput is not False:  # Default True
                await loc.first.clear()
            
            # Input with delay if configured
            value = replace_data_placeholders(step.value or "", collector) or step.value or ""
            if step.inputDelay:
                # Type character by character
                for char in value:
                    await loc.first.type(char, delay=step.inputDelay)
            else:
                await loc.first.fill(value)
            
            if step.wait and step.wait > 0:
                await page.wait_for_timeout(step.wait)

        elif step.action == "click":
            # Wait for selector if configured
            await wait_for_selector_if_configured(page, step, scope_locator)

            # Find locator with fallbacks
            loc, used_type, used_selector = await find_locator_with_fallbacks(
                page,
                scope_locator,
                step.object_type,
                step.object or "",
                step.fallbackSelectors
            )
            
            if not loc or await loc.count() == 0:
                if step.continueOnEmpty is False:
                    raise ValueError(f"Element not found: {step.object}")
                print(f"   ⚠️  Element not found: {step.object} - skipping click")
                return
            
            # Check element state
            if step.requireVisible is not False:  # Default True for click
                if not await loc.first.is_visible():
                    if step.forceClick:
                        print(f"   ⚠️  Element not visible, using force click")
                    else:
                        raise ValueError(f"Element not visible: {used_selector}")
            
            if step.requireEnabled:
                if not await loc.first.is_enabled():
                    raise ValueError(f"Element not enabled: {used_selector}")
            
            # Perform click with modifiers
            try:
                modifiers = step.clickModifiers or []
                
                if step.doubleClick:
                    await loc.first.dblclick(modifiers=modifiers)
                elif step.rightClick:
                    await loc.first.click(button="right", modifiers=modifiers, force=step.forceClick or False)
                else:
                    await loc.first.click(modifiers=modifiers, force=step.forceClick or False)
            except Exception as e:
                if step.skipOnError:
                    print(f"   ⚠️  Click failed (skipping): {e}")
                else:
                    raise

        elif step.action == "data":
            try:
                await _handle_data_extraction(page, step, collector, scope_locator)
            except Exception as e:
                print(f"   ⚠️  Data extraction failed for {step.object}: {e}")
                key = step.key or step.id or "data"
                if step.required:
                    raise
                collector[key] = step.defaultValue

        elif step.action == "eventBaseDownload":
            await _handle_event_download(page, step, collector)

        elif step.action == "foreach":
            await _handle_foreach(page, step, collector, execute_step, on_result)

        elif step.action == "open":
            await _handle_open(page, step, collector, execute_step, on_result)

        elif step.action == "scroll":
            await _handle_scroll(page, step)

        elif step.action == "savePDF":
            await _handle_save_pdf(page, step, collector)

        elif step.action in ("downloadPDF", "downloadFile"):
            await _handle_download_pdf(page, step, collector)

        elif step.action == "reload":
            await _handle_reload(page, step, collector)

        elif step.action == "getUrl":
            await _handle_get_url(page, step, collector)

        elif step.action == "getTitle":
            await _handle_get_title(page, step, collector)

        elif step.action == "getMeta":
            await _handle_get_meta(page, step, collector)

        elif step.action == "getCookies":
            await _handle_get_cookies(page, step, collector)

        elif step.action == "setCookies":
            await _handle_set_cookies(page, step, collector)

        elif step.action == "getLocalStorage":
            await _handle_get_local_storage(page, step, collector)

        elif step.action == "setLocalStorage":
            await _handle_set_local_storage(page, step, collector)

        elif step.action == "getSessionStorage":
            await _handle_get_session_storage(page, step, collector)

        elif step.action == "setSessionStorage":
            await _handle_set_session_storage(page, step, collector)

        elif step.action == "getViewportSize":
            await _handle_get_viewport_size(page, step, collector)

        elif step.action == "setViewportSize":
            await _handle_set_viewport_size(page, step, collector)

        elif step.action == "screenshot":
            await _handle_screenshot(page, step, collector)

        elif step.action == "waitForSelector":
            await _handle_wait_for_selector(page, step, collector)

        elif step.action == "evaluate":
            await _handle_evaluate(page, step, collector)

        # trailing wait
        if step.wait and step.wait > 0:
            await page.wait_for_timeout(step.wait)

    except Exception as e:
        # Top-level step guard
        if step.skipOnError:
            print(f"   ⚠️  Step '{step.id}' error (skipping): {e}")
            return
        if step.terminateonerror:
            raise
        print(f"   ⚠️  Step '{step.id}' error (ignored): {e}")


async def _handle_scroll(page: Page, step: BaseStep) -> None:
    """Handle scroll action"""
    if step.value is not None:
        try:
            offset = int(step.value)
        except ValueError:
            offset = await page.evaluate("() => window.innerHeight")
    else:
        offset = await page.evaluate("() => window.innerHeight")
    await page.evaluate("y => window.scrollBy(0, y)", offset)


async def execute_step_list(
    page: Page, steps: List[BaseStep], collected: Dict[str, Any], on_result=None
) -> None:
    """Execute a list of steps sequentially"""
    print(f"📝 Executing {len(steps)} step(s)")
    for step in steps:
        try:
            await execute_step(page, step, collected, on_result)
        except Exception as e:
            if step.terminateonerror:
                raise
            # else ignore to be future-proof


async def execute_tab(
    page: Page,
    template: TabTemplate,
    on_result: Optional[Callable[[Dict[str, Any], int], Any]] = None,
) -> List[Dict[str, Any]]:
    """Execute a complete tab template with pagination"""
    results: List[Dict[str, Any]] = []
    print(f"=== TAB {template.tab} ===")

    # 1) initSteps
    if template.initSteps:
        print("--- Running initSteps ---")
        await execute_step_list(page, template.initSteps, {}, on_result)

    pagination = template.pagination

    async def run_pagination(
        page: Page, pagination: PaginationConfig, log_prefix: str = ""
    ) -> bool:
        """Execute pagination action (next button or scroll)"""
        if pagination.strategy == "next" and pagination.nextButton:
            print(f"{log_prefix}👉 Clicking next button")
            try:
                await click_action(
                    page, pagination.nextButton.object_type, pagination.nextButton.object
                )
                if pagination.nextButton.wait:
                    await page.wait_for_timeout(pagination.nextButton.wait)
                else:
                    await page.wait_for_load_state("networkidle")
                return True
            except Exception:
                return False
        elif pagination.strategy == "scroll":
            print(f"{log_prefix}🖱️  Scrolling for pagination")
            offset = (
                pagination.scroll.offset
                if pagination.scroll and pagination.scroll.offset is not None
                else await page.evaluate("() => window.innerHeight")
            )
            await page.evaluate("y => window.scrollBy(0, y)", offset)
            delay = (
                pagination.scroll.delay
                if pagination.scroll and pagination.scroll.delay is not None
                else 1000
            )
            await page.wait_for_timeout(delay)
            return True
        return False

    # paginateAllFirst mode
    if pagination and pagination.paginateAllFirst:
        page_index = 0
        while True:
            if pagination.maxPages is not None and page_index >= pagination.maxPages:
                break
            paginated = await run_pagination(page, pagination, "[paginateAllFirst] ")
            if not paginated:
                break
            page_index += 1

        collected: Dict[str, Any] = {}
        steps_for_page = (
            template.perPageSteps
            if (template.perPageSteps and len(template.perPageSteps) > 0)
            else (template.steps or [])
        )
        await execute_step_list(page, steps_for_page, collected, on_result)
        # Always add result if steps were executed (even if collector is empty)
        if steps_for_page and len(steps_for_page) > 0:
            item_keys = [k for k in collected.keys() if k.startswith("item_")]
            result_index = 0
            if item_keys:
                for k in item_keys:
                    item = collected[k]
                    if item and len(item) > 0:
                        # Flatten nested foreach results into an array (same logic as callback)
                        flattened_result = flatten_nested_foreach_results(item)
                        results.append(flattened_result)
                        # Callback already called in _handle_foreach for each item, no need to call again
                        result_index += 1
            else:
                results.append(collected)
                if on_result:
                    await maybe_await(on_result(collected, 0))
        print(f"=== Finished tab {template.tab} - collected {len(results)} record(s) ===")
        return results

    # default pagination-per-page loop
    page_index = 0
    result_index = 0
    while True:
        print(f"--- Page iteration {page_index} ---")
        collected: Dict[str, Any] = {}

        if pagination and pagination.paginationFirst and page_index > 0:
            paginated = await run_pagination(page, pagination, "[paginationFirst] ")
            if not paginated:
                break

        steps_for_page = (
            template.perPageSteps
            if (template.perPageSteps and len(template.perPageSteps) > 0)
            else (template.steps or [])
        )
        await execute_step_list(page, steps_for_page, collected, on_result)

        # Always add result if steps were executed (even if collector is empty)
        # This ensures actions-only steps (like clicks) still produce results
        if steps_for_page and len(steps_for_page) > 0:
            item_keys = [k for k in collected.keys() if k.startswith("item_")]
            if item_keys:
                for k in item_keys:
                    item = collected[k]
                    if item and len(item) > 0:
                        # Flatten nested foreach results into an array (same logic as callback)
                        flattened_result = flatten_nested_foreach_results(item)
                        results.append(flattened_result)
                        # Callback already called in _handle_foreach for each item, no need to call again
                        result_index += 1
            else:
                results.append(collected)
                if on_result:
                    await maybe_await(on_result(collected, result_index))
                result_index += 1

        if not pagination:
            print("No pagination configured, finishing tab")
            break

        page_index += 1
        if pagination.maxPages is not None and page_index >= pagination.maxPages:
            break

        if not pagination.paginationFirst:
            paginated = await run_pagination(page, pagination, "")
            if not paginated:
                break

    print(f"=== Finished tab {template.tab} - collected {len(results)} record(s) ===")
    return results
