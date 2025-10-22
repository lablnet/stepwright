# scraper_parser.py
# Backward compatibility wrapper for refactored modules
# Author: Muhammad Umer Farooq <umer@lablnet.com>

"""
This module maintains backward compatibility with existing code.
All functionality has been refactored into separate modules:
- step_types.py: Type definitions and dataclasses
- helpers.py: Utility functions
- executor.py: Core execution logic
- parser.py: Public API

Import from this module for backward compatibility, or import directly from the new modules.
"""

# Re-export all types
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

# Re-export helper functions
from helpers import (
    replace_index_placeholders,
    replace_data_placeholders,
    locator_for,
)

# Re-export executor functions
from executor import (
    execute_step,
    execute_step_list,
    execute_tab,
    clone_step_with_index,
)

# Re-export public API
from parser import (
    run_scraper,
    run_scraper_with_callback,
)

__all__ = [
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
    "clone_step_with_index",
    # Public API
    "run_scraper",
    "run_scraper_with_callback",
]
