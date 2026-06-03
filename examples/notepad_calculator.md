# Example: Notepad and Calculator workflow

This walkthrough shows the mandatory loop:

```text
discover -> focus -> dump -> find -> act -> verify
```

## Notepad Save As

```jsonc
// 1. Discover visible windows.
{ "tool": "list_windows", "args": { "visible_only": true } }
// -> { windows: [..., { title: "Untitled - Notepad", handle: 132476, ... }] }

// 2. Focus Notepad.
{ "tool": "focus_window", "args": { "title_regex": "Notepad|Untitled" } }
// -> { title: "Untitled - Notepad", handle: 132476, verified: true }

// 3. Dump the UIA tree before acting.
{ "tool": "dump_ui_tree", "args": { "window_handle": 132476, "max_depth": 6 } }

// 4. Type text into the focused editor.
{ "tool": "type_text", "args": {
    "text": "Notes written by an AI coding agent.",
    "verify_value_contains": null
  } }

// 5. Open Save As.
{ "tool": "hotkey", "args": { "keys": "^s" } }

// 6. Wait for a common Save As dialog.
{ "tool": "wait_until_element", "args": {
    "spec": { "class_name": "#32770" },
    "timeout": 10
  } }

// 7. Fill the filename field and verify the value.
{ "tool": "type_text", "args": {
    "text": "agent-notes.txt",
    "spec": { "automation_id": "1001" },
    "clear_first": true,
    "verify_value_contains": "agent-notes.txt"
  } }

// 8. Confirm the dialog.
{ "tool": "hotkey", "args": { "keys": "%{ENTER}" } }

// 9. Generate a replay script.
{ "tool": "generate_stable_script_from_trace", "args": {} }
// -> ~/.windows_gui_mcp/traces/replay_1714123200.py
```

## Calculator button click

```jsonc
// 1. Focus Calculator.
{ "tool": "focus_window", "args": { "title_regex": "Calculator" } }

// 2. Dump controls and find stable names.
{ "tool": "dump_ui_tree", "args": { "max_depth": 8 } }

// 3. Click semantic buttons and verify the display text.
{ "tool": "click_element", "args": {
    "spec": { "name": "One", "control_type": "Button" },
    "expect_state_change": true
  } }
{ "tool": "click_element", "args": {
    "spec": { "name": "Plus", "control_type": "Button" },
    "expect_state_change": true
  } }
{ "tool": "click_element", "args": {
    "spec": { "name": "Two", "control_type": "Button" },
    "expect_state_change": true
  } }
{ "tool": "click_element", "args": {
    "spec": { "name": "Equals", "control_type": "Button" },
    "expect_state_change": true
  } }
{ "tool": "verify_text_exists", "args": {
    "text": "3",
    "source": "ui_tree"
  } }
```

## Recovery pattern

If verification fails, re-dump the tree before retrying:

```jsonc
{ "tool": "dump_ui_tree", "args": { "window_handle": 132476, "max_depth": 8 } }
{ "tool": "verify_text_exists", "args": { "text": "Save As", "source": "ui_tree" } }
{ "tool": "screenshot", "args": { "return_base64": false } }
```
