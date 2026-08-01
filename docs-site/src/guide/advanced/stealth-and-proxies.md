# Stealth & Anti-Bot Evasion Features

StepWright provides automated fingerprint evasion (`stealth=True`), proxy routing with authentication credentials, and CAPTCHA / Cloudflare challenge detection hooks.

---

## 🥷 1. Stealth Mode (`stealth=True`)

Modern web scrapers are easily detected by anti-bot systems (Cloudflare, Akamai, Datadome, PerimeterX) via JavaScript fingerprinting checks.

Enabling `stealth=True` automatically injects init scripts (`add_init_script`) into browser contexts to mask automation signatures:

- Spoofs `navigator.webdriver` to `undefined`.
- Mocks `navigator.languages` (`['en-US', 'en']`) and `navigator.plugins`.
- Simulates Chrome runtime objects (`window.chrome.runtime`, `csi`, `loadTimes`).
- Overrides `Permissions.prototype.query` to report granted notifications.
- Spoofs WebGL UNMASKED_VENDOR_WEBGL (`"Google Inc. (NVIDIA)"`) and UNMASKED_RENDERER_WEBGL flags.

```python
from stepwright import TabTemplate, RunOptions, run_scraper

template = TabTemplate(
    tab="stealth_scraping_flow",
    stealth=True,  # Per-template stealth mode
    steps=[
        BaseStep(id="nav", action="navigate", value="https://nowsecure.nl"),
        BaseStep(id="title", action="getTitle", key="page_title"),
    ]
)

# Or set stealth mode globally across all tabs
options = RunOptions(stealth=True)
results = await run_scraper([template], options)
```

---

## 🌐 2. Proxy Configuration (`proxy` & `ProxyConfig`)

Route outgoing traffic through HTTP, HTTPS, or SOCKS5 proxies per template or globally:

```python
from stepwright import ProxyConfig, RunOptions, TabTemplate

# 1. Using ProxyConfig dataclass
proxy_opts = ProxyConfig(
    server="http://proxy.example.com:8080",
    username="my_user",
    password="my_password",
    bypass="*.local,127.0.0.1",
)

# 2. Or using standard dictionary
proxy_dict = {
    "server": "socks5://proxy.example.com:1080",
    "username": "my_user",
    "password": "my_password",
}

options = RunOptions(proxy=proxy_opts)
```

---

## 🚨 3. CAPTCHA & Challenge Hooks (`on_captcha`)

Detect CAPTCHAs, Turnstile, or Cloudflare challenge pages during execution and invoke a custom resolution callback hook:

```python
def handle_captcha(page, collector):
    print("🚨 CAPTCHA detected! Solving or logging issue...")
    collector["captcha_flagged"] = True

template = TabTemplate(
    tab="protected_site",
    captcha_selector="iframe[src*='challenges.cloudflare.com']",
    on_captcha=handle_captcha,
    steps=[
        BaseStep(id="nav", action="navigate", value="https://example.com"),
    ]
)
```
