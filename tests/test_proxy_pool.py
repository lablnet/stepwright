# tests/test_proxy_pool.py
# Unit tests for Smart Proxy Rotation & Auto-Healing Proxy Pool

import time
import pytest
from stepwright import (
    ProxyPool,
    ProxyConfig,
    ProxyStatus,
    TabTemplate,
    BaseStep,
    RunOptions,
    validate_template_format,
    run_scraper,
)


def test_proxy_pool_initialization():
    """Test initializing ProxyPool from strings, dicts, and ProxyConfigs"""
    pool = ProxyPool(
        proxies=[
            "http://proxy1.com:8080",
            {"server": "http://proxy2.com:8080", "username": "u", "password": "p"},
            ProxyConfig(server="http://proxy3.com:8080"),
        ],
        strategy="round_robin",
    )

    stats = pool.get_stats()
    assert stats["total"] == 3
    assert stats["healthy"] == 3
    assert stats["cooling"] == 0
    assert stats["strategy"] == "round_robin"


def test_proxy_pool_rotation_strategies():
    """Test round_robin, random, and sticky rotation strategies"""
    pool = ProxyPool(
        proxies=["http://p1.com:8080", "http://p2.com:8080"],
        strategy="round_robin",
    )

    # Round Robin
    pr1 = pool.get_proxy()
    pr2 = pool.get_proxy()
    assert pr1.server == "http://p1.com:8080"
    assert pr2.server == "http://p2.com:8080"

    # Sticky Strategy
    pool_sticky = ProxyPool(
        proxies=["http://p1.com:8080", "http://p2.com:8080"],
        strategy="sticky",
    )
    st1 = pool_sticky.get_proxy(session_id="session_A")
    st2 = pool_sticky.get_proxy(session_id="session_A")
    assert st1.server == st2.server


def test_proxy_failure_and_cooldown_recovery():
    """Test tracking failure threshold, cooldown transition, and automatic recovery"""
    pool = ProxyPool(
        proxies=["http://p1.com:8080", "http://p2.com:8080"],
        max_failures=2,
        cooldown_seconds=1,  # 1 second cooldown for fast testing
    )

    assert len(pool.get_healthy_entries()) == 2

    # Report failures for p1
    pool.report_failure("http://p1.com:8080", reason="HTTP 403")
    assert len(pool.get_healthy_entries()) == 2  # 1 failure < 2 max_failures

    pool.report_failure("http://p1.com:8080", reason="HTTP 403")
    # Now p1 should be cooling
    assert len(pool.get_healthy_entries()) == 1
    assert pool.get_stats()["cooling"] == 1

    # Wait for 1 second cooldown expiration
    time.sleep(1.1)

    # Cooldown should be automatically refreshed & restored
    assert len(pool.get_healthy_entries()) == 2
    assert pool.get_stats()["healthy"] == 2


def test_validator_proxy_pool():
    """Test static format validation for proxy pool options"""
    t_valid = TabTemplate(
        tab="valid_pool",
        proxy_pool=["http://proxy1.com:8080"],
        proxy_rotation_strategy="round_robin",
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    assert validate_template_format(t_valid).is_valid is True

    t_invalid = TabTemplate(
        tab="invalid_pool",
        proxy_pool=["http://proxy1.com:8080"],
        proxy_rotation_strategy="invalid_strat",  # invalid strategy
        steps=[BaseStep(id="s1", action="navigate", value="https://example.com")],
    )
    res = validate_template_format(t_invalid)
    assert res.is_valid is False
    assert any(e.code == "INVALID_PROXY_STRATEGY" for e in res.errors)
