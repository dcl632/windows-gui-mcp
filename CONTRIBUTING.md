# Contributing

Thanks for helping improve `windows-gui-mcp`.

This project is a Windows GUI automation MCP server for AI coding agents. The
highest-value contributions improve reliable UI Automation lookup, action
verification, safe fallback behavior, trace quality, and replayable scripts.

## Development setup

Use Python 3.12 or newer.

```bash
python -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[dev]"
```

On Windows, install runtime extras when testing live desktop automation:

```powershell
.\.venv\Scripts\python -m pip install -e ".[dev,windows,ocr]"
```

## Checks

Run the same checks as CI before opening a pull request:

```bash
python -m compileall -q src tests
python -m pytest -q
ruff check .
python -m build
twine check dist/*
windows-gui-mcp --help
windows-gui-mcp --version
```

## Automation design rules

- Prefer UI Automation identifiers over coordinates.
- Verify every click, text entry, hotkey, wait, or fallback action with a clear
  post-condition.
- Treat OCR and image matching as last-resort fallbacks.
- Re-dump the UI tree after failed verification instead of retrying blindly.
- Keep examples generic, preferably Notepad, Calculator, or native Windows
  dialogs.
- Do not commit private hostnames, IP addresses, account names, emails, trace
  paths, screenshots, or customer/application data.

## Pull requests

Good pull requests usually include:

- A short description of the automation behavior being changed.
- Focused tests for trace generation, verification logic, wait behavior, or CLI
  behavior when applicable.
- Notes about live Windows testing if the change touches pywinauto, pyautogui,
  OCR, screenshots, or focus handling.

Keep changes narrow. Avoid unrelated formatting churn, dependency changes, or
large rewrites unless they are needed for the behavior being fixed.
