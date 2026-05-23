# Roadmap

## Completed MVP foundation

- [x] Project metadata and top-level README
- [x] Documentation skeleton
- [x] `src/mdguard` package bootstrap
- [x] Console entry point
- [x] Recursive Markdown discovery
- [x] Common noisy-directory ignores
- [x] Initial unittest suite
- [x] GitHub Actions CI workflow

## Completed MVP behavior

- [x] Human-readable CLI output
- [x] JSON output mode
- [x] Conservative `--fix` mode
- [x] MVP built-in rule set
- [x] Rule enable/disable controls
- [x] JSON `--rules` configuration file support
- [x] Encoding-aware autofix writes for supported encodings

## Phase 3: release hardening and real-project usability

Tracked in the Phase 3 GitHub milestone.

- [x] Refresh and align docs with shipped MVP behavior
- [ ] Stabilize and document JSON schema expectations
- [x] Add project-specific ignore/exclude patterns (via .mdguardignore)
- [ ] Add `pyproject.toml` configuration support
- [ ] Refine Markdown-specific line-length exceptions
- [x] Make rules aware of fenced code blocks
- [ ] Improve autofix fixed/remaining reporting semantics
- [ ] Add release validation and package smoke tests
- [ ] Verify the supported Python version matrix
- [x] Dogfood mdguard against this repository's docs in CI

## Phase 4: ecosystem integration and advanced Markdown intelligence

Tracked in the Phase 4 GitHub milestone.

- [ ] Inline suppression comments
- [ ] Baseline file support
- [ ] Structured rule metadata
- [ ] Generated rule documentation
- [ ] Pre-commit hook documentation
- [ ] stdin support
- [ ] Front matter awareness
- [ ] Internal heading anchor validation
- [ ] GitHub Actions annotation output
- [ ] CommonMark/GFM parser strategy spike

## Phase 4 backlog

Keep these ideas as backlog until the top Phase 4 work clarifies scope:

- SARIF output
- Optional plugin loading
- Setext heading support
- Reference-style link validation
- Optional local and remote broken-link checking
- Rule severity levels
- Built-in presets/profiles
- `mdguard init`
- Autofix dry-run or unified diff mode
- Editor integration notes
- CHANGELOG and release-note automation
- PyPI publishing workflow
- README badges and project metadata polish

## Phase 5: scale and ecosystem architecture

Tracked in the Phase 5 GitHub milestone.

- [ ] markdownlint compatibility mapping
- [ ] Public Python API design
- [ ] Batch result model for multi-file analysis
- [ ] Hierarchical configuration discovery
- [ ] Optional documentation quality score summary
- [ ] Editor integration design note
- [ ] Language Server Protocol diagnostics prototype
- [ ] Documentation site generation plan
- [ ] Safe remote-link-checking cache design
- [ ] Long-term dependency and extras policy
