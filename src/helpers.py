# helpers.py
# Helper functions for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import asyncio
import pathlib
import re
from typing import Any, Dict, Optional

from playwright.async_api import Locator

from step_types import SelectorType


def replace_index_placeholders(text: Optional[str], i: int) -> Optional[str]:
    """Replace index placeholders ({{ i }}, {{ i_plus1 }}) in text"""
    if not text:
        return text
    # Convert to string if it's not already a string
    text_str = str(text) if not isinstance(text, str) else text
    return (
        text_str.replace("{{ i }}", str(i))
        .replace("{{i}}", str(i))
        .replace("{{ i_plus1 }}", str(i + 1))
        .replace("{{i_plus1}}", str(i + 1))
    )


def replace_data_placeholders(text: Optional[str], collector: Dict[str, Any]) -> Optional[str]:
    """Replace data placeholders ({{ key }}) in text with values from collector"""
    if not text:
        return text

    def _repl(m: re.Match) -> str:
        key = m.group(1).strip()
        val = collector.get(key, m.group(0))
        if val is None:
            return m.group(0)
        # sanitize for filenames
        s = str(val).strip()
        s = re.sub(r"[^a-zA-Z0-9\s\-_]", "", s)
        s = re.sub(r"\s+", "_", s)
        return s

    return re.sub(r"\{\{\s*([^}]+)\s*\}\}", _repl, text)


def locator_for(context, type: Optional[SelectorType], selector: str) -> Locator:
    """
    Create a Playwright locator based on selector type.
    Context can be either a Page or a Locator (for scoped queries).
    """
    if not type:
        return context.locator(selector)
    if type == "id":
        return context.locator(f"#{selector}")
    if type == "class":
        return context.locator(f".{selector}")
    if type == "tag":
        return context.locator(selector)
    if type == "xpath":
        return context.locator(f"xpath={selector}")
    return context.locator(selector)


async def _ensure_dir(path_str: str) -> None:
    """Ensure directory exists for given file path"""
    pathlib.Path(path_str).parent.mkdir(parents=True, exist_ok=True)


async def maybe_await(x):
    """Await if coroutine, otherwise return as-is"""
    if asyncio.iscoroutine(x):
        return await x
    return x
