# tests/test_scraper_parser.py
# Unit tests for scraper_parser backward compatibility module

import pytest
import stepwright.scraper_parser as sp


def test_scraper_parser_re_exports():
    # Verify types re-exports
    assert sp.BaseStep is not None
    assert sp.NextButtonConfig is not None
    assert sp.ScrollConfig is not None
    assert sp.PaginationConfig is not None
    assert sp.TabTemplate is not None
    assert sp.RunOptions is not None

    # Verify helper re-exports
    assert sp.replace_index_placeholders is not None
    assert sp.replace_data_placeholders is not None
    assert sp.locator_for is not None

    # Verify executor re-exports
    assert sp.execute_step is not None
    assert sp.execute_step_list is not None
    assert sp.execute_tab is not None
    assert sp.clone_step_with_index is not None

    # Verify parser re-exports
    assert sp.run_scraper is not None
    assert sp.run_scraper_with_callback is not None
