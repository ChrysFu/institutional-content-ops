# Contributing

Contributions should improve a real content-operation need while preserving the rule that people remain responsible for facts, permissions, editorial judgment, and release approval.

## Development loop

1. Create a focused branch from `main`.
2. Add or update a behavior test before changing Python behavior.
3. Keep public interfaces backward compatible unless migration notes are agreed.
4. Update the relevant workflow documentation in the same change.
5. Run the validation commands below before opening a pull request.

```bash
python3 -m compileall -q src tests
ruff check src tests
python3 -m unittest discover -s tests -v
python3 src/content_guard.py --self-test
python3 src/content_guard.py --draft examples/draft-ready.md --policy content-policy.example.json --fail-on-issues
python3 src/content_guard.py --scan examples --policy content-policy.example.json --format sarif --output artifacts/content-scan.sarif --fail-on-issues
python3 src/repository_checks.py .
actionlint
```

Pull requests should explain the operational risk addressed, evidence used, compatibility impact, and rollback path. Do not include real confidential drafts, credentials, private analytics, or unapproved personal information in fixtures or logs.

Contributions incorporated into this repository are distributed under the repository's [MIT License](LICENSE). By submitting a contribution, you confirm that you have the right to do so under those terms.
