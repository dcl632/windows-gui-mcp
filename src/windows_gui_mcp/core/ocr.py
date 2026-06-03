"""OCR fallback ladder.

Order (use first available):
    1. Windows.Media.Ocr  (winocr) — fast, ships with OS, accurate on system fonts
    2. Tesseract          (pytesseract) — works everywhere, deps cheap
    3. EasyOCR             — heavier but best for non-Latin / messy fonts

OCR is the *second-to-last* fallback (after UIA/win32). Coordinate clicks
based on OCR bounding boxes are allowed only when verify_text_exists()
confirms the target string is visible.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ..utils.errors import OCRUnavailable

log = logging.getLogger("windows_gui_mcp.ocr")

_easyocr_reader: Any = None


@dataclass
class OCRMatch:
    text: str
    confidence: float
    bbox: tuple[int, int, int, int]  # (left, top, right, bottom) absolute screen coords
    engine: str

    def center(self) -> tuple[int, int]:
        left, top, right, bottom = self.bbox
        return ((left + right) // 2, (top + bottom) // 2)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bbox": list(self.bbox),
            "engine": self.engine,
            "center": list(self.center()),
        }


def _try_winocr(image: Any, languages: list[str]) -> list[OCRMatch] | None:
    try:
        import asyncio

        import winocr  # type: ignore
    except Exception:
        return None
    try:
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                winocr.recognize_pil(image, languages[0] if languages else "en-US")
            )
        finally:
            loop.close()
        out: list[OCRMatch] = []
        for line in getattr(result, "lines", []):
            for word in getattr(line, "words", []):
                rect = word.bounding_rect
                bbox = (int(rect.x), int(rect.y), int(rect.x + rect.width), int(rect.y + rect.height))
                out.append(OCRMatch(text=word.text, confidence=1.0, bbox=bbox, engine="winocr"))
        return out
    except Exception as e:  # noqa: BLE001
        log.debug("winocr failed: %s", e)
        return None


def _try_tesseract(image: Any, languages: list[str]) -> list[OCRMatch] | None:
    try:
        import pytesseract  # type: ignore
    except Exception:
        return None
    try:
        lang = "+".join(languages) if languages else "eng"
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        out: list[OCRMatch] = []
        n = len(data["text"])
        for i in range(n):
            t = (data["text"][i] or "").strip()
            if not t:
                continue
            left, top = int(data["left"][i]), int(data["top"][i])
            w, h = int(data["width"][i]), int(data["height"][i])
            conf_raw = data.get("conf", ["-1"] * n)[i]
            try:
                conf = float(conf_raw) / 100.0
            except Exception:
                conf = 0.0
            out.append(
                OCRMatch(text=t, confidence=conf, bbox=(left, top, left + w, top + h), engine="tesseract")
            )
        return out
    except Exception as e:  # noqa: BLE001
        log.debug("tesseract failed: %s", e)
        return None


def _try_easyocr(image: Any, languages: list[str]) -> list[OCRMatch] | None:
    global _easyocr_reader
    try:
        import easyocr  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return None
    try:
        if _easyocr_reader is None:
            _easyocr_reader = easyocr.Reader(languages or ["en"], gpu=False, verbose=False)
        arr = np.array(image)
        results = _easyocr_reader.readtext(arr)
        out: list[OCRMatch] = []
        for poly, txt, conf in results:
            xs = [int(p[0]) for p in poly]
            ys = [int(p[1]) for p in poly]
            bbox = (min(xs), min(ys), max(xs), max(ys))
            out.append(OCRMatch(text=str(txt), confidence=float(conf), bbox=bbox, engine="easyocr"))
        return out
    except Exception as e:  # noqa: BLE001
        log.debug("easyocr failed: %s", e)
        return None


def ocr(image: Any, languages: list[str] | None = None) -> list[OCRMatch]:
    languages = languages or ["en"]
    for fn in (_try_winocr, _try_tesseract, _try_easyocr):
        out = fn(image, languages)
        if out is not None:
            return out
    raise OCRUnavailable("no OCR engine available — install winocr, tesseract, or easyocr")


def find_text_on_screen(
    text: str,
    image: Any | None = None,
    languages: list[str] | None = None,
    fuzzy: bool = True,
    region: tuple[int, int, int, int] | None = None,
) -> list[OCRMatch]:
    """OCR an image (or capture screen) and return all matches for `text`."""
    if image is None:
        from .screenshot import _capture

        image = _capture(window_handle=None, region=region)
        if region:
            offset_x, offset_y = region[0], region[1]
        else:
            offset_x = offset_y = 0
    else:
        offset_x = offset_y = 0
    matches = ocr(image, languages)
    needle = text.lower().strip()
    out: list[OCRMatch] = []
    for m in matches:
        hay = m.text.lower().strip()
        hit = (needle in hay) if fuzzy else (hay == needle)
        if hit:
            left, top, right, bottom = m.bbox
            out.append(
                OCRMatch(
                    text=m.text,
                    confidence=m.confidence,
                    bbox=(left + offset_x, top + offset_y, right + offset_x, bottom + offset_y),
                    engine=m.engine,
                )
            )
    return out
