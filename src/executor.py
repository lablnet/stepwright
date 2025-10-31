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
)
from .scraper import (
    navigate,
    input as input_action,
    click as click_action,
)
from .page_actions import (
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
from .file_handlers import (
    _handle_event_download,
    _handle_save_pdf,
    _handle_download_pdf,
)
from .loop_handlers import (
    _handle_foreach,
    _handle_open,
    clone_step_with_index,
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

    try:
        if step.action == "navigate":
            await navigate(page, step.value or "")

        elif step.action == "input":
            await input_action(
                page,
                step.object_type or "tag",
                step.object or "",
                step.value or "",
                step.wait or 0,
            )

        elif step.action == "click":
            loc = locator_for(page, step.object_type, step.object or "")
            if await loc.count() == 0:
                print(f"   ⚠️  Element not found: {step.object} - skipping click")
            else:
                try:
                    await click_action(page, step.object_type or "tag", step.object or "")
                except Exception as e:
                    print(f"   ⚠️  Click failed for {step.object}: {e}")

        elif step.action == "data":
            try:
                check_selector = step.object or ""
                if step.data_type == "attribute" and re.search(r"/@\w+$", check_selector):
                    check_selector = re.sub(r"/@\w+$", "", check_selector)

                # Use scope_locator if provided (for foreach context)
                if scope_locator:
                    loc = locator_for(scope_locator, step.object_type, check_selector)
                else:
                    loc = locator_for(page, step.object_type, check_selector)

                if await loc.count() == 0:
                    print(f"   ⚠️  Element not found: {check_selector} - skipping data")
                    key = step.key or step.id or "data"
                    collector[key] = None
                else:
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

                    if step.wait and step.wait > 0:
                        await page.wait_for_timeout(step.wait)

                    key = step.key or step.id or "data"
                    collector[key] = val
                    print(f"Step Data: {key}: {val}")
            except Exception as e:
                print(f"   ⚠️  Data extraction failed for {step.object}: {e}")
                key = step.key or step.id or "data"
                collector[key] = None

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
        if collected:
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

        if collected:
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
