# handlers/__init__.py
# Handler modules for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

# Import data handlers
from .data_handlers import (
    _handle_data_extraction,
)

# Import file handlers
from .file_handlers import (
    _handle_event_download,
    _handle_save_pdf,
    _handle_download_pdf,
)

# Import loop handlers
from .loop_handlers import (
    _handle_foreach,
    _handle_open,
    clone_step_with_index,
)

# Import page action handlers
from .page_actions import (
    _handle_reload,
    _handle_get_url,
    _handle_get_title,
    _handle_get_meta,
    _handle_get_cookies,
    _handle_set_cookies,
    _handle_get_local_storage,
    _handle_set_local_storage,
    _handle_get_session_storage,
    _handle_set_session_storage,
    _handle_get_viewport_size,
    _handle_set_viewport_size,
    _handle_screenshot,
    _handle_wait_for_selector,
    _handle_evaluate,
)

# Import interaction handlers
from .interaction_handlers import (
    _handle_hover,
    _handle_select,
    _handle_drag_and_drop,
    _handle_upload,
    _handle_virtual_scroll,
)

# Import data flow handlers
from .data_flow_handlers import (
    _handle_read_data,
    _handle_write_data,
    _handle_custom_callback,
)

__all__ = [
    # Data handlers
    "_handle_data_extraction",
    # File handlers
    "_handle_event_download",
    "_handle_save_pdf",
    "_handle_download_pdf",
    # Loop handlers
    "_handle_foreach",
    "_handle_open",
    "clone_step_with_index",
    # Page action handlers
    "_handle_reload",
    "_handle_get_url",
    "_handle_get_title",
    "_handle_get_meta",
    "_handle_get_cookies",
    "_handle_set_cookies",
    "_handle_get_local_storage",
    "_handle_set_local_storage",
    "_handle_get_session_storage",
    "_handle_set_session_storage",
    "_handle_get_viewport_size",
    "_handle_set_viewport_size",
    "_handle_screenshot",
    "_handle_wait_for_selector",
    "_handle_evaluate",
    # Interaction handlers
    "_handle_hover",
    "_handle_select",
    "_handle_drag_and_drop",
    "_handle_upload",
    "_handle_virtual_scroll",
    # Data flow handlers
    "_handle_read_data",
    "_handle_write_data",
    "_handle_custom_callback",
]
