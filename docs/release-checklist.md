# Release checklist

This project is prepared for a `v0.1.0` public release.

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

```bash
git add .
git commit -m "Prepare windows-gui-mcp for public release"
gh repo create dcl632/windows-gui-mcp --public --source=. --remote=origin --push
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 dist/* --title "windows-gui-mcp v0.1.0" --notes-file README.md
```

## PyPI release

Only upload after the GitHub repository, release tag, and CI are public and
green.

```bash
python -m twine upload dist/*
```

Use a PyPI API token. Do not commit PyPI credentials or `.pypirc` files.

## OpenAI Codex for OSS application

After GitHub and PyPI are public, use the prepared answers in
`docs/openai-oss-application.md`.

Do not place ChatGPT account email, OpenAI organization ID, API keys, billing
information, or private deployment details in the repository.
