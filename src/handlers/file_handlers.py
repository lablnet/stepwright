# file_handlers.py
# File download and PDF handling for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import pathlib
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urljoin, parse_qs

from playwright.async_api import Page
from playwright.async_api import async_playwright

from ..step_types import BaseStep
from ..helpers import locator_for, replace_data_placeholders, _ensure_dir
from ..scraper import elem


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

