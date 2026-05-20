# Release Checklist

## Pre-release

- [ ] Update version in `pyproject.toml`
- [ ] Confirm changelog/release notes
- [ ] Run test suite locally
- [ ] Run lint and type checks (when enabled)

## Quality gates

- [ ] CI passing on default branch
- [ ] No known high-severity defects
- [ ] README and docs links validated

## Packaging

- [ ] Build sdist and wheel
- [ ] Smoke-test install in clean virtual environment
- [ ] Verify CLI entrypoint works

## Publish

- [ ] Tag release
- [ ] Publish package
- [ ] Announce release notes
