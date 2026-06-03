"""Thin dispatch layer — translates MCP arguments into core calls.

Every dispatcher records to trace.* and, on any failure, attaches a
freshly-dumped UI tree to help the LLM re-plan (matches the rule:
'失敗時先重新 dump UI tree').
"""

from __future__ import annotations

import logging

from ..core import element as core_element
from ..core import fallback as core_fallback
from ..core import input as core_input
from ..core import screenshot as core_screenshot
from ..core import trace as core_trace
from ..core import verify as core_verify
from ..core import wait as core_wait
from ..core import window as core_window
from ..core.element import ElementSpec
from .schemas import (
    ClickElementArgs,
    DumpUITreeArgs,
    ElementSpecModel,
    FallbackClickArgs,
    FindElementArgs,
    FocusWindowArgs,
    GenScriptArgs,
    HotkeyArgs,
    ListWindowsArgs,
    ScreenshotArgs,
    TypeTextArgs,
    VerifyTextExistsArgs,
    WaitUntilElementArgs,
)

log = logging.getLogger("windows_gui_mcp.dispatch")


def _spec(model: ElementSpecModel | None) -> ElementSpec:
    if model is None:
        return ElementSpec()
    return ElementSpec(
        automation_id=model.automation_id,
        name=model.name,
        control_type=model.control_type,
        class_name=model.class_name,
        nth=model.nth,
    )


def _attach_recovery(result: dict, window_handle: int | None) -> dict:
    """On failure, append a UI tree dump so the model can re-plan."""
    try:
        result["recovery_ui_tree"] = core_element.dump_ui_tree(window_handle=window_handle, max_depth=4)
    except Exception as e:  # noqa: BLE001
        result["recovery_ui_tree_error"] = str(e)
    return result


def _wrap(tool: str, args: dict, fn):
    try:
        result = fn()
        ok = True
        if isinstance(result, dict) and "verify" in result:
            ok = bool(result.get("verify", {}).get("ok", True))
        core_trace.record(tool, args, result if isinstance(result, dict) else {"value": result}, ok)
        return result
    except Exception as e:  # noqa: BLE001
        out: dict = {"error": str(e), "type": type(e).__name__}
        out = _attach_recovery(out, args.get("window_handle"))
        core_trace.record(tool, args, out, ok=False, note="exception")
        return out


def list_windows(args: ListWindowsArgs) -> dict:
    return _wrap(
        "list_windows", args.model_dump(), lambda: {"windows": core_window.list_windows(args.visible_only)}
    )


def focus_window(args: FocusWindowArgs) -> dict:
    return _wrap(
        "focus_window",
        args.model_dump(),
        lambda: core_window.focus_window(args.title_regex, prefer=args.prefer),
    )


def dump_ui_tree(args: DumpUITreeArgs) -> dict:
    return _wrap(
        "dump_ui_tree",
        args.model_dump(),
        lambda: core_element.dump_ui_tree(
            window_handle=args.window_handle, max_depth=args.max_depth, prefer=args.prefer
        ),
    )


def find_element(args: FindElementArgs) -> dict:
    def _do() -> dict:
        elem = core_element.find_element(
            _spec(args.spec), window_handle=args.window_handle, timeout=args.timeout, prefer=args.prefer
        )
        return {"element": core_element.describe_element(elem)}

    return _wrap("find_element", args.model_dump(), _do)


def click_element(args: ClickElementArgs) -> dict:
    def _do() -> dict:
        plan = core_verify.VerifyPlan(
            expect_element=_spec(args.expect_element_after) if args.expect_element_after else None,
            expect_disappear=_spec(args.expect_element_disappear) if args.expect_element_disappear else None,
            expect_state_change=not (args.expect_element_after or args.expect_element_disappear),
            timeout=4.0,
        )
        return core_input.click_element(
            _spec(args.spec),
            button=args.button,
            double=args.double,
            window_handle=args.window_handle,
            verify_plan=plan,
            timeout=args.timeout,
        )

    return _wrap("click_element", args.model_dump(), _do)


def type_text(args: TypeTextArgs) -> dict:
    return _wrap(
        "type_text",
        args.model_dump(),
        lambda: core_input.type_text(
            args.text,
            spec=_spec(args.spec) if args.spec else None,
            window_handle=args.window_handle,
            clear_first=args.clear_first,
            with_spaces=args.with_spaces,
            verify_value_contains=args.verify_value_contains,
            timeout=args.timeout,
        ),
    )


def hotkey(args: HotkeyArgs) -> dict:
    return _wrap(
        "hotkey", args.model_dump(), lambda: core_input.hotkey(args.keys, window_handle=args.window_handle)
    )


def screenshot(args: ScreenshotArgs) -> dict:
    return _wrap(
        "screenshot",
        args.model_dump(),
        lambda: core_screenshot.screenshot(
            window_handle=args.window_handle,
            region=args.region,
            save_path=args.save_path,
            return_base64=args.return_base64,
        ),
    )


def wait_until_element(args: WaitUntilElementArgs) -> dict:
    return _wrap(
        "wait_until_element",
        args.model_dump(),
        lambda: core_wait.wait_until_element(
            _spec(args.spec),
            timeout=args.timeout,
            state=args.state,
            window_handle=args.window_handle,
        ),
    )


def verify_text_exists(args: VerifyTextExistsArgs) -> dict:
    return _wrap(
        "verify_text_exists",
        args.model_dump(),
        lambda: core_wait.verify_text_exists(
            args.text,
            source=args.source,
            window_handle=args.window_handle,
            region=args.region,
            languages=args.languages,
        ),
    )


def fallback_click_by_image_or_ocr(args: FallbackClickArgs) -> dict:
    return _wrap(
        "fallback_click_by_image_or_ocr",
        args.model_dump(),
        lambda: core_fallback.fallback_click_by_image_or_ocr(
            image_path=args.image_path,
            text=args.text,
            confidence=args.confidence,
            languages=args.languages,
            region=args.region,
            double=args.double,
            button=args.button,
        ),
    )


def generate_stable_script_from_trace(args: GenScriptArgs) -> dict:
    return _wrap(
        "generate_stable_script_from_trace",
        args.model_dump(),
        lambda: core_trace.generate_stable_script_from_trace(out_path=args.out_path),
    )
