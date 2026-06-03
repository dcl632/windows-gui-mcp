## Summary

Describe the behavior or documentation change.

## Validation

- [ ] `python -m compileall -q src tests`
- [ ] `python -m pytest -q`
- [ ] `ruff check .`
- [ ] `python -m build`
- [ ] `twine check dist/*`
- [ ] Live Windows GUI test, if automation behavior changed

## Safety checklist

- [ ] Uses UI Automation lookup before coordinate, OCR, or image fallback.
- [ ] Adds or preserves post-action verification.
- [ ] Does not include private hostnames, IP addresses, account names, emails,
      screenshots, traces, credentials, or customer/application data.
