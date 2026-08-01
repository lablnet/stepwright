# validator.py
# Validation logic for StepWright templates and data flows
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

from typing import Any, Dict, List, Set, Union, Optional

from .step_types import (
    BaseStep,
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    ValidationError,
    ValidationResult,
)

VALID_ACTIONS = {
    "navigate",
    "input",
    "click",
    "data",
    "scroll",
    "eventBaseDownload",
    "foreach",
    "open",
    "savePDF",
    "printToPDF",
    "downloadPDF",
    "downloadFile",
    "reload",
    "getUrl",
    "getTitle",
    "getMeta",
    "getCookies",
    "setCookies",
    "getLocalStorage",
    "setLocalStorage",
    "getSessionStorage",
    "setSessionStorage",
    "getViewportSize",
    "setViewportSize",
    "screenshot",
    "waitForSelector",
    "evaluate",
    "hover",
    "dragAndDrop",
    "select",
    "uploadFile",
    "virtualScroll",
    "readData",
    "writeData",
    "custom",
    "intercept",
}

VALID_SELECTOR_TYPES = {"id", "class", "tag", "xpath"}


def validate_template_format(
    templates: Union[
        TabTemplate,
        ParallelTemplate,
        ParameterizedTemplate,
        List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    ]
) -> ValidationResult:
    """
    Validate the format and syntax of StepWright template(s) statically.

    :param templates: Single template object or list of templates
    :return: ValidationResult with errors and warnings
    """
    errors: List[ValidationError] = []
    warnings: List[str] = []

    if isinstance(templates, list):
        for idx, tmpl in enumerate(templates):
            _validate_template_format_single(tmpl, f"templates[{idx}]", errors, warnings)
    else:
        _validate_template_format_single(templates, "template", errors, warnings)

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


VALID_ENGINES = {"chromium", "firefox", "webkit"}


def _validate_template_format_single(
    tmpl: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate],
    path: str,
    errors: List[ValidationError],
    warnings: List[str],
) -> None:
    if isinstance(tmpl, TabTemplate):
        if not tmpl.tab:
            errors.append(
                ValidationError(
                    path=f"{path}.tab",
                    message="TabTemplate requires a non-empty 'tab' identifier",
                    code="MISSING_TAB_NAME",
                )
            )

        if tmpl.engine and tmpl.engine not in VALID_ENGINES:
            errors.append(
                ValidationError(
                    path=f"{path}.engine",
                    message=f"Invalid browser engine '{tmpl.engine}'. Must be one of {VALID_ENGINES}",
                    code="INVALID_ENGINE",
                )
            )

        step_groups = [
            ("initSteps", tmpl.initSteps),
            ("perPageSteps", tmpl.perPageSteps),
            ("steps", tmpl.steps),
        ]

        has_any_steps = False
        for group_name, steps in step_groups:
            if steps:
                has_any_steps = True
                for idx, step in enumerate(steps):
                    _validate_step_format(
                        step, f"{path}.{group_name}[{idx}]", errors, warnings
                    )

        if not has_any_steps:
            warnings.append(
                f"{path}: TabTemplate '{tmpl.tab}' has no steps defined (initSteps, perPageSteps, or steps)."
            )

        if tmpl.pagination:
            pag = tmpl.pagination
            if pag.strategy not in ("next", "scroll"):
                errors.append(
                    ValidationError(
                        path=f"{path}.pagination.strategy",
                        message=f"Invalid pagination strategy '{pag.strategy}'. Must be 'next' or 'scroll'",
                        code="INVALID_PAGINATION_STRATEGY",
                    )
                )
            if pag.strategy == "next" and not pag.nextButton:
                errors.append(
                    ValidationError(
                        path=f"{path}.pagination.nextButton",
                        message="Pagination strategy 'next' requires nextButton configuration",
                        code="MISSING_NEXT_BUTTON",
                    )
                )
            if pag.nextButton and pag.nextButton.object_type not in VALID_SELECTOR_TYPES:
                errors.append(
                    ValidationError(
                        path=f"{path}.pagination.nextButton.object_type",
                        message=f"Invalid selector type '{pag.nextButton.object_type}' in nextButton",
                        code="INVALID_SELECTOR_TYPE",
                    )
                )

        if tmpl.proxy:
            proxy_server = tmpl.proxy.server if hasattr(tmpl.proxy, "server") else tmpl.proxy.get("server") if isinstance(tmpl.proxy, dict) else None
            if not proxy_server or not isinstance(proxy_server, str) or not proxy_server.strip():
                errors.append(
                    ValidationError(
                        path=f"{path}.proxy.server",
                        message="Proxy configuration requires a non-empty 'server' URL",
                        code="INVALID_PROXY_SERVER",
                    )
                )

    elif isinstance(tmpl, ParallelTemplate):
        if tmpl.max_concurrency is not None and tmpl.max_concurrency <= 0:
            errors.append(
                ValidationError(
                    path=f"{path}.max_concurrency",
                    message="max_concurrency must be a positive integer greater than 0",
                    code="INVALID_CONCURRENCY",
                )
            )
        if not tmpl.templates:
            errors.append(
                ValidationError(
                    path=f"{path}.templates",
                    message="ParallelTemplate requires a non-empty list of templates",
                    code="EMPTY_PARALLEL_TEMPLATES",
                )
            )
        else:
            for idx, child in enumerate(tmpl.templates):
                _validate_template_format_single(
                    child, f"{path}.templates[{idx}]", errors, warnings
                )

    elif isinstance(tmpl, ParameterizedTemplate):
        if tmpl.max_concurrency is not None and tmpl.max_concurrency <= 0:
            errors.append(
                ValidationError(
                    path=f"{path}.max_concurrency",
                    message="max_concurrency must be a positive integer greater than 0",
                    code="INVALID_CONCURRENCY",
                )
            )
        if not tmpl.template:
            errors.append(
                ValidationError(
                    path=f"{path}.template",
                    message="ParameterizedTemplate requires a base template",
                    code="MISSING_BASE_TEMPLATE",
                )
            )
        else:
            _validate_template_format_single(
                tmpl.template, f"{path}.template", errors, warnings
            )

        if not tmpl.parameter_key:
            errors.append(
                ValidationError(
                    path=f"{path}.parameter_key",
                    message="ParameterizedTemplate requires a 'parameter_key'",
                    code="MISSING_PARAMETER_KEY",
                )
            )
        if not tmpl.values or len(tmpl.values) == 0:
            warnings.append(
                f"{path}: ParameterizedTemplate has empty 'values' list."
            )
    else:
        errors.append(
            ValidationError(
                path=path,
                message=f"Invalid template type: {type(tmpl)}",
                code="INVALID_TEMPLATE_TYPE",
            )
        )


