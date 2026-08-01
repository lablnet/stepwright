# proxy_pool.py
# Smart Proxy Rotation & Auto-Healing Proxy Pool for StepWright
# Author: Muhammad Umer Farooq <umer@lablnet.com>

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .step_types import ProxyConfig


class ProxyStatus(Enum):
    """Status of a proxy entry in the pool"""
    HEALTHY = "healthy"
    COOLING = "cooling"
    BANNED = "banned"


@dataclass
class ProxyEntry:
    """
    Represents a single proxy entry in the pool with health statistics.

    @since 2.0.0
    """
    config: ProxyConfig
    status: ProxyStatus = ProxyStatus.HEALTHY
    failure_count: int = 0
    success_count: int = 0
    cooldown_until: float = 0.0


class ProxyPool:
    """
    Smart Proxy Rotation Pool Manager.

    Supports round_robin, random, and sticky rotation strategies with
    automatic ban detection, failure counting, and cooldown recovery.

    @since 2.0.0
    """

    def __init__(
        self,
        proxies: Optional[List[Union[str, Dict[str, str], ProxyConfig]]] = None,
        strategy: str = "round_robin",
        max_failures: int = 3,
        cooldown_seconds: int = 300,
    ) -> None:
        """
        Initialize ProxyPool.

        :param proxies: List of proxy strings ("http://ip:port"), dicts, or ProxyConfig objects
        :param strategy: 'round_robin' | 'random' | 'sticky'
        :param max_failures: Number of consecutive failures before cooling down proxy
        :param cooldown_seconds: Duration in seconds to cool down a failing proxy
        """
        self.strategy = (strategy or "round_robin").lower()
        if self.strategy not in ("round_robin", "random", "sticky"):
            raise ValueError(f"Invalid proxy rotation strategy '{strategy}'. Must be 'round_robin', 'random', or 'sticky'.")

        self.max_failures = max(1, max_failures)
        self.cooldown_seconds = max(1, cooldown_seconds)
        self.entries: List[ProxyEntry] = []
        self._rr_index: int = 0
        self._sticky_map: Dict[str, ProxyConfig] = {}

        if proxies:
            for p in proxies:
                self.add_proxy(p)

    def add_proxy(self, proxy: Union[str, Dict[str, str], ProxyConfig]) -> ProxyEntry:
        """Add a new proxy to the pool."""
        if isinstance(proxy, str):
            cfg = ProxyConfig(server=proxy)
        elif isinstance(proxy, dict):
            cfg = ProxyConfig(
                server=proxy.get("server", ""),
                username=proxy.get("username"),
                password=proxy.get("password"),
                bypass=proxy.get("bypass"),
            )
        elif isinstance(proxy, ProxyConfig):
            cfg = proxy
        else:
            raise ValueError(f"Invalid proxy object type: {type(proxy)}. Expected str, dict, or ProxyConfig.")

        entry = ProxyEntry(config=cfg)
        self.entries.append(entry)
        return entry

    def _refresh_cooldowns(self) -> None:
        """Check and restore proxies whose cooldown period has expired."""
        now = time.time()
        for entry in self.entries:
            if entry.status == ProxyStatus.COOLING and now >= entry.cooldown_until:
                entry.status = ProxyStatus.HEALTHY
                entry.failure_count = 0
                entry.cooldown_until = 0.0

    def get_healthy_entries(self) -> List[ProxyEntry]:
        """Return list of currently healthy (or recovered) proxy entries."""
        self._refresh_cooldowns()
        healthy = [e for e in self.entries if e.status == ProxyStatus.HEALTHY]
        return healthy

    def get_proxy(self, session_id: Optional[str] = None) -> Optional[ProxyConfig]:
        """
        Get a proxy config according to the active rotation strategy.

        :param session_id: Session/tab ID for sticky proxy rotation
        :return: ProxyConfig or None if no healthy proxies are available
        """
        healthy = self.get_healthy_entries()
        if not healthy:
            return None

        if self.strategy == "sticky" and session_id:
            if session_id in self._sticky_map:
                sticky_cfg = self._sticky_map[session_id]
                # Check if still healthy
                if any(e.config.server == sticky_cfg.server and e.status == ProxyStatus.HEALTHY for e in healthy):
                    return sticky_cfg

            # Assign new sticky proxy
            selected = healthy[0].config
            self._sticky_map[session_id] = selected
            return selected

        elif self.strategy == "random":
            return random.choice(healthy).config

        else:  # round_robin
            # Round robin means pick each proxy once in order
            idx = self._rr_index % len(healthy)
            self._rr_index += 1
            return healthy[idx].config

    def report_success(self, server_url: str) -> None:
        """Report successful usage of a proxy."""
        for entry in self.entries:
            if entry.config.server == server_url:
                entry.success_count += 1
                entry.failure_count = 0
                entry.status = ProxyStatus.HEALTHY
                break

    def report_failure(self, server_url: str, reason: Optional[str] = None) -> None:
        """
        Report failure/ban for a proxy.
        If failure count reaches max_failures, puts proxy in COOLING status.
        """
        now = time.time()
        for entry in self.entries:
            if entry.config.server == server_url:
                entry.failure_count += 1
                if entry.failure_count >= self.max_failures:
                    entry.status = ProxyStatus.COOLING
                    entry.cooldown_until = now + self.cooldown_seconds
                    print(f"   ⚠️  Proxy '{server_url}' cooled down for {self.cooldown_seconds}s (failures: {entry.failure_count}). Reason: {reason or 'Max failures exceeded'}")
                break

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool health statistics."""
        self._refresh_cooldowns()
        return {
            "total": len(self.entries),
            "healthy": sum(1 for e in self.entries if e.status == ProxyStatus.HEALTHY),
            "cooling": sum(1 for e in self.entries if e.status == ProxyStatus.COOLING),
            "banned": sum(1 for e in self.entries if e.status == ProxyStatus.BANNED),
            "strategy": self.strategy,
        }
