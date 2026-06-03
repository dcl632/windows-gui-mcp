"""Verify-after-action helpers.

Every action tool MUST go through verify() before reporting success.
A failed verify auto-triggers a fresh dump_ui_tree() in the response so
the LLM can re-plan instead of retrying blindly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from ..utils.errors import VerifyFailed
from ..utils.retry import wait_for
from .element import ElementSpec, describe_element, find_element

log = logging.getLogger("windows_gui_mcp.verify")


@dataclass
class VerifyPlan:
    """Declarative post-condition for an action."""

    expect_element: ElementSpec | None = None  # element should appear
    expect_disappear: ElementSpec | None = None  # element should vanish
    expect_text_in_value: str | None = None  # focused element value contains text
    expect_state_change: bool = False  # any observable change vs pre-snapshot
    timeout: float = 6.0


def verify(
    plan: VerifyPlan,
    pre_snapshot: dict | None = None,
    target: Any = None,
    window_handle: int | None = None,
) -> dict:
    """Run a verify plan. Returns {ok, evidence, hint}. Never raises."""
    evidence: dict = {"plan": plan.__dict__.copy()}
    ok = True
    if plan.expect_element:
        try:
            found = find_element(plan.expect_element, window_handle=window_handle, timeout=plan.timeout)
            evidence["expect_element"] = describe_element(found)
        except Exception as e:  # noqa: BLE001
            ok = False
            evidence["expect_element_error"] = str(e)
    if plan.expect_disappear:

        def _gone() -> bool:
            try:
                find_element(plan.expect_disappear, window_handle=window_handle, timeout=0.4)
                return False
            except Exception:
                return True

        gone = wait_for(_gone, timeout=plan.timeout, interval=0.3) or False
        evidence["expect_disappear"] = bool(gone)
        ok = ok and bool(gone)
    if plan.expect_text_in_value and target is not None:

        def _has_text() -> bool:
            try:
                snap = describe_element(target)
                return (snap.get("value") or "").find(plan.expect_text_in_value) >= 0
            except Exception:
                return False

        ok_text = wait_for(_has_text, timeout=plan.timeout, interval=0.25) or False
        evidence["expect_text_in_value"] = ok_text
        ok = ok and ok_text
    if plan.expect_state_change and target is not None and pre_snapshot is not None:

        def _changed() -> bool:
            try:
                cur = describe_element(target)
                return cur != pre_snapshot
            except Exception:
                return False

        changed = wait_for(_changed, timeout=plan.timeout, interval=0.25) or False
        evidence["state_changed"] = changed
        ok = ok and changed
    if (
        not plan.expect_element
        and not plan.expect_disappear
        and not plan.expect_text_in_value
        and not plan.expect_state_change
    ):
        evidence["note"] = "no post-conditions provided — caller responsible for verification"
    return {"ok": ok, "evidence": evidence}


def assert_verified(result: dict, action: str) -> None:
    if not result.get("ok"):
        raise VerifyFailed(f"{action} could not be verified: {result.get('evidence')}")


def make_predicate(check: Callable[[], bool], timeout: float = 5.0) -> dict:
    """Generic boolean predicate verifier — used by hotkey/screenshot tools."""
    ok = wait_for(check, timeout=timeout, interval=0.3) or False
    return {"ok": bool(ok), "evidence": {"predicate": check.__name__}}
