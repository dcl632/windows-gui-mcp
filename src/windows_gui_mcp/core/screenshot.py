"""Screenshot — full screen, single window, or element bounding box."""

from __future__ import annotations

import base64
import io
import logging
import time
from pathlib import Path
from typing import Any

log = logging.getLogger("windows_gui_mcp.screenshot")

_DEFAULT_DIR = Path.home() / ".windows_gui_mcp" / "shots"


def _ensure_dir() -> Path:
    _DEFAULT_DIR.mkdir(parents=True, exist_ok=True)
    return _DEFAULT_DIR


def screenshot(
    window_handle: int | None = None,
    region: tuple[int, int, int, int] | None = None,
    save_path: str | None = None,
    return_base64: bool = False,
) -> dict:
    """Capture full screen, a window, or an absolute screen region.

    Returns {path, base64?, size, ts}.
    """
    img = _capture(window_handle=window_handle, region=region)
    out_path = Path(save_path) if save_path else _ensure_dir() / f"shot_{int(time.time() * 1000)}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
    payload: dict = {"path": str(out_path), "size": list(img.size), "ts": time.time()}
    if return_base64:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        payload["base64"] = base64.b64encode(buf.getvalue()).decode("ascii")
    return payload


def _capture(window_handle: int | None, region: tuple[int, int, int, int] | None) -> Any:
    """Try multiple strategies — works on Windows + headless dev hosts."""
    if window_handle:
        try:
            from ..utils.backend import get_backend

            bm = get_backend()
            desktop = bm.desktop()
            win = desktop.window(handle=window_handle)
            return win.capture_as_image()
        except Exception as e:  # noqa: BLE001
            log.debug("window capture failed, falling back to region: %s", e)
            try:
                rect = win.rectangle()
                region = (rect.left, rect.top, rect.right, rect.bottom)
            except Exception:
                region = None
    try:
        import pyautogui  # type: ignore

        if region:
            left, top, right, bottom = region
            return pyautogui.screenshot(region=(left, top, right - left, bottom - top))
        return pyautogui.screenshot()
    except Exception as e:  # noqa: BLE001
        log.debug("pyautogui screenshot failed: %s", e)
    try:
        from PIL import ImageGrab  # type: ignore

        return ImageGrab.grab(bbox=region)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"all screenshot backends failed: {e}") from e
