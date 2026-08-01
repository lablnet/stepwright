# parser.py
# Public API for StepWright scraper
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import asyncio

import time
from .step_types import (
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    RunOptions,
    BaseStep,
    ExecutionMetrics,
)
from .executor import execute_tab
from .scraper import get_browser, _shutdown_playwright
from .validator import validate_template_format, validate_template_data


async def run_scraper(
    templates: List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    options: Optional[RunOptions] = None,
) -> List[Dict[str, Any]]:
    """
    Execute a scraping template and return the gathered data.
    """
    results, _ = await run_scraper_with_metrics(templates, options)
    return results


async def run_scraper_with_metrics(
    templates: List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    options: Optional[RunOptions] = None,
) -> Tuple[List[Dict[str, Any]], ExecutionMetrics]:
    """
    Execute a scraping template and return both the gathered data and ExecutionMetrics.
    """
    options = options or RunOptions()
    browser = await get_browser((options.browser or {"headless": True}))

    # Use a single context for efficiency unless templates specify otherwise
    context = await browser.new_context()

    all_results: List[Dict[str, Any]] = []
    metrics = ExecutionMetrics()
    start_time = time.perf_counter()

    async def process_template(
        tmpl: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate],
        current_context,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        if isinstance(tmpl, TabTemplate):
            page = await current_context.new_page()
            try:
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

        elif isinstance(tmpl, ParallelTemplate):
            tasks = [process_template(t, current_context) for t in tmpl.templates]
            parallel_results = await asyncio.gather(*tasks)
            for res_list in parallel_results:
                results.extend(res_list)

        elif isinstance(tmpl, ParameterizedTemplate):
            parameterized_tasks = []
            for val in tmpl.values:
                from copy import deepcopy

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

                parameterized_tasks.append(
                    process_template(cloned_tmpl, current_context)
                )

            param_results = await asyncio.gather(*parameterized_tasks)
            for res_list in param_results:
                results.extend(res_list)

        return results

    try:
        tasks = [process_template(tmpl, context) for tmpl in templates]
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