def _validate_step_format(
    step: BaseStep,
    path: str,
    errors: List[ValidationError],
    warnings: List[str],
) -> None:
    if not isinstance(step, BaseStep):
        errors.append(
            ValidationError(
                path=path,
                message=f"Expected BaseStep instance, got {type(step)}",
                code="INVALID_STEP_TYPE",
            )
        )
        return

    if not step.id:
        errors.append(
            ValidationError(
                path=f"{path}.id",
                message="Step requires an 'id'",
                code="MISSING_STEP_ID",
            )
        )

    action = step.action or "navigate"
    if action not in VALID_ACTIONS:
        errors.append(
            ValidationError(
                path=f"{path}.action",
                message=f"Unknown or unsupported step action '{action}'",
                code="INVALID_ACTION",
            )
        )

    if step.object_type and step.object_type not in VALID_SELECTOR_TYPES:
        errors.append(
            ValidationError(
                path=f"{path}.object_type",
                message=f"Invalid object_type '{step.object_type}'. Must be one of {VALID_SELECTOR_TYPES}",
                code="INVALID_SELECTOR_TYPE",
            )
        )

    if step.frameSelectorType and step.frameSelectorType not in VALID_SELECTOR_TYPES:
        errors.append(
            ValidationError(
                path=f"{path}.frameSelectorType",
                message=f"Invalid frameSelectorType '{step.frameSelectorType}'. Must be one of {VALID_SELECTOR_TYPES}",
                code="INVALID_SELECTOR_TYPE",
            )
        )

    # Action specific requirements
    if action == "navigate" and not step.value:
        errors.append(
            ValidationError(
                path=f"{path}.value",
                message="Action 'navigate' requires a target URL in 'value'",
                code="MISSING_REQUIRED_VALUE",
            )
        )
    elif action in ("input", "click", "hover", "select", "uploadFile") and not step.object:
        errors.append(
            ValidationError(
                path=f"{path}.object",
                message=f"Action '{action}' requires a selector in 'object'",
                code="MISSING_REQUIRED_OBJECT",
            )
        )
    elif action == "foreach":
        if not step.object and not step.value:
            errors.append(
                ValidationError(
                    path=path,
                    message="Action 'foreach' requires either 'object' (selector) or 'value' (data source)",
                    code="MISSING_FOREACH_SOURCE",
                )
            )
        if not step.subSteps or len(step.subSteps) == 0:
            errors.append(
                ValidationError(
                    path=f"{path}.subSteps",
                    message="Action 'foreach' requires a non-empty list of 'subSteps'",
                    code="MISSING_SUBSTEPS",
                )
            )
    elif action == "open":
        if not step.object:
            errors.append(
                ValidationError(
                    path=f"{path}.object",
                    message="Action 'open' requires a link/element selector in 'object'",
                    code="MISSING_REQUIRED_OBJECT",
                )
            )
        if not step.subSteps or len(step.subSteps) == 0:
            errors.append(
                ValidationError(
                    path=f"{path}.subSteps",
                    message="Action 'open' requires a non-empty list of 'subSteps'",
                    code="MISSING_SUBSTEPS",
                )
            )
    elif action in ("readData", "writeData") and not step.value:
        errors.append(
            ValidationError(
                path=f"{path}.value",
                message=f"Action '{action}' requires a file path in 'value'",
                code="MISSING_REQUIRED_VALUE",
            )
        )
    elif action == "screenshot" and not step.value:
        errors.append(
            ValidationError(
                path=f"{path}.value",
                message="Action 'screenshot' requires a target filepath in 'value'",
                code="MISSING_REQUIRED_VALUE",
            )
        )
    elif action == "savePDF" and not step.value:
        errors.append(
            ValidationError(
                path=f"{path}.value",
                message="Action 'savePDF' requires a target filepath in 'value'",
                code="MISSING_REQUIRED_VALUE",
            )
        )
    elif action in ("downloadPDF", "downloadFile") and (not step.object or not step.value):
        errors.append(
            ValidationError(
                path=path,
                message=f"Action '{action}' requires both 'object' (link) and 'value' (filepath)",
                code="MISSING_DOWNLOAD_PARAMS",
            )
        )
    elif action == "dragAndDrop" and (not step.object or not step.targetObject):
        errors.append(
            ValidationError(
                path=path,
                message="Action 'dragAndDrop' requires both 'object' (source) and 'targetObject' (target)",
                code="MISSING_DRAG_TARGET",
            )
        )
    elif action == "custom" and not step.callback:
        errors.append(
            ValidationError(
                path=f"{path}.callback",
                message="Action 'custom' requires a 'callback' function",
                code="MISSING_CALLBACK",
            )
        )
    elif action == "intercept" and not (step.object or step.value):
        errors.append(
            ValidationError(
                path=path,
                message="Action 'intercept' requires a target URL pattern in 'object' or 'value'",
                code="MISSING_INTERCEPT_PATTERN",
            )
        )

    # Validate recursive subSteps
    if step.subSteps:
        for idx, sub in enumerate(step.subSteps):
            _validate_step_format(sub, f"{path}.subSteps[{idx}]", errors, warnings)


