"""Pydantic input schemas — MCP tool argument validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ElementSpecModel(BaseModel):
    automation_id: str | None = None
    name: str | None = None
    control_type: str | None = None
    class_name: str | None = None
    nth: int = 0


class ListWindowsArgs(BaseModel):
    visible_only: bool = True


class FocusWindowArgs(BaseModel):
    title_regex: str = Field(..., description="Python regex against window title")
    prefer: Literal["uia", "win32"] = "uia"


class DumpUITreeArgs(BaseModel):
    window_handle: int | None = None
    max_depth: int = 6
    prefer: Literal["uia", "win32"] = "uia"


class FindElementArgs(BaseModel):
    spec: ElementSpecModel
    window_handle: int | None = None
    timeout: float = 6.0
    prefer: Literal["uia", "win32"] = "uia"


class ClickElementArgs(BaseModel):
    spec: ElementSpecModel
    button: Literal["left", "right", "middle"] = "left"
    double: bool = False
    window_handle: int | None = None
    timeout: float = 8.0
    expect_element_after: ElementSpecModel | None = None
    expect_element_disappear: ElementSpecModel | None = None


class TypeTextArgs(BaseModel):
    text: str
    spec: ElementSpecModel | None = None
    window_handle: int | None = None
    clear_first: bool = False
    with_spaces: bool = True
    verify_value_contains: str | None = None
    timeout: float = 8.0


class HotkeyArgs(BaseModel):
    keys: str = Field(..., description="pywinauto-style chord, e.g. '^s', '%{F4}'")
    window_handle: int | None = None


class ScreenshotArgs(BaseModel):
    window_handle: int | None = None
    region: tuple[int, int, int, int] | None = None
    save_path: str | None = None
    return_base64: bool = False


class WaitUntilElementArgs(BaseModel):
    spec: ElementSpecModel
    timeout: float = 10.0
    state: Literal["visible", "enabled", "exists"] = "visible"
    window_handle: int | None = None


class VerifyTextExistsArgs(BaseModel):
    text: str
    source: Literal["ui_tree", "ocr"] = "ui_tree"
    window_handle: int | None = None
    region: tuple[int, int, int, int] | None = None
    languages: list[str] | None = None


class FallbackClickArgs(BaseModel):
    image_path: str | None = None
    text: str | None = None
    confidence: float = 0.85
    languages: list[str] | None = None
    region: tuple[int, int, int, int] | None = None
    double: bool = False
    button: Literal["left", "right", "middle"] = "left"


class GenScriptArgs(BaseModel):
    out_path: str | None = None
