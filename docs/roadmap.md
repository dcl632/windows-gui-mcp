# Roadmap

This roadmap is issue-ready and focuses on making Windows desktop automation
more reliable for AI coding agents. It does not imply a guaranteed release
schedule.

## Near-term work

1. Native Windows dialog coverage
   - Add documented scenarios for Save As, Open File, confirmation dialogs, and
     common error dialogs.
   - Acceptance: each scenario has a transcript, a verification condition, and a
     trace-to-script example.

2. Selector reliability scoring
   - Rank candidate selectors by `automation_id`, `name`, `control_type`, and
     `class_name` stability.
   - Acceptance: ambiguous matches explain why one selector was chosen.

3. Trace replay hardening
   - Improve generated pywinauto scripts so they preserve waits, focus changes,
     and verification checks.
   - Acceptance: traces from Notepad and Calculator produce readable replay
     scripts with TODO markers for fallback-only steps.

4. Fallback safety gates
   - Require explicit fallback reasons when OCR, image matching, or coordinate
     anchors are used.
   - Acceptance: fallback actions record the failed semantic lookup and the
     verification condition used afterward.

## Medium-term work

5. Live Windows smoke test matrix
   - Document repeatable smoke tests for Windows 11 Notepad, Calculator, File
     Explorer, and native dialogs.
   - Acceptance: maintainers can run a checklist on a local Windows desktop
     session before releases.

6. MCP client recipes
   - Add copy-paste configuration examples for common MCP clients and remote
     Windows SSH setups.
   - Acceptance: each recipe states where the MCP server runs and what
     permissions the Windows session needs.

7. Trace privacy and redaction
   - Add guidance and utilities for redacting private paths, window titles, OCR
     text, and screenshot paths from traces.
   - Acceptance: public bug reports can include safe minimal traces.

8. App-specific selector notes
   - Collect selector notes for common Windows-only tools where UI Automation is
     available but inconsistent.
   - Acceptance: notes prefer public apps and avoid private customer or account
     data.

## Maintenance priorities

- Keep the toolset small and composable.
- Prefer UI Automation over coordinates.
- Preserve post-action verification as a default design rule.
- Keep examples reproducible with public Windows applications.
- Treat OCR and image matching as fallbacks with audit trails.
