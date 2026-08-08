## Change summary

Describe the user-visible workflow improvement and the operational risk it addresses.

## Validation

- [ ] `python3 -m compileall -q src tests`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 src/content_guard.py --self-test`
- [ ] `python3 src/repository_checks.py .`
- [ ] Example policy and draft pass with `--fail-on-issues`

## Release safety

- [ ] Existing interfaces and default behavior remain compatible, or migration notes are included.
- [ ] Content facts, names, titles, numbers, permissions, and sensitive wording received human review.
- [ ] No automated result is represented as publication approval.
- [ ] Rollback owner and rollback action are known for changes affecting a live process.
