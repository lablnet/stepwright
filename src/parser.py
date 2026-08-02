# parser.py
# Public API for StepWright scraper
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import asyncio

import json
import time
from pathlib import Path

from .step_types import (
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    RunOptions,
    BaseStep,
    ExecutionMetrics,
    ProxyConfig,
    parse_template_from_dict,
)
from .executor import execute_tab
from .scraper import get_browser, get_device_preset, _shutdown_playwright
from .validator import validate_template_format, validate_template_data
from .handlers import apply_stealth_scripts


def load_template(
    source: Union[str, Path, dict, TabTemplate, ParallelTemplate, ParameterizedTemplate, List[Any]]
) -> Union[TabTemplate, ParallelTemplate, ParameterizedTemplate, List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]]]:
    """
    Load and parse a template from a JSON file path, JSON string, dictionary, or template instance.
    Supports single template objects or a list of templates.

    @since 2.0.0
    """
    if isinstance(source, (TabTemplate, ParallelTemplate, ParameterizedTemplate)):
        return source

    if isinstance(source, list):
        return [load_template(item) for item in source]

    if isinstance(source, dict):
        return parse_template_from_dict(source)

    if isinstance(source, (str, Path)):
        p = Path(source) if isinstance(source, (str, Path)) else None
        if p and p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
        else:
            content = str(source)
        data = json.loads(content)
        return load_template(data)

    raise ValueError(f"Unsupported template source type: {type(source)}")


def save_template(
    template: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate, BaseStep, List[Any]],
    file_path: Union[str, Path],
    indent: int = 2,
) -> str:
    """
    Save a template or step object to a JSON file.
    
    @since 2.0.0
    """
    if isinstance(template, list):
        serialized = [item.to_dict() if hasattr(item, "to_dict") else item for item in template]
    elif hasattr(template, "to_dict"):
        serialized = template.to_dict()
    else:
        serialized = template

    json_str = json.dumps(serialized, indent=indent)
    Path(file_path).write_text(json_str, encoding="utf-8")
    return json_str


def template_to_json(
    template: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate, BaseStep, List[Any]],
    file_path: Optional[Union[str, Path]] = None,
    indent: int = 2,
) -> str:
    """
    Export a template object or list to a JSON string or file.
    
    @since 2.0.0
    """
    if file_path:
        return save_template(template, file_path, indent=indent)
    if isinstance(template, list):
        serialized = [item.to_dict() if hasattr(item, "to_dict") else item for item in template]
    elif hasattr(template, "to_dict"):
        serialized = template.to_dict()
    else:
        serialized = template
    return json.dumps(serialized, indent=indent)


def template_from_json(
    source: Union[str, Path]
) -> Union[TabTemplate, ParallelTemplate, ParameterizedTemplate, List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]]]:
    """
    Parse a template object or list from a JSON string or file.
    
    @since 2.0.0
    """
    return load_template(source)


def _normalize_templates(
    templates: Union[
        str,
        Path,
        dict,
        TabTemplate,
        ParallelTemplate,
        ParameterizedTemplate,
        List[Union[str, Path, dict, TabTemplate, ParameterizedTemplate, ParallelTemplate]],
    ]
) -> List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]]:
    """
    Normalize a list of templates into a list of TabTemplate, ParallelTemplate, or ParameterizedTemplate.
    
    @since 2.0.0
    """
    loaded = load_template(templates)
    if isinstance(loaded, list):
        return loaded
    return [loaded]



