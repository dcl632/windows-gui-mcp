"""wait_until_element + verify_text_exists."""

from __future__ import annotations

import logging

from .element import ElementSpec, describe_element, find_element
from .ocr import find_text_on_screen
from .screenshot import _capture

log = logging.getLogger("windows_gui_mcp.wait")


def wait_until_element(
    spec: ElementSpec,
    timeout: float = 10.0,
    state: str = "visible",
    window_handle: int | None = None,
) -> dict:
    """Block until element matches `state`. State ∈ {visible, enabled, exists}."""
    elem = find_element(spec, window_handle=window_handle, timeout=timeout)
    snap = describe_element(elem)
    ok = (
        (state == "visible" and snap["visible"])
        or (state == "enabled" and snap["enabled"])
        or (state == "exists")
    )
    return {"ok": ok, "snapshot": snap, "state": state, "spec": spec.__dict__}


def verify_text_exists(
    text: str,
    source: str = "ui_tree",
    window_handle: int | None = None,
    region: tuple[int, int, int, int] | None = None,
    languages: list[str] | None = None,
) -> dict:
    """Confirm `text` is present.

    source='ui_tree' walks the focused window's UIA tree for cheap, exact match.
    source='ocr' captures the screen and runs the OCR ladder (last resort).
    """
    if source == "ui_tree":
        from .element import dump_ui_tree

        tree = dump_ui_tree(window_handle=window_handle, max_depth=12)
        flat = _flatten(tree["tree"])
        hits = [n for n in flat if text in (n.get("name") or "") or text in (n.get("value") or "")]
        return {"ok": bool(hits), "source": "ui_tree", "hits": hits[:10]}
    img = _capture(window_handle=window_handle, region=region)
    matches = find_text_on_screen(text, image=img, languages=languages, fuzzy=True, region=region)
    return {
        "ok": bool(matches),
        "source": "ocr",
        "hits": [m.to_dict() for m in matches[:10]],
    }


def _flatten(node: dict) -> list[dict]:
    out = [node]
    for c in node.get("children", []) or []:
        out.extend(_flatten(c))
    return out
