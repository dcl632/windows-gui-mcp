# windows-gui-mcp

[![CI](https://github.com/dcl632/windows-gui-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dcl632/windows-gui-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/windows-gui-mcp.svg)](https://pypi.org/project/windows-gui-mcp/)
[![Release](https://img.shields.io/github/v/release/dcl632/windows-gui-mcp)](https://github.com/dcl632/windows-gui-mcp/releases)
[![License](https://img.shields.io/github/license/dcl632/windows-gui-mcp)](LICENSE)

Windows GUI Automation MCP server for AI coding agents.

`windows-gui-mcp` helps agents operate Windows desktop applications through
semantic UI Automation instead of brittle coordinate clicks. It is designed for
agent workflows that need to inspect a live Windows UI, act on stable
identifiers, verify every action, and turn successful sessions into reusable
scripts.

Install from PyPI:

```powershell
py -3.12 -m pip install "windows-gui-mcp[windows,ocr]"
```

Demo and project notes:

- [Notepad and Calculator demo](docs/demo.md)
- [Example workflow](examples/notepad_calculator.md)
- [Roadmap](docs/roadmap.md)
- [Competitive positioning](docs/competitive-positioning.md)

## Why this exists

AI agents can work reliably with web pages because browsers expose structured
DOM state. Windows desktop applications are harder: the visible UI is often
stateful, asynchronous, and easy to break with raw coordinates.

This project targets a gap in the agent ecosystem: reliable control of
Windows-only desktop software through MCP, with UI Automation as the default
interface and OCR/image matching treated as explicit fallbacks.

This project exposes a small MCP toolset that keeps the agent in a safer loop:

1. Discover visible windows.
2. Focus the target window.
3. Dump the UI Automation tree.
4. Find controls by stable identifiers.
5. Act with post-action verification.
6. Use OCR or image fallback only after semantic lookup fails.
7. Generate a pywinauto replay script from the trace.

## Tooling model

```text
AI coding agent
      |
      | MCP stdio
      v
windows_gui_mcp.server
      |
      v
tools/dispatch + trace recorder
      |
      +-- window / element / input / verify / wait
      +-- screenshot / OCR / fallback / trace-to-script
      |
      v
Windows backend ladder
      |
      +-- pywinauto UIA      first choice
      +-- pywinauto win32    legacy fallback
      +-- pyautogui          image/coordinate last resort
```

## MCP tools

| Tool | Purpose |
| --- | --- |
| `list_windows` | Enumerate visible top-level windows. |
| `focus_window` | Bring a title-matching window to the foreground and verify focus. |
| `dump_ui_tree` | Dump the UIA tree so the agent can choose stable identifiers. |
| `find_element` | Locate one control by `automation_id`, `name`, `control_type`, or `class_name`. |
| `click_element` | Click a semantically identified control and verify the post-condition. |
| `type_text` | Type into a target control and optionally verify the value. |
| `hotkey` | Send a pywinauto-style key chord such as `^s` or `%{F4}`. |
| `screenshot` | Capture the screen, a window, or a region. |
| `wait_until_element` | Wait for a control to exist, become visible, or become enabled. |
| `verify_text_exists` | Verify text through UIA first, OCR only when requested. |
| `fallback_click_by_image_or_ocr` | Last-resort click by image template or OCR anchor. |
| `generate_stable_script_from_trace` | Convert the current trace into a pywinauto replay script. |

## Install

Python 3.12 or newer is required.

macOS and Linux controller machines may ship an older system Python. If
`python3 --version` is below 3.12, install Python 3.12 or newer before running
`pip install windows-gui-mcp`. Live GUI automation still needs the MCP server to
run on the Windows desktop session that owns the target UI.

For normal Windows agent use:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install "windows-gui-mcp[windows,ocr]"
```

For local development from this repository:

```bash
python -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[dev]"
```

On Windows, install the optional runtime extras when you want live GUI control:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev,windows,ocr]"
```

OCR support is optional. If you use Tesseract OCR, install the Windows package
separately and make sure `tesseract.exe` is on `PATH`.

## Run

Start the MCP server on the Windows machine that owns the desktop session:

```powershell
windows-gui-mcp
```

Check CLI metadata without starting the MCP stdio transport:

```powershell
windows-gui-mcp --help
windows-gui-mcp --version
```

Example local MCP client config:

```json
{
  "mcpServers": {
    "windows-gui": {
      "command": "windows-gui-mcp"
    }
  }
}
```

Example SSH-based config from another machine:

```json
{
  "mcpServers": {
    "windows-gui": {
      "command": "ssh",
      "args": [
        "user@windows-host",
        "C:\\path\\to\\windows-gui-mcp\\.venv\\Scripts\\windows-gui-mcp.exe"
      ]
    }
  }
}
```

## Example workflow

This is the intended agent loop for a Notepad or Calculator task:

```text
1. list_windows()
2. focus_window(title_regex="Notepad|Calculator")
3. dump_ui_tree(window_handle=...)
4. find_element(spec={"name": "Save", "control_type": "Button"})
5. click_element(
     spec={"name": "Save", "control_type": "Button"},
     expect_element_after={"class_name": "#32770"}
   )
6. type_text(
     spec={"automation_id": "1001"},
     text="agent-notes.txt",
     verify_value_contains="agent-notes.txt"
   )
7. hotkey("%{ENTER}")
8. generate_stable_script_from_trace()
```

See [examples/notepad_calculator.md](examples/notepad_calculator.md) for a
longer walkthrough.

For a fuller transcript, expected output, and generated replay script shape, see
[docs/demo.md](docs/demo.md).

## Safety rules

- Prefer `automation_id`, then `name`, then `control_type`, then `class_name`.
- Do not start with screen coordinates.
- Verify every click or text entry with a concrete post-condition.
- Re-dump the UI tree after a failed verification instead of retrying blindly.
- Treat OCR and image matching as fallbacks, not the primary automation path.

## Development checks

```bash
python -m compileall -q src tests
python -m pytest -q
ruff check .
python -m build
twine check dist/*
```

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and automation
design rules. See [SECURITY.md](SECURITY.md) for vulnerability reporting and
desktop automation safety expectations.

## License

MIT
