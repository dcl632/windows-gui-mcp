# Release checklist

This project has a public `v0.1.0` GitHub release and PyPI package. Use this
checklist for future release verification.

## Current public release

- Repository: `https://github.com/dcl632/windows-gui-mcp`
- Release: `https://github.com/dcl632/windows-gui-mcp/releases/tag/v0.1.0`
- Package name: `windows-gui-mcp`
- PyPI: `https://pypi.org/project/windows-gui-mcp/`
- License: MIT
- CI: GitHub Actions on Ubuntu and Windows

## Local verification

Run these checks before tagging:

```bash
python -m compileall -q src tests
python -m pytest -q
ruff check .
python -m build
twine check dist/*
windows-gui-mcp --help
windows-gui-mcp --version
```

## GitHub release

For a future release, build from a clean working tree and create a new tag:

```bash
git add .
git commit -m "Prepare release vX.Y.Z"
git tag vX.Y.Z
git push origin main vX.Y.Z
gh release create vX.Y.Z dist/* --title "windows-gui-mcp vX.Y.Z" --notes-file README.md
```

## PyPI release

Only publish after the GitHub repository, release tag, and CI are public and
green.

Preferred path: PyPI Trusted Publishing:
`https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/`

For `v0.1.0`, the PyPI Trusted Publisher was created with these exact values:

- PyPI project name: `windows-gui-mcp`
- Owner: `dcl632`
- Repository name: `windows-gui-mcp`
- Workflow filename: `publish.yml`
- Environment name: `pypi`

Then run the `Publish to PyPI` workflow from GitHub Actions, or publish a new
GitHub Release. The workflow uses GitHub OIDC and does not need a long-lived
PyPI API token.

Fallback path: local token upload.

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-... python -m twine upload dist/*
```

Do not commit PyPI credentials or `.pypirc` files.

## OpenAI Codex for OSS application

After GitHub and PyPI are public, use the prepared answers in
`docs/openai-oss-application.md`.

Do not place ChatGPT account email, OpenAI organization ID, API keys, billing
information, or private deployment details in the repository.
