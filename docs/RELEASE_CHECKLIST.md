# Release Checklist

## Pre-release

- [ ] Confirm the target version in `pyproject.toml`.
- [ ] Confirm changelog or release notes are current.
- [ ] Confirm README and docs describe shipped behavior.
- [ ] Review open issues for release blockers.

## Local quality gates

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m mdguard.cli --help
python -m mdguard.cli --list-rules
python -m mdguard.cli README.md docs/*.md --json
```

Checklist:

- [ ] Local test suite passes.
- [ ] CLI help works.
- [ ] Rule listing works.
- [ ] JSON output is parseable.
- [ ] No known high-severity defects remain.

## CI quality gates

- [ ] Default branch CI is passing.
- [ ] Supported Python versions pass in CI.
- [ ] Release validation workflow passes, once implemented.
- [ ] Repository docs dogfood check passes, once enabled.

## Packaging

```bash
python -m build
```

Checklist:

- [ ] Build sdist and wheel.
- [ ] Smoke-test install in a clean virtual environment.
- [ ] Verify the `mdguard` console entry point works from the built wheel.
- [ ] Verify `python -m mdguard.cli --help` works.

## Publish

- [ ] Tag release.
- [ ] Publish package.
- [ ] Create GitHub release notes.
- [ ] Announce release notes where appropriate.
