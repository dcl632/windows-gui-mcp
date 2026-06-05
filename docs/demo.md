# Demo: Notepad and Calculator

This page shows representative MCP tool transcripts for common Windows desktop
tasks. Exact window handles, automation IDs, control names, and dialog layouts
can vary across Windows versions, so the agent should always dump the live UI
tree before acting.

The intended loop is:

```text
discover -> focus -> dump -> find -> act -> verify -> trace-to-script
```

## Notepad: write text and open Save As

Expected result:

- Notepad receives text typed by the agent.
- The Save As dialog is opened through a verified hotkey/action path.
- The filename field contains `agent-notes.txt`.
- The session trace can be converted into a replayable pywinauto script.

Representative transcript:

```jsonc
{ "tool": "list_windows", "args": { "visible_only": true } }
// -> { "windows": [{ "title": "Untitled - Notepad", "handle": 132476 }] }

{ "tool": "focus_window", "args": { "title_regex": "Notepad|Untitled" } }
// -> { "ok": true, "verified": true, "handle": 132476 }

{ "tool": "dump_ui_tree", "args": { "window_handle": 132476, "max_depth": 6 } }
// -> { "ok": true, "tree": [{ "name": "Text editor", "control_type": "Edit" }] }

{
  "tool": "type_text",
  "args": {
    "spec": { "control_type": "Edit" },
    "text": "Notes written by an AI coding agent.",
    "verify_value_contains": "Notes written"
  }
}
// -> { "ok": true, "verify": { "ok": true, "method": "value_contains" } }

{ "tool": "hotkey", "args": { "keys": "^s" } }
// -> { "ok": true }

{
  "tool": "wait_until_element",
  "args": {
    "spec": { "class_name": "#32770" },
    "state": "visible",
    "timeout": 10
  }
}
// -> { "ok": true, "matched": { "name": "Save As", "class_name": "#32770" } }

{
  "tool": "type_text",
  "args": {
    "spec": { "automation_id": "1001" },
    "text": "agent-notes.txt",
    "clear_first": true,
    "verify_value_contains": "agent-notes.txt"
  }
}
// -> { "ok": true, "verify": { "ok": true, "method": "value_contains" } }

{ "tool": "generate_stable_script_from_trace", "args": {} }
// -> { "ok": true, "path": "~/.windows_gui_mcp/traces/replay_1714123200.py" }
```

Generated replay script shape:

```python
from pywinauto import Application
from pywinauto.keyboard import send_keys

app = Application(backend="uia").connect(title_re="Notepad|Untitled")
window = app.window(title_re="Notepad|Untitled")
window.set_focus()

window.child_window(control_type="Edit").type_keys(
    "Notes written by an AI coding agent.",
    with_spaces=True,
)
send_keys("^s")

dialog = app.window(class_name="#32770")
dialog.wait("visible", timeout=10)
dialog.child_window(auto_id="1001").set_edit_text("agent-notes.txt")
```

## Calculator: verify semantic button clicks

Expected result:

- Calculator receives semantic button clicks instead of coordinate clicks.
- The display is verified through UI Automation text after `1 + 2 =`.
- If verification fails, the agent re-dumps the UI tree before retrying.

Representative transcript:

```jsonc
{ "tool": "focus_window", "args": { "title_regex": "Calculator" } }
// -> { "ok": true, "verified": true }

{ "tool": "dump_ui_tree", "args": { "max_depth": 8 } }
// -> { "ok": true, "tree": [{ "name": "One", "control_type": "Button" }] }

{
  "tool": "click_element",
  "args": {
    "spec": { "name": "One", "control_type": "Button" },
    "expect_state_change": true
  }
}
// -> { "ok": true, "verify": { "ok": true } }

{
  "tool": "click_element",
  "args": {
    "spec": { "name": "Plus", "control_type": "Button" },
    "expect_state_change": true
  }
}
// -> { "ok": true, "verify": { "ok": true } }

{
  "tool": "click_element",
  "args": {
    "spec": { "name": "Two", "control_type": "Button" },
    "expect_state_change": true
  }
}
// -> { "ok": true, "verify": { "ok": true } }

{
  "tool": "click_element",
  "args": {
    "spec": { "name": "Equals", "control_type": "Button" },
    "expect_state_change": true
  }
}
// -> { "ok": true, "verify": { "ok": true } }

{
  "tool": "verify_text_exists",
  "args": {
    "text": "3",
    "source": "ui_tree"
  }
}
// -> { "ok": true, "source": "ui_tree" }
```

## Failure recovery

The recovery path is intentionally conservative:

```jsonc
{ "tool": "dump_ui_tree", "args": { "max_depth": 8 } }
{ "tool": "wait_until_element", "args": { "spec": { "name": "Save As" }, "timeout": 10 } }
{ "tool": "verify_text_exists", "args": { "text": "Save As", "source": "ui_tree" } }
{ "tool": "screenshot", "args": { "return_base64": false } }
```

Only after UI Automation lookup and verification fail should an agent use OCR or
image matching through `fallback_click_by_image_or_ocr`.
