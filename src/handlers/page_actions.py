# page_actions.py
# Page-related action handlers for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

from playwright.async_api import Page

from ..step_types import BaseStep
from ..helpers import locator_for, replace_data_placeholders, _ensure_dir


async def _handle_reload(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle reload action - reload the current page"""
    wait_until = step.value or "load"  # load, domcontentloaded, networkidle, commit
    valid_options = ["load", "domcontentloaded", "networkidle", "commit"]
    
    if wait_until not in valid_options:
        wait_until = "load"
    
    print(f"   🔄 Reloading page (wait_until={wait_until})")
    await page.reload(wait_until=wait_until)


async def _handle_get_url(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getUrl action - get current page URL and store in collector"""
    url = page.url
    key = step.key or step.id or "url"
    collector[key] = url
    print(f"   🔗 Current URL: {url}")
    print(f"   📋 Stored in collector[{key}]")


async def _handle_get_title(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getTitle action - get page title and store in collector"""
    title = await page.title()
    key = step.key or step.id or "title"
    collector[key] = title
    print(f"   📄 Page title: {title}")
    print(f"   📋 Stored in collector[{key}]")


async def _handle_screenshot(
    page: Page, step: BaseStep, collector: Dict[str, Any]
) -> None:
    """Handle screenshot action - take a screenshot of the page or element"""
    if not step.value:
        raise ValueError(f"screenshot step {step.id} requires 'value' as target filepath")

    target_path = replace_data_placeholders(step.value, collector) or step.value
    await _ensure_dir(target_path)
    
    saved_path: Optional[str] = None
    
    try:
        # If object is specified, screenshot that element
        if step.object:
            loc = locator_for(page, step.object_type, step.object)
            if await loc.count() == 0:
                print(f"   ⚠️  Element not found: {step.object} - taking full page screenshot")
                await page.screenshot(path=target_path, full_page=True)
            else:
                await loc.first.screenshot(path=target_path)
                print(f"   📸 Screenshot saved (element) to {target_path}")
        else:
            # Full page screenshot
            full_page = step.data_type == "full"  # Use data_type as flag for full_page
            await page.screenshot(path=target_path, full_page=full_page)
            print(f"   📸 Screenshot saved ({'full page' if full_page else 'viewport'}) to {target_path}")
        
        saved_path = target_path
        
        # Store path in collector if key is provided
        if step.key:
            collector[step.key] = saved_path
            
    except Exception as e:
        print(f"   ⚠️  Screenshot failed: {e}")
        if step.terminateonerror:
            raise


async def _handle_wait_for_selector(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle waitForSelector action - wait for an element to appear"""
    if not step.object:
        raise ValueError("waitForSelector step requires object locator")
    
    timeout = step.wait or 30000  # Default 30 seconds
    state = step.value or "visible"  # visible, hidden, attached, detached
    
    valid_states = ["visible", "hidden", "attached", "detached"]
    if state not in valid_states:
        state = "visible"
    
    print(f"   ⏳ Waiting for selector {step.object} (state={state}, timeout={timeout}ms)")
    
    try:
        loc = locator_for(page, step.object_type, step.object)
        await loc.wait_for(state=state, timeout=timeout)
        print(f"   ✅ Selector found: {step.object}")
        
        # Store success status in collector if key is provided
        if step.key:
            collector[step.key] = True
    except Exception as e:
        print(f"   ⚠️  Wait for selector failed: {step.object} - {e}")
        if step.key:
            collector[step.key] = False
        if step.terminateonerror:
            raise


async def _handle_get_meta(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getMeta action - get meta tags from the page"""
    # If object is specified, get that specific meta tag, otherwise get all meta tags
    meta_name = step.object  # e.g., "description", "og:title", "keywords"
    
    if meta_name:
        # Get specific meta tag - use safe attribute checking
        meta_content = await page.evaluate(
            """(metaName) => {
                const metas = document.querySelectorAll('meta');
                for (const meta of metas) {
                    if (meta.getAttribute('name') === metaName || meta.getAttribute('property') === metaName) {
                        return meta.getAttribute('content');
                    }
                }
                return null;
            }""",
            meta_name
        )
        key = step.key or step.id or "meta"
        collector[key] = meta_content
        print(f"   📋 Meta tag '{meta_name}': {meta_content}")
        print(f"   📋 Stored in collector[{key}]")
    else:
        # Get all meta tags as a dictionary
        all_meta = await page.evaluate(
            """() => {
                const metas = {};
                document.querySelectorAll('meta').forEach(meta => {
                    const name = meta.getAttribute('name') || meta.getAttribute('property');
                    const content = meta.getAttribute('content');
                    if (name && content) {
                        metas[name] = content;
                    }
                });
                return metas;
            }"""
        )
        key = step.key or step.id or "meta"
        collector[key] = all_meta
        print(f"   📋 Retrieved {len(all_meta)} meta tags")
        print(f"   📋 Stored in collector[{key}]")


async def _handle_get_cookies(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getCookies action - get cookies from the page"""
    url = step.value or page.url
    cookies = await page.context.cookies(url)
    
    # If object is specified, get that specific cookie, otherwise get all cookies
    cookie_name = step.object
    
    if cookie_name:
        # Get specific cookie
        cookie_value = None
        for cookie in cookies:
            if cookie["name"] == cookie_name:
                cookie_value = cookie["value"]
                break
        key = step.key or step.id or "cookie"
        collector[key] = cookie_value
        print(f"   🍪 Cookie '{cookie_name}': {cookie_value}")
        print(f"   📋 Stored in collector[{key}]")
    else:
        # Get all cookies as a dictionary
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        key = step.key or step.id or "cookies"
        collector[key] = cookies_dict
        print(f"   🍪 Retrieved {len(cookies_dict)} cookies")
        print(f"   📋 Stored in collector[{key}]")


async def _handle_set_cookies(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle setCookies action - set cookies for the page"""
    if not step.value:
        raise ValueError("setCookies step requires 'value' as cookie value")
    if not step.object:
        raise ValueError("setCookies step requires 'object' as cookie name")
    
    cookie_name = replace_data_placeholders(step.object, collector) or step.object
    cookie_value = replace_data_placeholders(step.value, collector) or step.value
    
    url = page.url
    await page.context.add_cookies([
        {
            "name": cookie_name,
            "value": cookie_value,
            "url": url,
        }
    ])
    print(f"   🍪 Set cookie '{cookie_name}' = '{cookie_value}'")


async def _handle_get_local_storage(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getLocalStorage action - get localStorage values"""
    key_name = step.object  # Specific key to get, or None for all
    
    if key_name:
        # Get specific localStorage key
        key_json = json.dumps(key_name)
        value = await page.evaluate(f"() => localStorage.getItem({key_json})")
        key = step.key or step.id or "localStorage"
        collector[key] = value
        print(f"   💾 localStorage['{key_name}']: {value}")
        print(f"   📋 Stored in collector[{key}]")
    else:
        # Get all localStorage keys
        all_storage = await page.evaluate(
            """() => {
                const storage = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    storage[key] = localStorage.getItem(key);
                }
                return storage;
            }"""
        )
        key = step.key or step.id or "localStorage"
        collector[key] = all_storage
        print(f"   💾 Retrieved {len(all_storage)} localStorage items")
        print(f"   📋 Stored in collector[{key}]")


async def _handle_set_local_storage(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle setLocalStorage action - set localStorage value"""
    if not step.object:
        raise ValueError("setLocalStorage step requires 'object' as key name")
    if step.value is None:
        raise ValueError("setLocalStorage step requires 'value' as value")
    
    key_name = replace_data_placeholders(step.object, collector) or step.object
    value = replace_data_placeholders(str(step.value), collector) or str(step.value)
    
    # Use JSON encoding for safe JavaScript evaluation
    key_json = json.dumps(key_name)
    value_json = json.dumps(value)
    await page.evaluate(f"() => localStorage.setItem({key_json}, {value_json})")
    print(f"   💾 Set localStorage['{key_name}'] = '{value}'")


async def _handle_get_session_storage(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getSessionStorage action - get sessionStorage values"""
    key_name = step.object  # Specific key to get, or None for all
    
    if key_name:
        # Get specific sessionStorage key
        key_json = json.dumps(key_name)
        value = await page.evaluate(f"() => sessionStorage.getItem({key_json})")
        key = step.key or step.id or "sessionStorage"
        collector[key] = value
        print(f"   💾 sessionStorage['{key_name}']: {value}")
        print(f"   📋 Stored in collector[{key}]")
    else:
        # Get all sessionStorage keys
        all_storage = await page.evaluate(
            """() => {
                const storage = {};
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    storage[key] = sessionStorage.getItem(key);
                }
                return storage;
            }"""
        )
        key = step.key or step.id or "sessionStorage"
        collector[key] = all_storage
        print(f"   💾 Retrieved {len(all_storage)} sessionStorage items")
        print(f"   📋 Stored in collector[{key}]")


async def _handle_set_session_storage(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle setSessionStorage action - set sessionStorage value"""
    if not step.object:
        raise ValueError("setSessionStorage step requires 'object' as key name")
    if step.value is None:
        raise ValueError("setSessionStorage step requires 'value' as value")
    
    key_name = replace_data_placeholders(step.object, collector) or step.object
    value = replace_data_placeholders(str(step.value), collector) or str(step.value)
    
    # Use JSON encoding for safe JavaScript evaluation
    key_json = json.dumps(key_name)
    value_json = json.dumps(value)
    await page.evaluate(f"() => sessionStorage.setItem({key_json}, {value_json})")
    print(f"   💾 Set sessionStorage['{key_name}'] = '{value}'")


async def _handle_get_viewport_size(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle getViewportSize action - get viewport dimensions"""
    viewport = page.viewport_size
    if viewport is None:
        viewport = await page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
    
    key = step.key or step.id or "viewportSize"
    collector[key] = {"width": viewport["width"], "height": viewport["height"]}
    print(f"   📐 Viewport size: {viewport['width']}x{viewport['height']}")
    print(f"   📋 Stored in collector[{key}]")


async def _handle_set_viewport_size(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle setViewportSize action - set viewport dimensions"""
    if not step.value:
        raise ValueError("setViewportSize step requires 'value' as dimensions (e.g., '1920x1080' or 'width,height')")
    
    # Parse dimensions: can be "1920x1080" or "1920,1080" or "1920 1080"
    dims_str = step.value.replace("x", ",").replace(" ", ",")
    try:
        width, height = map(int, dims_str.split(","))
        await page.set_viewport_size({"width": width, "height": height})
        print(f"   📐 Set viewport size to {width}x{height}")
    except ValueError:
        raise ValueError(f"Invalid viewport size format: {step.value}. Use 'widthxheight' (e.g., '1920x1080')")


async def _handle_evaluate(page: Page, step: BaseStep, collector: Dict[str, Any]) -> None:
    """Handle evaluate action - evaluate JavaScript and optionally store result"""
    if not step.value:
        raise ValueError("evaluate step requires 'value' as JavaScript code")
    
    # Replace data placeholders in the JavaScript code
    js_code = replace_data_placeholders(step.value, collector)
    
    print(f"   🔧 Evaluating JavaScript: {js_code[:100]}...")
    
    try:
        result = await page.evaluate(js_code)
        
        # Store result in collector if key is provided
        if step.key:
            collector[step.key] = result
            print(f"   📋 Result stored in collector[{step.key}]")
        else:
            print(f"   📋 Result: {result}")
            
    except Exception as e:
        print(f"   ⚠️  JavaScript evaluation failed: {e}")
        if step.key:
            collector[step.key] = None
        if step.terminateonerror:
            raise


async def _handle_press(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Any] = None,
) -> None:
    """
    Handle press action - send keyboard key press event

    @since 2.0.0
    """
    key_name = replace_data_placeholders(step.value or "", collector) or step.value
    if not key_name:
        raise ValueError("press step requires 'value' specifying key name (e.g., 'Enter', 'Control+A')")

    if step.object:
        loc = locator_for(scope_locator or page, step.object_type, step.object)
        await loc.press(key_name)
        print(f"   ⌨️  Pressed key '{key_name}' on target element: {step.object}")
    else:
        await page.keyboard.press(key_name)
        print(f"   ⌨️  Pressed page key '{key_name}'")


async def _handle_type(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Any] = None,
) -> None:
    """
    Handle type / clickAndType action - type text into an input with character delay

    @since 2.0.0
    """
    if not step.object:
        raise ValueError("type step requires 'object' selector")
    if step.value is None:
        raise ValueError("type step requires 'value' text string to type")

    text = replace_data_placeholders(str(step.value), collector)
    delay = step.inputDelay or 0

    loc = locator_for(scope_locator or page, step.object_type, step.object)
    if step.clearBeforeInput:
        await loc.fill("")

    await loc.type(text, delay=delay)
    print(f"   ⌨️  Typed '{text}' into {step.object} with delay {delay}ms")


async def _handle_dialog(
    page: Page, step: BaseStep, collector: Dict[str, Any]
) -> None:
    """
    Handle dialog action - configure browser alert/confirm/prompt auto-handler

    @since 2.0.0
    """
    mode = (step.value or "accept").lower()
    prompt_text = step.object or ""

    print(f"   💬 Registered dialog handler mode: {mode}")

    def dialog_handler(dialog):
        print(f"   💬 Browser dialog triggered: {dialog.message}")
        if mode == "dismiss":
            asyncio.create_task(dialog.dismiss())
        else:
            asyncio.create_task(dialog.accept(prompt_text))

    page.on("dialog", dialog_handler)


async def _handle_mouse_move(
    page: Page,
    step: BaseStep,
    collector: Dict[str, Any],
    scope_locator: Optional[Any] = None,
) -> None:
    """
    Handle mouseMove action - move mouse cursor to element or (x, y) coordinates

    @since 2.0.0
    """
    if step.object:
        loc = locator_for(scope_locator or page, step.object_type, step.object)
        await loc.hover()
        print(f"   🖱️  Moved mouse to element: {step.object}")
    elif step.value:
        coords_str = replace_data_placeholders(step.value, collector) or step.value
        coords = [int(c.strip()) for c in coords_str.replace("x", ",").replace(" ", ",").split(",")]
        if len(coords) < 2:
            raise ValueError(f"mouseMove step requires 'x,y' coordinates in 'value', got '{step.value}'")
        await page.mouse.move(coords[0], coords[1])
        print(f"   🖱️  Moved mouse to coordinates: ({coords[0]}, {coords[1]})")
    else:
        raise ValueError("mouseMove step requires either 'object' selector or 'value' coordinates ('x,y')")


async def _handle_wait_for_navigation(
    page: Page, step: BaseStep, collector: Dict[str, Any]
) -> None:
    """
    Handle waitForNavigation action - wait for page load state

    @since 2.0.0
    """
    state = (step.value or "networkidle").lower()
    timeout = step.wait or 30000
    print(f"   ⏳ Waiting for navigation load state: {state}")
    if state in ("networkidle", "domcontentloaded", "load"):
        await page.wait_for_load_state(state, timeout=timeout)
    else:
        await page.wait_for_url(step.value, timeout=timeout)


async def _handle_set_headers(
    page: Page, step: BaseStep, collector: Dict[str, Any]
) -> None:
    """
    Handle setHeaders action - set extra HTTP request headers dynamically

    @since 2.0.0
    """
    if not step.value and not step.key:
        raise ValueError("setHeaders step requires 'object' (header name) & 'value' (header value)")

    if step.object and step.value:
        h_name = replace_data_placeholders(step.object, collector) or step.object
        h_val = replace_data_placeholders(step.value, collector) or step.value
        headers = {h_name: h_val}
    elif step.key and step.key in collector and isinstance(collector[step.key], dict):
        headers = collector[step.key]
    else:
        raise ValueError("setHeaders step requires 'object' & 'value' or a valid dict in collector[key]")

    await page.set_extra_http_headers(headers)
    print(f"   🔑 Dynamically set extra HTTP headers: {headers}")

