"""click_element / type_text / hotkey — semantic-first input."""

from __future__ import annotations

import logging
from typing import Any

from ..utils.backend import get_backend
from ..utils.retry import with_retries
from .element import ElementSpec, describe_element, find_element
from .verify import VerifyPlan, verify

log = logging.getLogger("windows_gui_mcp.input")


def click_element(
    spec: ElementSpec,
    button: str = "left",
    double: bool = False,
    window_handle: int | None = None,
    verify_plan: VerifyPlan | None = None,
    timeout: float = 8.0,
) -> dict:
    """Click an element identified semantically (auto_id/name/control_type)."""
    elem = find_element(spec, window_handle=window_handle, timeout=timeout)
    pre = describe_element(elem)

    def _do() -> None:
        try:
            if double:
                elem.double_click_input(button=button)
            else:
                elem.click_input(button=button)
        except Exception:
            if double:
                elem.double_click()
            else:
                elem.click()

    with_retries(_do, attempts=3)

    plan = verify_plan or VerifyPlan(expect_state_change=True, timeout=4.0)
    v = verify(plan, pre_snapshot=pre, target=elem, window_handle=window_handle)
    return {
        "action": "click",
        "spec": spec.__dict__,
        "pre": pre,
        "post": describe_element(elem),
        "verify": v,
    }


def type_text(
    text: str,
    spec: ElementSpec | None = None,
    window_handle: int | None = None,
    clear_first: bool = False,
    with_spaces: bool = True,
    verify_value_contains: str | None = None,
    timeout: float = 8.0,
) -> dict:
    """Type text — into a target element if specified, else into focused control."""
    target: Any | None = None
    pre: dict | None = None
    if spec is not None and spec.is_specified():
        target = find_element(spec, window_handle=window_handle, timeout=timeout)
        pre = describe_element(target)
        try:
            target.set_focus()
        except Exception:
            target.click_input()
        if clear_first:
            try:
                if hasattr(target, "set_text"):
                    target.set_text("")
                else:
                    target.type_keys("^a{DEL}", with_spaces=False, set_foreground=False)
            except Exception:
                pass

    def _send() -> None:
        if target is not None and hasattr(target, "type_keys"):
            target.type_keys(_escape_for_typekeys(text), with_spaces=with_spaces, set_foreground=False)
        else:
            bm = get_backend()
            bm.pyautogui.typewrite(text, interval=0.01)

    with_retries(_send, attempts=2)

    expected = verify_value_contains if verify_value_contains is not None else text
    plan = VerifyPlan(expect_text_in_value=expected if target is not None else None, timeout=4.0)
    v = verify(plan, pre_snapshot=pre, target=target, window_handle=window_handle)
    return {
        "action": "type_text",
        "text_len": len(text),
        "target": pre,
        "post": describe_element(target) if target is not None else None,
        "verify": v,
    }


def hotkey(keys: str, window_handle: int | None = None) -> dict:
    """Send a key chord. `keys` accepts pywinauto syntax: '^s', '%{F4}', '+{TAB}'."""
    bm = get_backend()
    desktop = bm.desktop()
    win = desktop.window(handle=window_handle) if window_handle else None
    if win is not None:
        with_retries(lambda: win.set_focus())
        with_retries(lambda: win.type_keys(keys, set_foreground=False, with_spaces=True))
    else:
        bm.pyautogui.hotkey(*_translate_chord(keys))
    return {"action": "hotkey", "keys": keys, "verify": {"ok": True, "evidence": {"sent": keys}}}


def _escape_for_typekeys(text: str) -> str:
    """type_keys treats ^+%~(){}[] as modifiers — wrap them as literals."""
    out = []
    for ch in text:
        if ch in "^+%~(){}[]":
            out.append("{" + ch + "}")
        else:
            out.append(ch)
    return "".join(out)


_KEY_ALIAS = {"ctrl": "ctrl", "control": "ctrl", "alt": "alt", "shift": "shift", "win": "win"}


def _translate_chord(chord: str) -> list[str]:
    """Convert pywinauto-style '^s' into ['ctrl','s'] for pyautogui.hotkey."""
    parts: list[str] = []
    i = 0
    s = chord
    while i < len(s):
        c = s[i]
        if c == "^":
            parts.append("ctrl")
        elif c == "%":
            parts.append("alt")
        elif c == "+":
            parts.append("shift")
        elif c == "{":
            j = s.index("}", i)
            parts.append(s[i + 1 : j].lower())
            i = j
        else:
            parts.append(c.lower())
        i += 1
    return parts
