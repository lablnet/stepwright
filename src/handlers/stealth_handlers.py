# handlers/stealth_handlers.py
# Stealth and Anti-Bot Evasion scripts & CAPTCHA detection for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Union

from playwright.async_api import BrowserContext, Page

STEALTH_JS_SCRIPT = """
(() => {
    // 1. Remove navigator.webdriver
    try {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    } catch (e) {}

    // 2. Mock navigator.languages and navigator.plugins
    try {
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    } catch (e) {}

    try {
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    } catch (e) {}

    // 3. Mock window.chrome runtime object
    try {
        if (!window.chrome) {
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        }
    } catch (e) {}

    // 4. Override Permissions API query
    try {
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
        );
    } catch (e) {}

    // 5. Spoof WebGL vendor and renderer
    try {
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // UNMASKED_VENDOR_WEBGL
            if (parameter === 37445) {
                return 'Google Inc. (NVIDIA)';
            }
            // UNMASKED_RENDERER_WEBGL
            if (parameter === 37446) {
                return 'ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Direct3D11 vs_5_0 ps_5_0, D3D11)';
            }
            return getParameter.apply(this, arguments);
        };
    } catch (e) {}
})();
"""


async def apply_stealth_scripts(target: Union[BrowserContext, Page]) -> None:
    """
    Inject stealth initialization scripts into a BrowserContext or Page
    to bypass automated bot detection scripts.

    @since 2.0.0
    """
    print("   🥷 Applying Stealth Anti-Bot Evasion scripts")
    if hasattr(target, "add_init_script"):
        await target.add_init_script(STEALTH_JS_SCRIPT)


async def check_and_handle_captcha(
    page: Page,
    template_or_options: Any,
    collector: Dict[str, Any],
) -> bool:
    """
    Check if a CAPTCHA or Cloudflare challenge element is present on the page.
    If detected and on_captcha callback is provided, invoke on_captcha(page, collector).

    @since 2.0.0
    """
    custom_selector = getattr(template_or_options, "captcha_selector", None)
    on_captcha_fn = getattr(template_or_options, "on_captcha", None)

    if not on_captcha_fn:
        return False

    captcha_selectors = [
        custom_selector,
        "iframe[src*='challenges.cloudflare.com']",
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        ".g-recaptcha",
        "#cf-challenge-stage",
    ]
    captcha_selectors = [s for s in captcha_selectors if s]

    for sel in captcha_selectors:
        try:
            loc = page.locator(sel)
            if await loc.count() > 0:
                print(f"   🚨 CAPTCHA / Challenge detected using selector: {sel}")
                result = on_captcha_fn(page, collector)
                if hasattr(result, "__await__"):
                    await result
                return True
        except Exception:
            pass

    return False
