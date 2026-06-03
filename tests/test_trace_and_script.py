"""Tests that run on any host (no pywinauto / no Windows needed).

We exercise:
  - trace recorder (record / snapshot / save)
  - stable-script emitter (semantic specs preserved, coord/OCR steps marked TODO)
  - input._escape_for_typekeys / _translate_chord
  - schemas validation
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from windows_gui_mcp.core import trace
from windows_gui_mcp.core.input import _escape_for_typekeys, _translate_chord
from windows_gui_mcp.tools.schemas import (
    ClickElementArgs,
    ElementSpecModel,
    HotkeyArgs,
    TypeTextArgs,
)


@pytest.fixture(autouse=True)
def _reset_trace():
    trace.reset()
    yield
    trace.reset()


def test_trace_records_and_persists(tmp_path: Path):
    trace.record("focus_window", {"title_regex": "Notepad|Untitled"}, {"verified": True}, ok=True)
    trace.record(
        "click_element",
        {"spec": {"name": "Save", "control_type": "Button"}},
        {"verify": {"ok": True}},
        ok=True,
    )
    snap = trace.snapshot()
    assert len(snap["entries"]) == 2
    assert snap["entries"][0]["tool"] == "focus_window"
    p = trace.save(str(tmp_path / "t.json"))
    data = json.loads(Path(p).read_text())
    assert len(data["entries"]) == 2


def test_generate_stable_script_uses_semantic_specs(tmp_path: Path):
    trace.record("focus_window", {"title_regex": "Notepad|Untitled"}, {}, ok=True)
    trace.record(
        "click_element",
        {"spec": {"name": "Save", "control_type": "Button"}},
        {"verify": {"ok": True}},
        ok=True,
    )
    trace.record(
        "type_text",
        {
            "spec": {"automation_id": "FileNameInput"},
            "text": "agent-notes.txt",
        },
        {"verify": {"ok": True}},
        ok=True,
    )
    trace.record("hotkey", {"keys": "%{ENTER}"}, {"verify": {"ok": True}}, ok=True)
    out = tmp_path / "replay.py"
    info = trace.generate_stable_script_from_trace(out_path=str(out))
    body = out.read_text()
    assert "title_re='Notepad|Untitled'" in body
    assert "title='Save'" in body and "control_type='Button'" in body
    assert "auto_id='FileNameInput'" in body
    assert "type_keys('%{ENTER}'" in body
    assert info["todo_markers"] == 0


def test_script_marks_coord_only_steps_as_todo(tmp_path: Path):
    trace.record("focus_window", {"title_regex": "x"}, {}, ok=True)
    trace.record(
        "click_element",
        {"spec": {}},
        {"verify": {"ok": True}},
        ok=True,
    )
    out = tmp_path / "replay.py"
    info = trace.generate_stable_script_from_trace(out_path=str(out))
    assert info["todo_markers"] == 1
    assert "TODO[1]" in out.read_text()


def test_failed_steps_are_skipped(tmp_path: Path):
    trace.record("focus_window", {"title_regex": "x"}, {}, ok=True)
    trace.record(
        "click_element",
        {"spec": {"name": "Export"}},
        {"error": "ElementNotFound"},
        ok=False,
    )
    out = tmp_path / "replay.py"
    trace.generate_stable_script_from_trace(out_path=str(out))
    body = out.read_text()
    assert "SKIPPED" in body
    assert "win.descendants" not in body or "title='Export'" not in body


def test_escape_for_typekeys_protects_modifier_chars():
    assert _escape_for_typekeys("a^b+c%d~e") == "a{^}b{+}c{%}d{~}e"
    assert _escape_for_typekeys("plain text") == "plain text"


def test_translate_chord_to_pyautogui():
    assert _translate_chord("^s") == ["ctrl", "s"]
    assert _translate_chord("%{F4}") == ["alt", "f4"]
    assert _translate_chord("^+s") == ["ctrl", "shift", "s"]


def test_schema_rejects_unknown_button():
    with pytest.raises(Exception):
        ClickElementArgs(spec=ElementSpecModel(name="x"), button="middle-extra")


def test_hotkey_args_round_trip():
    a = HotkeyArgs(keys="^s")
    assert a.keys == "^s"


def test_type_text_args_with_verify():
    a = TypeTextArgs(
        text="hello", spec=ElementSpecModel(automation_id="Field1"), verify_value_contains="hello"
    )
    assert a.verify_value_contains == "hello"
    assert a.spec is not None and a.spec.automation_id == "Field1"
