"""Polling helpers — used by every verify_after step."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def wait_for(
    predicate: Callable[[], T | None],
    timeout: float = 8.0,
    interval: float = 0.25,
) -> T | None:
    """Poll predicate() until it returns truthy or timeout. Returns last value."""
    deadline = time.monotonic() + timeout
    last: T | None = None
    while time.monotonic() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    return last


def with_retries(fn: Callable[[], T], attempts: int = 3, base_delay: float = 0.4) -> T:
    """Exponential backoff for transient COM/UIA failures."""
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — surface caller-side
            last_exc = exc
            time.sleep(base_delay * (2**i))
    assert last_exc is not None
    raise last_exc
