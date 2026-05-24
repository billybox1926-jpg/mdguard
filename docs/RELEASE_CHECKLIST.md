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
python scripts/validate.py
```

Checklist:

- [ ] Local test suite passes.
- [ ] CLI help and version output work.
- [ ] Rule listing works.
- [ ] JSON output is parseable.
- [ ] Repository docs dogfood check passes.

## CI quality gates

- [ ] Default branch CI is passing when Actions are available.
- [ ] Supported Python versions pass locally or in CI.
- [ ] Release validation workflow passes before publishing a tag.
- [ ] Repository docs dogfood check passes.

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
