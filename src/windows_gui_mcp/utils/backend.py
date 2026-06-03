"""Backend orchestrator: prefer UIA, fallback to win32, then pyautogui.

Holds a process-wide singleton so callers don't re-instantiate
pywinauto.Application objects on every tool call (which is slow and
sometimes deadlocks COM).
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from typing import Any

from .errors import BackendUnavailable

log = logging.getLogger("windows_gui_mcp.backend")

_ON_WINDOWS = sys.platform == "win32"


@dataclass
class BackendState:
    uia_ok: bool = False
    win32_ok: bool = False
    pyautogui_ok: bool = False
    last_focused_handle: int | None = None
    last_focused_title: str | None = None
    notes: list[str] = field(default_factory=list)


class BackendManager:
    """Lazy-init wrapper around pywinauto + pyautogui.

    Order of preference for ANY element interaction:
        1. UIA (best — works for WPF/UWP/WinUI/most Win32)
        2. win32 (fallback for legacy MFC, classic dialogs)
        3. pyautogui (last resort — image / coords only)
    """

    def __init__(self) -> None:
        self.state = BackendState()
        self._desktop_uia: Any = None
        self._desktop_w32: Any = None
        self._pag: Any = None

    def ensure(self) -> BackendState:
        if not _ON_WINDOWS:
            self.state.notes.append("non-Windows host — only screenshot/OCR ops are real")
            return self.state
        try:
            from pywinauto import Desktop  # type: ignore

            self._desktop_uia = Desktop(backend="uia")
            self.state.uia_ok = True
        except Exception as e:  # noqa: BLE001
            self.state.notes.append(f"UIA init failed: {e}")
        try:
            from pywinauto import Desktop  # type: ignore

            self._desktop_w32 = Desktop(backend="win32")
            self.state.win32_ok = True
        except Exception as e:  # noqa: BLE001
            self.state.notes.append(f"win32 init failed: {e}")
        try:
            import pyautogui  # type: ignore

            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.05
            self._pag = pyautogui
            self.state.pyautogui_ok = True
        except Exception as e:  # noqa: BLE001
            self.state.notes.append(f"pyautogui init failed: {e}")
        return self.state

    def desktop(self, prefer: str = "uia") -> Any:
        self.ensure()
        if prefer == "uia" and self.state.uia_ok:
            return self._desktop_uia
        if prefer == "win32" and self.state.win32_ok:
            return self._desktop_w32
        if self.state.uia_ok:
            return self._desktop_uia
        if self.state.win32_ok:
            return self._desktop_w32
        raise BackendUnavailable("no pywinauto Desktop backend available")

    @property
    def pyautogui(self) -> Any:
        self.ensure()
        if not self.state.pyautogui_ok:
            raise BackendUnavailable("pyautogui unavailable")
        return self._pag


_manager: BackendManager | None = None


def get_backend() -> BackendManager:
    global _manager
    if _manager is None:
        _manager = BackendManager()
        _manager.ensure()
    return _manager
