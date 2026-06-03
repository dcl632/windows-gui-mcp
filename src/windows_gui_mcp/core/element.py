"""Element finder + UI tree dump.

Identifier priority (mandatory, per project rules):
    automation_id  >  name  >  control_type  >  index_in_parent  >  coords (last resort)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..utils.errors import ElementNotFound
from ..utils.retry import wait_for
from .window import get_focused_window

log = logging.getLogger("windows_gui_mcp.element")


@dataclass
class ElementSpec:
    """Stable element identifier — never raw coords."""

    automation_id: str | None = None
    name: str | None = None
    control_type: str | None = None
    class_name: str | None = None
    nth: int = 0  # if multiple matches, pick this index

    def to_pywin_kwargs(self) -> dict:
        kw: dict = {}
        if self.automation_id:
            kw["auto_id"] = self.automation_id
        if self.name:
            kw["title"] = self.name
        if self.control_type:
            kw["control_type"] = self.control_type
        if self.class_name:
            kw["class_name"] = self.class_name
        return kw

    def is_specified(self) -> bool:
        return any([self.automation_id, self.name, self.control_type, self.class_name])


@dataclass
class ElementSnapshot:
    automation_id: str | None
    name: str
    control_type: str | None
    class_name: str | None
    rect: tuple[int, int, int, int] | None
    enabled: bool
    visible: bool
    value: str | None = None
    children: list["ElementSnapshot"] = field(default_factory=list)

    def to_dict(self, include_children: bool = True) -> dict:
        d = {
            "automation_id": self.automation_id,
            "name": self.name,
            "control_type": self.control_type,
            "class_name": self.class_name,
            "rect": list(self.rect) if self.rect else None,
            "enabled": self.enabled,
            "visible": self.visible,
            "value": self.value,
        }
        if include_children:
            d["children"] = [c.to_dict(True) for c in self.children]
        return d


def _snapshot(elem: Any, depth: int = 0, max_depth: int = 8) -> ElementSnapshot:
    try:
        rect = elem.rectangle()
        rect_t = (rect.left, rect.top, rect.right, rect.bottom)
    except Exception:
        rect_t = None
    try:
        auto_id = getattr(elem.element_info, "automation_id", None) or None
    except Exception:
        auto_id = None
    try:
        ctype = getattr(elem.element_info, "control_type", None) or None
    except Exception:
        ctype = None
    try:
        cls = elem.class_name() if hasattr(elem, "class_name") else None
    except Exception:
        cls = None
    try:
        name = elem.window_text() or ""
    except Exception:
        name = ""
    try:
        enabled = bool(elem.is_enabled())
    except Exception:
        enabled = True
    try:
        visible = bool(elem.is_visible())
    except Exception:
        visible = True
    value: str | None = None
    try:
        if hasattr(elem, "get_value"):
            value = elem.get_value()
        elif hasattr(elem, "iface_value"):
            value = elem.iface_value.CurrentValue
    except Exception:
        pass
    snap = ElementSnapshot(
        automation_id=auto_id,
        name=name,
        control_type=ctype,
        class_name=cls,
        rect=rect_t,
        enabled=enabled,
        visible=visible,
        value=value,
    )
    if depth < max_depth:
        try:
            for child in elem.children():
                snap.children.append(_snapshot(child, depth + 1, max_depth))
        except Exception:
            pass
    return snap


def dump_ui_tree(window_handle: int | None = None, max_depth: int = 6, prefer: str = "uia") -> dict:
    """Dump the focused window's UI tree (or one identified by handle)."""
    from ..utils.backend import get_backend

    bm = get_backend()
    desktop = bm.desktop(prefer=prefer)
    if window_handle is None:
        win = get_focused_window(prefer=prefer)
    else:
        win = desktop.window(handle=window_handle)
    snap = _snapshot(win, depth=0, max_depth=max_depth)
    return {
        "backend": prefer,
        "handle": int(getattr(win, "handle", 0) or 0),
        "tree": snap.to_dict(include_children=True),
    }


def _candidates(window: Any, spec: ElementSpec) -> list[Any]:
    """Yield matches in identifier-priority order."""
    if not spec.is_specified():
        return []
    kw = spec.to_pywin_kwargs()
    matches: list[Any] = []
    try:
        matches = window.descendants(**kw)
    except Exception as e:  # noqa: BLE001
        log.debug("descendants(%s) failed: %s", kw, e)
    return matches


def find_element(
    spec: ElementSpec,
    window_handle: int | None = None,
    timeout: float = 6.0,
    prefer: str = "uia",
) -> Any:
    """Locate one element. Polls — returns when found or raises."""
    from ..utils.backend import get_backend

    if not spec.is_specified():
        raise ElementNotFound("ElementSpec must include at least one identifier")
    bm = get_backend()
    desktop = bm.desktop(prefer=prefer)
    if window_handle is None:
        window = get_focused_window(prefer=prefer)
    else:
        window = desktop.window(handle=window_handle)

    def _try() -> Any:
        cands = _candidates(window, spec)
        if len(cands) > spec.nth:
            return cands[spec.nth]
        return None

    elem = wait_for(_try, timeout=timeout, interval=0.25)
    if elem is None:
        raise ElementNotFound(f"no element matched {spec} within {timeout}s")
    return elem


def describe_element(elem: Any) -> dict:
    return _snapshot(elem, depth=0, max_depth=0).to_dict(include_children=False)


def is_same_state(a: dict, b: dict) -> bool:
    keys = ("automation_id", "name", "value", "rect", "enabled", "visible")
    return all(a.get(k) == b.get(k) for k in keys)
