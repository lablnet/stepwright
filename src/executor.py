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
    """Handle savePDF action - attempts to download actual PDF binary before falling back to page.pdf"""
    if not step.value:
        raise ValueError(f"savePDF step {step.id} requires 'value' as target filepath")

    collector_key = step.key or step.id or "file"
    saved_path: Optional[str] = None
    target_path_base: str = step.value

    try:
        # Ensure the page finished initial navigation
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=step.wait or 600000)
        except Exception:
            pass

        # Try to resolve the direct PDF URL
        pdf_url: Optional[str] = None

        # 1) If the current URL points to a PDF (anywhere in the URL), use it or extract from query
        current_url = page.url
        print(f"   📄 Current URL: {current_url}")
        try:
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            candidates = []
            for param in ["file", "src", "document", "url"]:
                if param in query_params and query_params[param]:
                    val = query_params[param][0]
                    if re.search(r"\.pdf", val, re.IGNORECASE):
                        candidates.append(val)
            
            if candidates:
                param_pdf = candidates[0]
                pdf_url = urljoin(current_url, param_pdf)
        except Exception:
            pass

        if not pdf_url and re.search(r"\.pdf", current_url, re.IGNORECASE):
            pdf_url = current_url

        # 2) Otherwise, try to discover PDF source from common viewer elements
        if not pdf_url:
            try:
                pdf_url = await page.evaluate(
                    """() => {
                        const getAbs = (src) => {
                            if (!src) return null;
                            try {
                                return new URL(src, window.location.href).toString();
                            } catch {
                                return src;
                            }
                        };

                        const embed = document.querySelector('embed[type="application/pdf"]');
                        if (embed && embed.getAttribute('src')) return getAbs(embed.getAttribute('src'));

                        const objectEl = document.querySelector('object[type="application/pdf"]');
                        if (objectEl && objectEl.getAttribute('data')) return getAbs(objectEl.getAttribute('data'));

                        const iframes = Array.from(document.querySelectorAll('iframe'));
                        const iframe = iframes.find(f => {
                            const s = f.getAttribute('src') || '';
                            return /\.pdf/i.test(s) || s.includes('pdf');
                        });
                        if (iframe && iframe.getAttribute('src')) return getAbs(iframe.getAttribute('src'));

                        return null;
                    }"""
                )
            except Exception:
                pass

        # 3) Additional wait if requested (helps some viewers populate 'src')
        if not pdf_url and step.wait and step.wait > 0:
            await page.wait_for_timeout(step.wait)
            try:
                # Try again once after waiting
                pdf_url = await page.evaluate(
                    """() => {
                        const iframes = Array.from(document.querySelectorAll('iframe'));
                        const iframe = iframes.find(f => f.getAttribute('src'));
                        return iframe ? iframe.src : null;
                    }"""
                )
            except Exception:
                pass

        # If we couldn't find a PDF URL, try fallback methods
        if not pdf_url:
            print("   📄 Direct PDF URL not found. Trying viewer download fallback...")
            # Will try viewer download methods below
        else:
            # Build candidate URLs and try them until one succeeds
            candidates: List[str] = []
            is_absolute = bool(re.match(r"^https?:", pdf_url, re.IGNORECASE))
            
            if is_absolute:
                candidates.append(pdf_url)
            else:
                # 1) Same-origin resolution
                candidates.append(urljoin(current_url, pdf_url))

            # No site-specific heuristics; keep candidates generic only

            # Log URLs for debugging
            print(f"   📄 Current URL: {current_url}")
            print(f"   📄 Candidate PDF URLs: {candidates}")

            # Download the first successful candidate
            downloaded_buffer: Optional[bytes] = None
            for candidate_url in candidates:
                try:
                    ctx = page.context
                    cookies = await ctx.cookies(candidate_url)
                    cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies) if cookies else ""
                    
                    async with async_playwright() as p:
                        api = await p.request.new_context(
                            extra_http_headers={
                                **({"Cookie": cookie_header} if cookie_header else {}),
                                "Referer": current_url,
                                "User-Agent": "Mozilla/5.0",
                            }
                        )
                        res = await api.get(candidate_url)
                        if res.ok:
                            downloaded_buffer = await res.body()
                            await api.dispose()
                            pdf_url = candidate_url  # final URL used
                            break
                        else:
                            print(f"   📄 GET {candidate_url} -> {res.status} {res.status_text()}")
                            await api.dispose()
                except Exception as e:
                    print(f"   📄 GET {candidate_url} failed: {e}")

            if downloaded_buffer:
                resolved_path = replace_data_placeholders(target_path_base, collector) or target_path_base
                await _ensure_dir(resolved_path)
                with open(resolved_path, "wb") as f:
                    f.write(downloaded_buffer)
                saved_path = resolved_path
                print(f"   📄 PDF saved to {resolved_path} (from {pdf_url})")
            else:
                pdf_url = None  # Reset to trigger fallback

        # Fallback: viewer download methods
        if not saved_path:
            if not pdf_url:
                print("   📄 All candidate PDF URLs failed. Trying viewer download fallback...")
            
            # Main page attempt (deep shadow click only)
            saved = False
            
            # Try clicking download buttons in main page
            try:
                async with page.expect_download(timeout=5000) as dl_info:
                    clicked_main = await page.evaluate(
                        """async () => {
                            const targetIds = ['download', 'save'];
                            const visited = new Set();
                            
                            function tryClick(node) {
                                if (visited.has(node)) return false;
                                visited.add(node);
                                const el = node;
                                if (el && el.id && targetIds.includes(el.id)) {
                                    el.click();
                                    return true;
                                }
                                const elem = node;
                                if (!elem) return false;
                                const sr = elem.shadowRoot;
                                if (sr) {
                                    for (const child of Array.from(sr.children)) {
                                        if (tryClick(child)) return true;
                                    }
                                }
                                for (const child of Array.from(elem.children)) {
                                    if (tryClick(child)) return true;
                                }
                                return false;
                            }
                            return tryClick(document.documentElement);
                        }"""
                    )
                
                if clicked_main:
                    dl = await dl_info.value
                    resolved_path = replace_data_placeholders(target_path_base, collector) or target_path_base
                    await _ensure_dir(resolved_path)
                    await dl.save_as(resolved_path)
                    saved_path = resolved_path
                    print(f"   📄 PDF saved via viewer download to {resolved_path}")
                    saved = True
            except Exception:
                pass

            # Frames attempt
            if not saved:
                all_frames = page.frames
                for frame in all_frames:
                    if frame == page.main_frame:
                        continue
                    try:
                        async with page.expect_download(timeout=5000) as dl_info:
                            clicked = await frame.evaluate(
                                """async () => {
                                    const targetIds = ['download', 'save'];
                                    const visited = new Set();
                                    
                                    function tryClick(node) {
                                        if (visited.has(node)) return false;
                                        visited.add(node);
                                        const el = node;
                                        if (el && el.id && targetIds.includes(el.id)) {
                                            el.click();
                                            return true;
                                        }
                                        const elem = node;
                                        if (!elem) return false;
                                        const sr = elem.shadowRoot;
                                        if (sr) {
                                            for (const child of Array.from(sr.children)) {
                                                if (tryClick(child)) return true;
                                            }
                                        }
                                        for (const child of Array.from(elem.children)) {
                                            if (tryClick(child)) return true;
                                        }
                                        return false;
                                    }
                                    return tryClick(document.documentElement);
                                }"""
                            )
                        
                        if clicked:
                            dl = await dl_info.value
                            resolved_path = replace_data_placeholders(target_path_base, collector) or target_path_base
                            await _ensure_dir(resolved_path)
                            await dl.save_as(resolved_path)
                            saved_path = resolved_path
                            print(f"   📄 PDF saved via viewer download to {resolved_path}")
                            saved = True
                            break
                    except Exception:
                        continue

            # Non-click fallback: try to scrape a direct download link href and fetch it
            if not saved:
                try:
                    hrefs = await page.evaluate(
                        """() => {
                            const links = [];
                            const anchors = Array.from(document.querySelectorAll('a'));
                            for (const a of anchors) {
                                const text = (a.textContent || '').toLowerCase();
                                const aria = (a.getAttribute('aria-label') || '').toLowerCase();
                                if (a.hasAttribute('download') || text.includes('download') || aria.includes('download')) {
                                    if (a.href) links.push(a.href);
                                }
                            }
                            return links.slice(0, 3);
                        }"""
                    )
                    if hrefs and len(hrefs) > 0:
                        for href in hrefs:
                            try:
                                ctx = page.context
                                cookies = await ctx.cookies(href)
                                cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies) if cookies else ""
                                
                                async with async_playwright() as p:
                                    api = await p.request.new_context(
                                        extra_http_headers={
                                            **({"Cookie": cookie_header} if cookie_header else {}),
                                            "Referer": current_url,
                                            "User-Agent": "Mozilla/5.0",
                                            "Accept": "application/pdf,*/*",
                                        }
                                    )
                                    res = await api.get(href)
                                    if res.ok:
                                        body = await res.body()
                                        resolved_path = replace_data_placeholders(target_path_base, collector) or target_path_base
                                        await _ensure_dir(resolved_path)
                                        with open(resolved_path, "wb") as f:
                                            f.write(body)
                                        saved_path = resolved_path
                                        print(f"   📄 PDF saved via scraped href to {resolved_path}")
                                        await api.dispose()
                                        saved = True
                                        break
                                    await api.dispose()
                            except Exception:
                                pass
                except Exception:
                    pass

            if not saved:
                print("   📄 Viewer download fallback failed.")

    except Exception as e:
        print(f"   📄 savePDF failed: {e}")
    finally:
        collector[collector_key] = saved_path


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
