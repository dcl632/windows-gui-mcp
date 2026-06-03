"""Windows GUI Automation MCP server.

Run on the target Windows machine:
    windows-gui-mcp           # stdio MCP transport
    python -m windows_gui_mcp.server

Register with an MCP client:
    {
      "mcpServers": {
        "windows-gui": { "command": "windows-gui-mcp" }
      }
    }
"""

from __future__ import annotations

import logging
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import dispatch
from .tools.schemas import (
    ClickElementArgs,
    DumpUITreeArgs,
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("windows_gui_mcp.server")

server = Server("windows-gui-mcp")

_HELP = """windows-gui-mcp

Windows GUI Automation MCP server for AI coding agents.

Usage:
  windows-gui-mcp             Start the MCP stdio server
  windows-gui-mcp --help      Show this help message
  windows-gui-mcp --version   Show the installed package version
"""

# Map tool name -> (schema model, dispatch fn, description)
TOOL_REGISTRY: dict[str, tuple[type, Any, str]] = {
    "list_windows": (
        ListWindowsArgs,
        dispatch.list_windows,
        "Enumerate top-level windows. Use this FIRST to discover handles + titles.",
    ),
    "focus_window": (
        FocusWindowArgs,
        dispatch.focus_window,
        "Bring a window matching `title_regex` to foreground. Verifies via GetForegroundWindow.",
    ),
    "dump_ui_tree": (
        DumpUITreeArgs,
        dispatch.dump_ui_tree,
        "Dump UIA tree of focused window. Read this BEFORE clicking — find stable automation_id / name.",
    ),
    "find_element": (
        FindElementArgs,
        dispatch.find_element,
        "Locate a single element by automation_id (preferred) / name / control_type. Polls until timeout.",
    ),
    "click_element": (
        ClickElementArgs,
        dispatch.click_element,
        "Click an element identified semantically. NEVER pass coordinates. Verifies state change after.",
    ),
    "type_text": (
        TypeTextArgs,
        dispatch.type_text,
        "Type text into target element (or focused control). Verifies element value contains expected text.",
    ),
    "hotkey": (
        HotkeyArgs,
        dispatch.hotkey,
        "Send a keyboard chord. Use pywinauto syntax: '^s' = Ctrl+S, '%{F4}' = Alt+F4, '+{TAB}' = Shift+Tab.",
    ),
    "screenshot": (
        ScreenshotArgs,
        dispatch.screenshot,
        "Capture full screen, a window (handle), or a region. Saves PNG; optionally returns base64.",
    ),
    "wait_until_element": (
        WaitUntilElementArgs,
        dispatch.wait_until_element,
        "Block until element reaches state ∈ {visible,enabled,exists}. Use after async UI transitions.",
    ),
    "verify_text_exists": (
        VerifyTextExistsArgs,
        dispatch.verify_text_exists,
        "Confirm text appears. source='ui_tree' walks UIA (cheap). source='ocr' captures + OCRs (last resort).",
    ),
    "fallback_click_by_image_or_ocr": (
        FallbackClickArgs,
        dispatch.fallback_click_by_image_or_ocr,
        "LAST RESORT click by image template or OCR text anchor. Only after UIA + win32 lookups failed.",
    ),
    "generate_stable_script_from_trace": (
        GenScriptArgs,
        dispatch.generate_stable_script_from_trace,
        "Emit a Python pywinauto script replaying this session — uses ONLY semantic identifiers.",
    ),
}


@server.list_tools()
async def _list_tools() -> list[Tool]:
    out: list[Tool] = []
    for name, (schema_cls, _, desc) in TOOL_REGISTRY.items():
        out.append(
            Tool(
                name=name,
                description=desc,
                inputSchema=schema_cls.model_json_schema(),
            )
        )
    return out


@server.call_tool()
async def _call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name not in TOOL_REGISTRY:
        return [TextContent(type="text", text=f"unknown tool: {name}")]
    schema_cls, fn, _ = TOOL_REGISTRY[name]
    try:
        args = schema_cls(**(arguments or {}))
    except Exception as e:  # noqa: BLE001
        return [TextContent(type="text", text=f"argument validation error: {e}")]
    result = fn(args)
    import json

    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]


async def _amain() -> None:
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def _package_version() -> str:
    try:
        return version("windows-gui-mcp")
    except PackageNotFoundError:
        from . import __version__

        return __version__


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if args in (["--help"], ["-h"]):
        print(_HELP.strip())
        return
    if args == ["--version"]:
        print(_package_version())
        return
    if args:
        raise SystemExit(f"unknown argument(s): {' '.join(args)}")

    import anyio

    anyio.run(_amain)


if __name__ == "__main__":
    main()
