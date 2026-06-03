# Security Policy

`windows-gui-mcp` can operate a live Windows desktop session. Security reports
are welcome, especially when they involve unsafe action execution, incorrect
verification, unintended trace-to-script output, or privacy leaks in logs,
screenshots, traces, examples, or generated scripts.

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Please report security issues through GitHub Security Advisories when available
for the repository. If that is not available, open a GitHub issue with a minimal
description and avoid posting exploit details, private hostnames, IP addresses,
account names, screenshots, tokens, or sensitive traces.

Useful reports include:

- The affected version or commit.
- The Windows version and automation backend involved.
- Minimal reproduction steps using Notepad, Calculator, or a native Windows
  dialog when possible.
- Expected behavior, actual behavior, and why the behavior may be unsafe.

## Safety expectations

Security-sensitive changes should preserve these properties:

- UI Automation lookup is preferred before coordinate, OCR, or image fallback.
- Actions should have explicit post-action verification.
- Generated replay scripts should avoid embedding private paths or environment
  details.
- Logs, examples, and tests should not include private infrastructure,
  customer data, credentials, or personal account details.