async def _build_context_args(options: RunOptions, tmpl: Optional[TabTemplate] = None) -> dict:
    context_args = {}

    device_name = (tmpl and tmpl.device) or options.device
    if device_name:
        preset = await get_device_preset(device_name)
        context_args.update(preset)

    user_agent = (tmpl and tmpl.user_agent) or options.user_agent
    if user_agent:
        context_args["user_agent"] = user_agent

    viewport = (tmpl and tmpl.viewport) or options.viewport
    if viewport:
        context_args["viewport"] = viewport

    locale = (tmpl and tmpl.locale) or options.locale
    if locale:
        context_args["locale"] = locale

    timezone_id = (tmpl and tmpl.timezone_id) or options.timezone_id
    if timezone_id:
        context_args["timezone_id"] = timezone_id

    geolocation = (tmpl and tmpl.geolocation) or options.geolocation
    if geolocation:
        context_args["geolocation"] = geolocation

    permissions = (tmpl and tmpl.permissions) or options.permissions
    if permissions:
        context_args["permissions"] = permissions

    is_mobile = (tmpl and tmpl.is_mobile) if (tmpl and tmpl.is_mobile is not None) else options.is_mobile
    if is_mobile is not None:
        context_args["is_mobile"] = is_mobile

    has_touch = (tmpl and tmpl.has_touch) if (tmpl and tmpl.has_touch is not None) else options.has_touch
    if has_touch is not None:
        context_args["has_touch"] = has_touch

    extra_headers = (tmpl and tmpl.extra_http_headers) or options.extra_http_headers
    if extra_headers:
        context_args["extra_http_headers"] = extra_headers

    proxy_val = (tmpl and tmpl.proxy) or options.proxy
    proxy_pool_val = (tmpl and tmpl.proxy_pool) or options.proxy_pool

    if proxy_pool_val:
        from .proxy_pool import ProxyPool
        if not isinstance(proxy_pool_val, ProxyPool):
            strategy = (tmpl and tmpl.proxy_rotation_strategy) or options.proxy_rotation_strategy
            max_failures = (tmpl and tmpl.proxy_max_failures) or options.proxy_max_failures
            cooldown = (tmpl and tmpl.proxy_cooldown_seconds) or options.proxy_cooldown_seconds
            pool_instance = ProxyPool(proxy_pool_val, strategy=strategy, max_failures=max_failures, cooldown_seconds=cooldown)
        else:
            pool_instance = proxy_pool_val

        session_id = tmpl.tab if tmpl else None
        p_cfg = pool_instance.get_proxy(session_id=session_id)
        if p_cfg:
            proxy_val = p_cfg

    if proxy_val:
        if isinstance(proxy_val, ProxyConfig):
            p_dict = {"server": proxy_val.server}
            if proxy_val.username:
                p_dict["username"] = proxy_val.username
            if proxy_val.password:
                p_dict["password"] = proxy_val.password
            if proxy_val.bypass:
                p_dict["bypass"] = proxy_val.bypass
            context_args["proxy"] = p_dict
        elif isinstance(proxy_val, dict):
            context_args["proxy"] = proxy_val

    return context_args


