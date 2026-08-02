# test_validator.py
# Unit tests for StepWright template and data validation
# Author: Muhammad Umer Farooq <umer@lablnet.com>

import pytest
from stepwright import (
    BaseStep,
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    validate_template_format,
    validate_template_data,
    PaginationConfig,
    NextButtonConfig,
)


def test_validate_template_format_valid():
    """Test format validation on a perfectly valid TabTemplate"""
    template = TabTemplate(
        tab="valid_tab",
        steps=[
            BaseStep(id="nav", action="navigate", value="https://example.com"),
            BaseStep(
                id="extract",
                action="foreach",
                object=".item",
                object_type="class",
                subSteps=[
                    BaseStep(
                        id="title",
                        action="data",
                        object="h2",
                        object_type="tag",
                        key="title",
                    )
                ],
            ),
        ],
    )

    result = validate_template_format(template)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_template_format_invalid_action():
    """Test format validation with unknown action and missing required fields"""
    template = TabTemplate(
        tab="invalid_tab",
        steps=[
            BaseStep(id="bad_action", action="non_existent_action"),
            BaseStep(id="nav_no_value", action="navigate"),
            BaseStep(id="input_no_obj", action="input"),
        ],
    )

    result = validate_template_format(template)
    assert result.is_valid is False
    codes = [e.code for e in result.errors]
    assert "INVALID_ACTION" in codes
    assert "MISSING_REQUIRED_VALUE" in codes
    assert "MISSING_REQUIRED_OBJECT" in codes


def test_validate_template_format_foreach_and_open_errors():
    """Test foreach and open step requirements"""
    template = TabTemplate(
        tab="loop_errors",
        steps=[
            BaseStep(id="bad_foreach", action="foreach"),  # missing source & subSteps
            BaseStep(
                id="bad_open", action="open", object=".link"
            ),  # missing subSteps
        ],
    )

    result = validate_template_format(template)
    assert result.is_valid is False
    codes = [e.code for e in result.errors]
    assert "MISSING_FOREACH_SOURCE" in codes
    assert "MISSING_SUBSTEPS" in codes


def test_validate_template_format_selector_type_error():
    """Test invalid selector type detection"""
    template = TabTemplate(
        tab="selector_err",
        steps=[
            BaseStep(
                id="s1",
                action="click",
                object="btn",
                object_type="invalid_type",  # invalid
            )
        ],
    )

    result = validate_template_format(template)
    assert result.is_valid is False
    assert result.errors[0].code == "INVALID_SELECTOR_TYPE"


def test_validate_template_format_parallel_and_parameterized():
    """Test validation on ParallelTemplate and ParameterizedTemplate"""
    base_tab = TabTemplate(
        tab="base_{{keyword}}",
        steps=[BaseStep(id="nav", action="navigate", value="https://example.com/{{keyword}}")],
    )

    param_tmpl = ParameterizedTemplate(
        template=base_tab,
        parameter_key="keyword",
        values=["python", "playwright"],
    )

    parallel_tmpl = ParallelTemplate(templates=[param_tmpl])

    res = validate_template_format(parallel_tmpl)
    assert res.is_valid is True

    # Test invalid parameterized template
    bad_param = ParameterizedTemplate(template=None, parameter_key="", values=[])
    bad_res = validate_template_format(bad_param)
    assert bad_res.is_valid is False


def test_validate_template_data_valid():
    """Test data validation when all expected keys are extracted"""
    template = TabTemplate(
        tab="search",
        steps=[
            BaseStep(id="title", action="data", object=".title", key="title_key"),
            BaseStep(id="url", action="getUrl", key="current_url"),
            BaseStep(
                id="loop",
                action="foreach",
                object=".item",
                subSteps=[
                    BaseStep(id="price", action="data", object=".price", key="price_key")
                ],
            ),
        ],
    )

    expected = ["title_key", "current_url", "price_key"]
    res = validate_template_data(template, expected)
    assert res.is_valid is True
    assert len(res.errors) == 0


def test_validate_template_data_missing_keys():
    """Test data validation when expected keys are missing"""
    template = TabTemplate(
        tab="search",
        steps=[
            BaseStep(id="title", action="data", object=".title", key="title_key"),
        ],
    )

    expected = ["title_key", "missing_price", "missing_author"]
    res = validate_template_data(template, expected)
    assert res.is_valid is False
    assert len(res.errors) == 2
    err_paths = [e.path for e in res.errors]
    assert "data.missing_price" in err_paths
    assert "data.missing_author" in err_paths


