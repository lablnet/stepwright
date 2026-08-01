# drivers/__init__.py
# Package exports for StepWright Drivers

from __future__ import annotations

from typing import Any, Union

from .base_driver import BaseDriver
from .playwright_driver import PlaywrightDriver

# Driver registry instance cache
_default_driver_instance: Union[PlaywrightDriver, None] = None
_active_driver: Union[BaseDriver, None] = None


def set_active_driver(driver: Union[str, BaseDriver, None]) -> BaseDriver:
    """
    Set the active thread/execution driver instance.

    @since 2.0.0
    """
    global _active_driver
    _active_driver = get_driver(driver)
    return _active_driver


def get_driver(driver: Union[str, BaseDriver, None] = None) -> BaseDriver:
    """
    Get or resolve a browser driver instance.

    :param driver: Driver name string (e.g. 'playwright') or a BaseDriver instance
    :return: BaseDriver instance

    @since 2.0.0
    """
    global _default_driver_instance, _active_driver
    if driver is None:
        if _active_driver is not None:
            return _active_driver
        if _default_driver_instance is None:
            _default_driver_instance = PlaywrightDriver()
        return _default_driver_instance
    elif driver == "playwright":
        if _default_driver_instance is None:
            _default_driver_instance = PlaywrightDriver()
        return _default_driver_instance
    elif isinstance(driver, BaseDriver):
        return driver
    else:
        raise ValueError(f"Unsupported driver: {driver}. Expected 'playwright' or an instance of BaseDriver.")


__all__ = [
    "BaseDriver",
    "PlaywrightDriver",
    "get_driver",
    "set_active_driver",
]