def validate_template_data(
    templates: Union[
        TabTemplate,
        ParallelTemplate,
        ParameterizedTemplate,
        List[Union[TabTemplate, ParallelTemplate, ParameterizedTemplate]],
    ],
    expected_keys: List[str],
) -> ValidationResult:
    """
    Validate that the template flow extracts all expected output data keys.

    :param templates: Single template or list of templates
    :param expected_keys: List of expected collector key names
    :return: ValidationResult with missing keys detailed as errors
    """
    extracted_keys: Set[str] = set()

    if isinstance(templates, list):
        for tmpl in templates:
            _collect_extracted_keys(tmpl, extracted_keys)
    else:
        _collect_extracted_keys(templates, extracted_keys)

    errors: List[ValidationError] = []
    warnings: List[str] = []

    for exp_key in expected_keys:
        if exp_key not in extracted_keys:
            errors.append(
                ValidationError(
                    path=f"data.{exp_key}",
                    message=f"Expected data key '{exp_key}' is not extracted by any step in the template",
                    code="MISSING_EXPECTED_DATA_KEY",
                )
            )

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def _collect_extracted_keys(
    tmpl: Union[TabTemplate, ParallelTemplate, ParameterizedTemplate],
    extracted_keys: Set[str],
) -> None:
    if isinstance(tmpl, TabTemplate):
        step_groups = [tmpl.initSteps, tmpl.perPageSteps, tmpl.steps]
        for group in step_groups:
            if group:
                for step in group:
                    _collect_keys_from_step(step, extracted_keys)

    elif isinstance(tmpl, ParallelTemplate):
        if tmpl.templates:
            for child in tmpl.templates:
                _collect_extracted_keys(child, extracted_keys)

    elif isinstance(tmpl, ParameterizedTemplate):
        if tmpl.template:
            _collect_extracted_keys(tmpl.template, extracted_keys)


def _collect_keys_from_step(step: BaseStep, extracted_keys: Set[str]) -> None:
    if not isinstance(step, BaseStep):
        return

    key = step.key or step.id
    action = step.action or "navigate"

    # Actions that store values in collector
    if action in (
        "data",
        "getUrl",
        "getTitle",
        "getMeta",
        "getCookies",
        "getLocalStorage",
        "getSessionStorage",
        "readData",
        "evaluate",
        "custom",
        "screenshot",
        "savePDF",
        "downloadPDF",
        "downloadFile",
        "eventBaseDownload",
        "virtualScroll",
    ):
        if key:
            extracted_keys.add(key)

    if step.key:
        extracted_keys.add(step.key)

    if step.subSteps:
        for sub in step.subSteps:
            _collect_keys_from_step(sub, extracted_keys)