def test_validator_edge_cases():
    """Test detailed validation error branches across Tab, Parallel, Parameterized templates and Steps"""
    from stepwright.step_types import PaginationConfig

    bad_tab = TabTemplate(
        tab="t1",
        engine="invalid_browser",
        driver=123,
        proxy_rotation_strategy="invalid_strat",
        pagination=PaginationConfig(strategy="invalid_strat"),
        steps=[BaseStep(id="s1", action="click", object_type="invalid_type", object="btn")]
    )
    res = validate_template_format(bad_tab)
    assert res.is_valid is False
    assert len(res.errors) >= 3

    next_pag_tab = TabTemplate(
        tab="t2",
        pagination=PaginationConfig(strategy="next"),
        steps=[BaseStep(id="s1", action="click", object="#btn")]
    )
    res_pag = validate_template_format(next_pag_tab)
    assert any(e.code == "MISSING_NEXT_BUTTON" for e in res_pag.errors)

    bad_steps_tab = TabTemplate(
        tab="t3",
        steps=[
            BaseStep(id="s1", action="open"),
            BaseStep(id="s2", action="mouseMove"),
            BaseStep(id="s3", action="if"),
            BaseStep(id="s4", action="while"),
            BaseStep(id="s5", action="try"),
            "not_a_step_instance"
        ]
    )
    res_steps = validate_template_format(bad_steps_tab)
    assert res_steps.is_valid is False
    assert len(res_steps.errors) >= 5


def test_validator_action_validation_branches():
    """Test validator checks for missing object/value across various step actions"""
    tab = TabTemplate(
        tab="v_actions",
        steps=[
            BaseStep(id="a1", action="input", object_type="id"),  # missing object & value
            BaseStep(id="a2", action="navigate"),  # missing value
            BaseStep(id="a3", action="savePDF"),  # missing value
            BaseStep(id="a4", action="writeData"),  # missing value
            BaseStep(id="a5", action="readData"),  # missing value
            BaseStep(id="a6", action="custom"),  # missing callback
        ]
    )
    res = validate_template_format(tab)
    assert res.is_valid is False
    codes = [e.code for e in res.errors]
    assert "MISSING_REQUIRED_OBJECT" in codes
    assert "MISSING_REQUIRED_VALUE" in codes
    assert "MISSING_CALLBACK" in codes


def test_validator_proxy_next_button_and_driver_branches():
    """Test validator checks for invalid proxy server, nextButton invalid selector type, invalid driver, and parallel templates"""
    from stepwright.step_types import PaginationConfig, ProxyConfig, ParallelTemplate, ParameterizedTemplate
    from stepwright.validator import validate_template_data


    bad_tab = TabTemplate(
        tab="v_proxy_btn",
        proxy=ProxyConfig(server=""),  # empty server
        pagination=PaginationConfig(
            strategy="next",
            nextButton=BaseStep(id="nb", action="click", object_type="invalid_sel_type", object="btn")
        ),
        driver=12345,  # invalid driver type
        steps=[]  # empty steps warning
    )
    res = validate_template_format(bad_tab)
    assert res.is_valid is False
    codes = [e.code for e in res.errors]
    assert "INVALID_PROXY_SERVER" in codes

    # Test validate_template_data with ParallelTemplate and ParameterizedTemplate
    parallel_tmpl = ParallelTemplate(
        templates=[
            TabTemplate(tab="p1", steps=[BaseStep(id="d1", action="data", object="#item", key="k1")]),
            TabTemplate(tab="p2", steps=[BaseStep(id="d2", action="data", object="#item", key="k2")])
        ]
    )
    res_par = validate_template_data(parallel_tmpl, ["k1", "k2"])
    assert res_par.is_valid is True

    param_tmpl = ParameterizedTemplate(
        template=TabTemplate(tab="pm1", steps=[BaseStep(id="d3", action="data", object="#item", key="k3")]),
        parameter_key="keyword",
        values=["v1"]
    )
    res_param = validate_template_data(param_tmpl, ["k3"])
    assert res_param.is_valid is True


    assert "INVALID_SELECTOR_TYPE" in codes
    assert "INVALID_DRIVER" in codes

    # ParallelTemplate invalid concurrency and empty templates
    bad_parallel = ParallelTemplate(templates=[], max_concurrency=-1)
    res_p = validate_template_format(bad_parallel)
    assert res_p.is_valid is False
    p_codes = [e.code for e in res_p.errors]
    assert "INVALID_CONCURRENCY" in p_codes
    assert "EMPTY_PARALLEL_TEMPLATES" in p_codes

    # ParameterizedTemplate invalid concurrency and missing key
    bad_param = ParameterizedTemplate(template=None, parameter_key="", values=[], max_concurrency=0)
    res_pm = validate_template_format(bad_param)
    assert res_pm.is_valid is False
    pm_codes = [e.code for e in res_pm.errors]
    assert "MISSING_BASE_TEMPLATE" in pm_codes

    # validate_template_data missing expected keys check
    data_tab = TabTemplate(
        tab="v_data",
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")]
    )
    res_data = validate_template_data(data_tab, expected_keys=["missing_output_key"])
    assert res_data.is_valid is False
    assert any(e.code == "MISSING_EXPECTED_DATA_KEY" for e in res_data.errors)






