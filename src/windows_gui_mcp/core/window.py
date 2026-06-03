"""Window enumeration + focus."""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass
from typing import Any

from ..utils.backend import get_backend
from ..utils.errors import WindowNotFound
from ..utils.retry import wait_for, with_retries

log = logging.getLogger("windows_gui_mcp.window")


@dataclass
class WindowInfo:
    title: str
    handle: int
    pid: int | None
    class_name: str | None
    rect: tuple[int, int, int, int] | None
    visible: bool
    backend: str


def list_windows(visible_only: bool = True) -> list[dict]:
    bm = get_backend()
    out: list[WindowInfo] = []
    seen: set[int] = set()
    for backend_name in ("uia", "win32"):
        if (backend_name == "uia" and not bm.state.uia_ok) or (
            backend_name == "win32" and not bm.state.win32_ok
        ):
            continue
        try:
            desktop = bm.desktop(prefer=backend_name)
            for w in desktop.windows():
                try:
                    handle = int(w.handle)
                except Exception:
                    continue
                if handle in seen:
                    continue
                seen.add(handle)
                try:
                    title = w.window_text() or ""
                    visible = bool(w.is_visible())
                    if visible_only and not visible:
                        continue
                    rect_obj = w.rectangle()
                    rect = (rect_obj.left, rect_obj.top, rect_obj.right, rect_obj.bottom)
                    pid = getattr(w, "process_id", lambda: None)()
                    cls = getattr(w, "class_name", lambda: None)()
                    out.append(
                        WindowInfo(
                            title=title,
                            handle=handle,
                            pid=pid,
                            class_name=cls,
                            rect=rect,
                            visible=visible,
                            backend=backend_name,
                        )
                    )
                except Exception as e:  # noqa: BLE001
                    log.debug("skip window %s: %s", handle, e)
        except Exception as e:  # noqa: BLE001
            log.warning("backend %s enumerate failed: %s", backend_name, e)
    out.sort(key=lambda w: (not w.visible, w.title.lower()))
    return [asdict(w) for w in out]


def _match_window(title_regex: str, prefer: str) -> Any:
    bm = get_backend()
    desktop = bm.desktop(prefer=prefer)
    pat = re.compile(title_regex, re.IGNORECASE)

    def _try() -> Any:
        for w in desktop.windows():
            try:
                if w.is_visible() and pat.search(w.window_text() or ""):
                    return w
            except Exception:
                continue
        return None

    win = wait_for(_try, timeout=4.0, interval=0.3)
    if not win:
        raise WindowNotFound(f"no visible window matches {title_regex!r} on {prefer}")
    return win


def focus_window(title_regex: str, prefer: str = "uia") -> dict:
    """Bring a matching window to foreground. Returns the focused window's metadata."""
    bm = get_backend()
    win = _match_window(title_regex, prefer)
    with_retries(lambda: win.set_focus())
    handle = int(win.handle)
    title = win.window_text() or ""
    bm.state.last_focused_handle = handle
    bm.state.last_focused_title = title
    rect = win.rectangle()
    return {
        "title": title,
        "handle": handle,
        "rect": [rect.left, rect.top, rect.right, rect.bottom],
        "backend": prefer,
        "verified": _verify_foreground(handle),
    }


def _verify_foreground(handle: int) -> bool:
    """Confirm the OS reports our window as foreground."""
    try:
        import ctypes  # type: ignore

        fg = ctypes.windll.user32.GetForegroundWindow()
        return int(fg) == handle
    except Exception:
        return True


def get_focused_window(prefer: str = "uia") -> Any:
    """Return cached focused window, falling back to OS query."""
    bm = get_backend()
    desktop = bm.desktop(prefer=prefer)
    if bm.state.last_focused_handle:
        try:
            return desktop.window(handle=bm.state.last_focused_handle)
        except Exception:
            pass
    try:
        import ctypes  # type: ignore

        fg = ctypes.windll.user32.GetForegroundWindow()
        return desktop.window(handle=int(fg))
    except Exception as e:  # noqa: BLE001
        raise WindowNotFound("no focused window") from e
