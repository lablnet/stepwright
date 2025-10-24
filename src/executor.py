# executor.py
# Core execution logic for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import pathlib
import re
from typing import Any, Callable, Dict, List, Optional

from playwright.async_api import Page
from playwright.async_api import async_playwright

from .step_types import BaseStep, PaginationConfig, TabTemplate
from .helpers import (
    locator_for,
    replace_index_placeholders,
    replace_data_placeholders,
    _ensure_dir,
    maybe_await,
)
from .scraper import (
    navigate,
    input as input_action,
    click as click_action,
    elem,
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
            await _handle_foreach(page, step, collector, on_result)

        elif step.action == "open":
            await _handle_open(page, step, collector, on_result)

        elif step.action == "scroll":
            await _handle_scroll(page, step)

        elif step.action == "savePDF":
            await _handle_save_pdf(page, step, collector)

        elif step.action in ("downloadPDF", "downloadFile"):
            await _handle_download_pdf(page, step, collector)

        # trailing wait
        if step.wait and step.wait > 0:
            await page.wait_for_timeout(step.wait)

    except Exception as e:
        # Top-level step guard
        if step.terminateonerror:
            raise
        print(f"   ⚠️  Step '{step.id}' error (ignored): {e}")


async def _handle_event_download(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle eventBaseDownload action"""
    if not step.value:
        raise ValueError(f"download step {step.id} requires 'value' as target filepath")

    key = step.key or step.id or "file"
    saved_path: Optional[str] = None
    try:
        target = await elem(page, step.object_type or "tag", step.object or "")
        if await target.is_visible():
            async with page.expect_download(timeout=10000) as dl_info:
                await target.click()
            dl = await dl_info.value
            await _ensure_dir(step.value)
            await dl.save_as(step.value)
            saved_path = step.value
            print(f"   📥 Saved to {saved_path}")
        else:
            print(f"   📥 Element not visible or not found: {step.object}")
    except Exception as e:
        print(f"   📥 Download failed for {step.object}: {e}")
    finally:
        collector[key] = saved_path


async def _handle_foreach(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
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
                await execute_step(page, cloned, item_collector, on_result, scope_locator=current)
            except Exception as e:
                print(f"⚠️  sub-step '{cloned.id}' failed: {e}")
                if cloned.terminateonerror:
                    raise

        collector[f"item_{idx}"] = item_collector

        if item_collector:
            print(f"   📋 Collected data for item {idx}: {list(item_collector.keys())}")
            # Note: on_result callback is handled by execute_tab for consistency


async def _handle_open(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
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
                await execute_step(new_page, cloned, inner, on_result)
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


async def _handle_save_pdf(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle savePDF action"""
    if not step.value:
        raise ValueError(f"savePDF step {step.id} requires 'value' as target filepath")

    key = step.key or step.id or "file"
    saved_path: Optional[str] = None
    try:
        # Try to ensure the page is ready
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=step.wait or 600000)
        except Exception:
            pass

        # crude readiness loop
        pdf_ready = False
        for attempt in range(15):
            try:
                info = await page.evaluate(
                    """() => {
                        const viewer = document.querySelector('embed[type="application/pdf"]')
                             || document.querySelector('object[type="application/pdf"]')
                             || document.querySelector('iframe[src*=".pdf"]')
                             || document.querySelector('.pdf-viewer')
                             || document.querySelector('[data-pdf]');
                        const bodyText = document.body ? document.body.innerText : '';
                        const substantial = bodyText.length > 200;
                        const pdfText = /PDF|Page|Agenda|Meeting/.test(bodyText);
                        return {viewer: !!viewer, substantial, len: bodyText.length, pdfText};
                    }"""
                )
                if info.get("substantial") or info.get("pdfText"):
                    pdf_ready = True
                    break
                await page.wait_for_timeout(2000)
            except Exception:
                await page.wait_for_timeout(2000)

        if step.wait and step.wait > 0:
            await page.wait_for_timeout(step.wait)

        # Print to PDF (Chromium-only)
        pdf_bytes = await page.pdf(format="A4")

        resolved = replace_data_placeholders(step.value, collector) or step.value
        await _ensure_dir(resolved)
        with open(resolved, "wb") as f:
            f.write(pdf_bytes)
        saved_path = resolved
        print(f"   📄 PDF saved to {resolved}")
    except Exception as e:
        print(f"   📄 PDF save failed: {e}")
    finally:
        collector[key] = saved_path


async def _handle_download_pdf(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle downloadPDF/downloadFile action"""
    if not step.object:
        raise ValueError("downloadPDF requires object locator")
    if not step.value:
        raise ValueError(f"downloadPDF step {step.id} requires 'value' as target filepath")

    key = step.key or step.id or "file"
    saved_path: Optional[str] = None

    try:
        link = locator_for(page, step.object_type, step.object)
        if await link.count() == 0:
            print(f"   ⚠️  PDF link not found: {step.object}")
            collector[key] = None
            return

        href = await link.get_attribute("href")

        if not href or href.startswith("javascript"):
            ctx = page.context
            page_promise = ctx.wait_for_event("page")
            try:
                await link.click(modifiers=["Meta"])
            except Exception:
                await link.click()
            new_page = await page_promise
            try:
                await new_page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                pass
            href = new_page.url
            await new_page.close()

        if not href:
            print(f"   ⚠️  Could not resolve PDF URL from {step.object}")
            collector[key] = None
            return

        if not href.startswith("http"):
            href = str(pathlib.PurePosixPath(str(page.url))).rstrip("/") + "/" + href.lstrip("/")

        # collect cookies for target URL
        ctx = page.context
        cookies = await ctx.cookies(href)
        cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies) if cookies else ""

        # dedicated request context
        async with async_playwright() as p:
            req_ctx = await p.request.new_context(
                extra_http_headers={
                    **({"Cookie": cookie_header} if cookie_header else {}),
                    "Referer": page.url,
                    "User-Agent": "Mozilla/5.0",
                }
            )
            res = await req_ctx.get(href)
            if not res.ok:
                print(f"   📄 GET {href} -> {res.status} {res.status_text()}")
                await req_ctx.dispose()
                collector[key] = None
                return
            buffer = await res.body()
            await req_ctx.dispose()

        resolved = replace_data_placeholders(step.value, collector) or step.value
        await _ensure_dir(resolved)
        with open(resolved, "wb") as f:
            f.write(buffer)
        saved_path = resolved
        print(f"   📄 File saved to {resolved}")
    except Exception as e:
        print(f"   📄 downloadPDF failed: {e}")
    finally:
        collector[key] = saved_path


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
                        results.append(item)
                        if on_result:
                            await maybe_await(on_result(item, result_index))
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
                        results.append(item)
                        if on_result:
                            await maybe_await(on_result(item, result_index))
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
