# Outreach Drafts

These drafts are for external visibility after the repository is ready. Do not
post them automatically from automation; publish only after a maintainer reviews
the wording and confirms the target channel.

## GitHub repository description

```text
Windows GUI Automation MCP server for AI coding agents: UIA-first control, verify-after-action, OCR/image fallback, and trace-to-script replay.
```

## Short announcement

```text
I released windows-gui-mcp, an MIT-licensed MCP server for AI coding agents that need to operate Windows desktop apps.

It focuses on semantic UI Automation instead of brittle coordinates: dump the UI tree, find stable controls, act with post-action verification, use OCR/image matching only as a fallback, then generate a pywinauto replay script from the trace.

Repo: https://github.com/dcl632/windows-gui-mcp
PyPI: https://pypi.org/project/windows-gui-mcp/
```

## Reddit / forum draft

```text
I built windows-gui-mcp, a small MCP server for AI coding agents that need to automate Windows desktop applications.

The design goal is reliability rather than raw remote control:

- UI Automation first, not coordinates first
- verify every state-changing action
- OCR/image matching only as a fallback
- trace-to-script generation for pywinauto replay
- examples for Notepad and Calculator

I am looking for feedback from people who automate Windows-only tools, native dialogs, installers, or desktop apps that do not have web APIs.

Repo: https://github.com/dcl632/windows-gui-mcp
PyPI: https://pypi.org/project/windows-gui-mcp/
```

## Hacker News / Show HN draft

```text
Show HN: windows-gui-mcp, an MCP server for Windows GUI automation

windows-gui-mcp helps AI coding agents operate Windows desktop apps through UI Automation instead of raw coordinates. The MCP tools expose a conservative loop: discover windows, focus the target, dump the UIA tree, find stable controls, act with verification, use OCR/image fallback only when semantic lookup fails, and generate a pywinauto replay script from the trace.

The first demos focus on Notepad, Calculator, and native dialogs. The project is MIT licensed and available on PyPI.

Repo: https://github.com/dcl632/windows-gui-mcp
```

## MCP directory submission draft

```text
windows-gui-mcp is an MCP server for AI agents operating Windows desktop applications. It exposes UI Automation-first tools for listing windows, focusing apps, dumping the UI tree, finding controls, clicking and typing with verification, waiting for UI state, using OCR/image fallback as a last resort, and generating pywinauto replay scripts from successful traces.

Package: windows-gui-mcp
License: MIT
Repository: https://github.com/dcl632/windows-gui-mcp
```

## Suggested GitHub issues

Create these as public issues only after maintainer approval:

1. Add native Save As / Open File dialog smoke transcript.
2. Add selector reliability scoring for ambiguous UIA matches.
3. Improve generated replay scripts with waits and verification comments.
4. Add fallback audit records for OCR and image clicks.
5. Document MCP client setup recipes for local and SSH Windows hosts.
6. Add trace redaction guidance for public bug reports.
7. Add Windows 11 Calculator live smoke checklist.
8. Add File Explorer navigation example using stable UIA selectors.
