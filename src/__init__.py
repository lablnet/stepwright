"""
StepWright - A powerful web scraping library built with Playwright

A declarative, step-by-step approach to web automation and data extraction.
"""

__version__ = "0.1.1"
__author__ = "Muhammad Umer Farooq"
__email__ = "umer@lablnet.com"

# Import main API
from parser import run_scraper, run_scraper_with_callback

# Import types
from step_types import (
    BaseStep,
    NextButtonConfig,
    ScrollConfig,
    PaginationConfig,
    TabTemplate,
    RunOptions,
    SelectorType,
    DataType,
)

# Import helpers (for advanced usage)
from helpers import (
    replace_index_placeholders,
    replace_data_placeholders,
    locator_for,
)

# Import executor functions (for advanced usage)
from executor import (
    execute_step,
    execute_step_list,
    execute_tab,
)

# Import low-level scraper functions (for advanced usage)
from scraper import (
    get_browser,
    navigate,
    elem,
    input,
    click,
    double_click,
    click_check_box,
    get_data,
)

__all__ = [
    # Version
    "__version__",
    # Main API
    "run_scraper",
    "run_scraper_with_callback",
    # Types
    "BaseStep",
    "NextButtonConfig",
    "ScrollConfig",
    "PaginationConfig",
    "TabTemplate",
    "RunOptions",
    "SelectorType",
    "DataType",
    # Helpers
    "replace_index_placeholders",
    "replace_data_placeholders",
    "locator_for",
    # Executor
    "execute_step",
    "execute_step_list",
    "execute_tab",
    # Low-level scraper
    "get_browser",
    "navigate",
    "elem",
    "input",
    "click",
    "double_click",
    "click_check_box",
    "get_data",
]