async def run_scraper(
    templates: Union[
        str,
        Path,
        dict,
        TabTemplate,
        ParallelTemplate,
        ParameterizedTemplate,
        List[Union[str, Path, dict, TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    ],
    options: Optional[RunOptions] = None,
) -> List[Dict[str, Any]]:
    """
    Execute a scraping template (dataclass object, dict, or JSON file path) and return the gathered data.
    """
    results, _ = await run_scraper_with_metrics(templates, options)
    return results


async def run_scraper_with_metrics(
    templates: Union[
        str,
        Path,
        dict,
        TabTemplate,
        ParallelTemplate,
        ParameterizedTemplate,
        List[Union[str, Path, dict, TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    ],
    options: Optional[RunOptions] = None,
) -> Tuple[List[Dict[str, Any]], ExecutionMetrics]:
    """
    Execute a scraping template and return both the gathered data and ExecutionMetrics.
    """
    norm_templates = _normalize_templates(templates)
    options = options or RunOptions()
    engine = options.engine or "chromium"
    browser = await get_browser((options.browser or {"headless": True}), engine=engine)

    # Base default context
    default_context_args = await _build_context_args(options)
    context = await browser.new_context(**default_context_args)
    if options.stealth:
        await apply_stealth_scripts(context)

    all_results: List[Dict[str, Any]] = []
    metrics = ExecutionMetrics()
    start_time = time.perf_counter()

    # Setup global semaphore for max_concurrency
    global_conc = options.max_concurrency
    global_sem = asyncio.Semaphore(global_conc) if (global_conc and global_conc > 0) else None

    async def process_template(
        tmpl: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate],
        current_context,
        delay_ms: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if delay_ms and delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)

        results: List[Dict[str, Any]] = []

        if isinstance(tmpl, TabTemplate):
            from .drivers import set_active_driver
            active_drv = set_active_driver(tmpl.driver or options.driver)

            # Check if tab has custom context args or engine override
            tab_context_args = await _build_context_args(options, tmpl)
            target_context = current_context
            custom_context = None

            if tab_context_args != default_context_args:
                custom_context = await browser.new_context(**tab_context_args)
                target_context = custom_context

            is_stealth = tmpl.stealth or options.stealth
            if is_stealth:
                await apply_stealth_scripts(target_context)

            page = await target_context.new_page()
            try:
                if global_sem:
                    async with global_sem:
                        tab_results = await execute_tab(
                            page,
                            tmpl,
                            options.onResult,
                            metrics=metrics if options.collect_metrics else None,
                            debug_on_failure=options.debug_on_failure,
                        )
                else:
                    tab_results = await execute_tab(
                        page,
                        tmpl,
                        options.onResult,
                        metrics=metrics if options.collect_metrics else None,
                        debug_on_failure=options.debug_on_failure,
                    )
                results.extend(tab_results)
            finally:
                await page.close()
                if custom_context:
                    await custom_context.close()

        elif isinstance(tmpl, ParallelTemplate):
            p_conc = tmpl.max_concurrency
            p_sem = asyncio.Semaphore(p_conc) if (p_conc and p_conc > 0) else None
            p_delay = tmpl.rate_limit_delay_ms or options.rate_limit_delay_ms

            async def run_parallel_item(item, idx):
                item_delay = (idx * p_delay) if p_delay else None
                if p_sem:
                    async with p_sem:
                        return await process_template(item, current_context, delay_ms=item_delay)
                else:
                    return await process_template(item, current_context, delay_ms=item_delay)

            tasks = [run_parallel_item(t, i) for i, t in enumerate(tmpl.templates)]
            parallel_results = await asyncio.gather(*tasks)
            for res_list in parallel_results:
                results.extend(res_list)

        elif isinstance(tmpl, ParameterizedTemplate):
            p_conc = tmpl.max_concurrency
            p_sem = asyncio.Semaphore(p_conc) if (p_conc and p_conc > 0) else None
            p_delay = tmpl.rate_limit_delay_ms or options.rate_limit_delay_ms

            from copy import deepcopy

            async def run_param_val(val, idx):
                cloned_tmpl = deepcopy(tmpl.template)
                placeholder = f"{{{{{tmpl.parameter_key}}}}}"
                if placeholder in cloned_tmpl.tab:
                    cloned_tmpl.tab = cloned_tmpl.tab.replace(placeholder, str(val))
                else:
                    cloned_tmpl.tab = f"{cloned_tmpl.tab}_{val}"

                def inject_param(steps: List[BaseStep], key: str, value: Any):
                    placeholder = f"{{{{{key}}}}}"
                    for s in steps:
                        if s.value and placeholder in str(s.value):
                            s.value = str(s.value).replace(placeholder, str(value))
                        if s.object and placeholder in str(s.object):
                            s.object = str(s.object).replace(placeholder, str(value))
                        if s.subSteps:
                            inject_param(s.subSteps, key, value)

                if cloned_tmpl.steps:
                    inject_param(cloned_tmpl.steps, tmpl.parameter_key, val)
                if cloned_tmpl.initSteps:
                    inject_param(cloned_tmpl.initSteps, tmpl.parameter_key, val)
                if cloned_tmpl.perPageSteps:
                    inject_param(cloned_tmpl.perPageSteps, tmpl.parameter_key, val)

                item_delay = (idx * p_delay) if p_delay else None

                if p_sem:
                    async with p_sem:
                        return await process_template(cloned_tmpl, current_context, delay_ms=item_delay)
                else:
                    return await process_template(cloned_tmpl, current_context, delay_ms=item_delay)

            parameterized_tasks = [
                run_param_val(val, idx) for idx, val in enumerate(tmpl.values)
            ]
            param_results = await asyncio.gather(*parameterized_tasks)
            for res_list in param_results:
                results.extend(res_list)

        return results

    try:
        tasks = [process_template(tmpl, context) for tmpl in norm_templates]
        final_results = await asyncio.gather(*tasks)
        for res_list in final_results:
            all_results.extend(res_list)
    finally:
        metrics.total_duration_ms = (time.perf_counter() - start_time) * 1000.0
        await context.close()
        await browser.close()
        await _shutdown_playwright()

    return all_results, metrics


async def run_scraper_with_callback(
    templates: List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    on_result: Callable[[Dict[str, Any], int], Any],
    options: Optional[RunOptions] = None,
) -> None:
    """
    Execute a scraping template with streaming results via callback for each result.
    """
    options = options or RunOptions()
    options.onResult = on_result
    await run_scraper(templates, options)

