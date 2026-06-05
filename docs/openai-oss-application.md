# OpenAI Codex for OSS application notes

Official links:

- Program: https://developers.openai.com/community/codex-for-oss
- Application form: https://openai.com/form/codex-for-oss/
- Terms: https://developers.openai.com/codex/codex-for-oss-terms

## Project identity

- First name: `Ding Chao`
- Last name: `Liao`
- GitHub username: `dcl632`
- Repository URL: `https://github.com/dcl632/windows-gui-mcp`
- Role: primary maintainer / original AI-assisted implementation owner
- Package name: `windows-gui-mcp`
- License: MIT
- Public release: `https://github.com/dcl632/windows-gui-mcp/releases/tag/v0.1.0`
- CI: GitHub Actions on Ubuntu and Windows
- PyPI publishing: published through GitHub Actions Trusted Publishing workflow
- PyPI status: `windows-gui-mcp` version `0.1.0` is available on PyPI
- Security readiness: GitHub private vulnerability reporting, secret scanning,
  and push protection are enabled

## Form choices

- Describe your role: `Primary maintainer`
- I'm interested in: `Codex Security` and `API credits for my project`

## Qualification draft

```text
windows-gui-mcp is an MIT-licensed MCP server for AI coding agents that need to operate Windows desktop applications. It targets an underserved part of the agent ecosystem: Windows-only desktop software that does not expose a browser DOM or web API. The project exposes UI Automation-first tools, verify-after-action workflows, OCR/image fallback as a last resort, and trace-to-script generation so agents can inspect live Windows UI, act on stable controls, verify outcomes, and turn successful sessions into reusable pywinauto scripts.
```

## API credits draft

```text
Use credits to improve Codex-assisted development of Windows GUI automation scenarios, expand Notepad/Calculator/native dialog demos, review trace-to-script output, triage public issues, improve selector reliability, and evaluate safety of MCP tool behavior around action verification, fallback clicks, trace privacy, and generated replay scripts.
```

## Anything else draft

```text
This is a new public project, so the strongest qualification is ecosystem importance rather than existing star count. The repo is already prepared as a real open-source package: public GitHub repository, MIT license, PyPI package, v0.1.0 GitHub release, Ubuntu/Windows CI, issue templates, CONTRIBUTING, SECURITY, private vulnerability reporting, roadmap, Notepad/Calculator demos, and positioning notes. The goal is to give coding agents a safer MCP layer for Windows GUI automation: UIA-first selectors, explicit post-action verification, fallback discipline, and replayable traces.
```

## Ecosystem importance notes

- AI agents have strong tooling for browsers because web pages expose a DOM, but
  many developer, test, installer, enterprise, and Windows-only workflows still
  require native desktop automation.
- `windows-gui-mcp` is focused on that gap rather than general remote desktop
  control.
- The project is new and should not claim adoption metrics it does not have.
  Frame the application around clear scope, public release readiness, safety
  posture, and why Windows GUI automation matters for coding agents.

## Private fields to fill in the form only

Do not commit these values to the repository:

- ChatGPT email address
- OpenAI organization ID
- Billing or payment details
- Any private deployment hostnames, IP addresses, usernames, or trace paths

## Submission checklist

- Public GitHub repository exists.
- Release `v0.1.0` exists.
- GitHub Actions CI is green.
- PyPI Trusted Publisher is configured and the package is published.
- README includes install, run, examples, and safety rules.
- CONTRIBUTING, SECURITY, changelog, pull request template, and issue templates exist.
- GitHub private vulnerability reporting, secret scanning, and push protection are enabled.
- Repository contains no private host, account, email, or internal workflow details.
- PyPI package exists and installs successfully from a clean virtual environment.
- Demo, roadmap, outreach drafts, and positioning notes are present.
