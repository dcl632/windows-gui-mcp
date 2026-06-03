---
name: windows-gui
description: Drive Windows desktop apps stably via the windows-gui MCP. Use this skill when the task requires interacting with a Windows desktop application through UI Automation, native dialogs, or other non-web GUI surfaces. The skill enforces UIA-first, verify-after-every-action, and OCR-only-as-last-resort behavior.
---

# windows-gui operator playbook

You are driving a Windows desktop through the `windows-gui` MCP.
Every action must follow the identifier-priority ladder:

```text
automation_id > name > control_type > class_name
  > image template > OCR text > raw coordinates
```

Raw coordinates are forbidden by default. Use them only through the fallback
tool after semantic lookup has failed and explain why the fallback is needed.

## Mandatory loop

For every UI step, use this sequence:

```text
1. list_windows()
2. focus_window(title_regex=...)
3. dump_ui_tree(window_handle=..., max_depth=6)
4. find_element(spec={...})
5. click_element / type_text / hotkey
6. Check verify.ok
7. If verify.ok is false, re-dump and replan before retrying
```

## Hard rules

- Never pass coordinates to `click_element`.
- Never use `fallback_click_by_image_or_ocr` before trying `find_element`.
- Always name a post-condition for clicks that open, close, or change UI state.
- Always check `verify.ok` in the tool response.
- Hotkeys use pywinauto syntax: `^s`, `%{F4}`, `+{TAB}`, `^+s`, `{ENTER}`, `{ESC}`.

## Recovery ladder

```text
verify.ok == false
  |
  +-- 1. dump_ui_tree again
  +-- 2. wait_until_element(spec=..., state="visible", timeout=10)
  +-- 3. screenshot()
  +-- 4. verify_text_exists(text=..., source="ui_tree")
  +-- 5. verify_text_exists(text=..., source="ocr")
  +-- 6. fallback_click_by_image_or_ocr
```

## Reusable scripts

After a multi-step task succeeds, call `generate_stable_script_from_trace()`.
It emits a pywinauto script that replays the trace without MCP. Steps that used
OCR or coordinate fallback are emitted as TODO markers; replace those markers
with stable UI identifiers before reusing the script.

## Common Windows app hints

- Notepad: title regex `Notepad|Untitled`; Save As dialogs often expose the
  filename field as `automation_id="1001"` in classic common dialogs.
- Calculator: most buttons expose stable `name` values such as `One`, `Plus`,
  `Equals`, and `Clear`.
- Microsoft Office: ribbon items often expose automation IDs; use a deeper
  `dump_ui_tree(max_depth=10)` before choosing targets.
- Browser native dialogs: common dialogs often use `class_name="#32770"`.
- UWP / WinUI apps: prefer UIA and verify state changes carefully.

## What to skip

- Web pages: use a browser automation tool instead.
- Tasks that can be done through SSH or CLI: prefer the direct command line.
- Native macOS apps: this skill targets Windows desktops only.

## Sanity checklist before reporting done

- Every state-changing action has `verify.ok = true`.
- No fallback click was used without a written reason.
- Reusable tasks generated a stable script from the trace.
- Visible end states were checked with a final screenshot when useful.
