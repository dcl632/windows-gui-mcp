"""Image-template + OCR-anchored click — used only after UIA & win32 fail."""

from __future__ import annotations

import logging
from pathlib import Path

from ..utils.backend import get_backend
from ..utils.errors import ElementNotFound, OCRUnavailable
from .ocr import find_text_on_screen
from .screenshot import _capture

log = logging.getLogger("windows_gui_mcp.fallback")


def fallback_click_by_image_or_ocr(
    image_path: str | None = None,
    text: str | None = None,
    confidence: float = 0.85,
    languages: list[str] | None = None,
    region: tuple[int, int, int, int] | None = None,
    double: bool = False,
    button: str = "left",
) -> dict:
    """Last-resort click. Tries image template first, then OCR.

    Returns {strategy, point, confidence}. Raises ElementNotFound on miss.
    """
    get_backend()  # ensure backend warmed up before pyautogui calls
    if image_path:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(image_path)
        try:
            import pyautogui  # type: ignore

            box = pyautogui.locateOnScreen(str(path), confidence=confidence, region=region)
            if box is not None:
                cx, cy = pyautogui.center(box)
                _click_xy(int(cx), int(cy), button=button, double=double)
                return {
                    "strategy": "image_template",
                    "point": [int(cx), int(cy)],
                    "confidence": confidence,
                    "image_path": str(path),
                }
        except Exception as e:  # noqa: BLE001
            log.debug("image template lookup failed: %s", e)
    if text:
        try:
            img = _capture(window_handle=None, region=region)
            matches = find_text_on_screen(text, image=img, languages=languages, fuzzy=True, region=region)
        except OCRUnavailable as e:
            raise ElementNotFound(f"OCR unavailable: {e}") from e
        if not matches:
            raise ElementNotFound(f"OCR could not locate {text!r} on screen")
        best = max(matches, key=lambda m: m.confidence)
        cx, cy = best.center()
        _click_xy(cx, cy, button=button, double=double)
        return {
            "strategy": "ocr",
            "point": [cx, cy],
            "confidence": best.confidence,
            "engine": best.engine,
            "matched_text": best.text,
        }
    raise ElementNotFound("provide image_path or text for fallback click")


def _click_xy(x: int, y: int, button: str = "left", double: bool = False) -> None:
    bm = get_backend()
    pag = bm.pyautogui
    pag.moveTo(x, y, duration=0.05)
    if double:
        pag.doubleClick(x=x, y=y, button=button)
    else:
        pag.click(x=x, y=y, button=button)
