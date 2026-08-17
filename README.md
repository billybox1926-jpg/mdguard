# mdguard

![mdguard icon](icon.svg)

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/billybox1926-jpg/mdguard/releases/tag/v0.1.0)
[![CI](https://github.com/billybox1926-jpg/mdguard/workflows/CI/badge.svg)](https://github.com/billybox1926-jpg/mdguard/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/status-released-brightgreen.svg)](https://github.com/billybox1926-jpg/mdguard/releases/tag/v0.1.0)

`mdguard` is a tiny, dependency-light Markdown linter and conservative autofixer
for READMEs, docs folders, notes, and agent-generated repository documentation.

It is intentionally smaller than the full Markdown linting ecosystem. The goal is
practical guardrails for solo developers, small repos, Windows/PowerShell users,
and AI-assisted coding workflows where documentation can get messy fast.

mdguard focuses on formatting consistency (whitespace, line length, heading
structure, link integrity) with **optional** security-focused rules you can enable
for CI pipelines and shared documentation: detection of XSS vectors in raw HTML,
dangerous URI schemes like `javascript:`, and patterns that resemble API keys or
tokens. These security rules are heuristic and opt-in — they supplement, but do
not replace, dedicated secret scanners and security review.

## Status

Released. The package has a `src/mdguard/` implementation, console entry
point, recursive Markdown discovery, built-in rules, JSON/GitHub output, conservative
autofix, baselines, inline suppressions, project configuration, tests, and local release
validation. Latest release: [v0.1.0](https://github.com/billybox1926-jpg/mdguard/releases/tag/v0.1.0).

## Install locally

```bash
python -m pip install -e .
```

## Usage

```bash
mdguard README.md
mdguard docs/
mdguard README.md docs/
mdguard . --json
mdguard . --fix
```

Useful options:

```bash
mdguard --list-rules
mdguard docs/ --strict
mdguard docs/ --max-length 100
mdguard docs/ --enable missing-h1
mdguard docs/ --disable line-length
mdguard docs/ --exclude "docs/generated/**"
mdguard docs/ --rules rules.json
```

## Built-in rules

Enabled by default:

- `empty-link`
- `final-newline`
- `heading-jump`
- `line-length`
- `trailing-whitespace`

Available but disabled by default:

- `duplicate-headings`
- `missing-h1`

Autofix currently handles conservative formatting changes such as trimming
trailing whitespace and ensuring a final newline. Structural or semantic document
changes are reported instead of rewritten.

See [docs/RULES.md](docs/RULES.md) for rule behavior and the built-in rule
contract.

## JSON output

`--json` emits machine-readable results on stdout and keeps human-readable
status text off stdout.

Current top-level JSON fields:

- `schema_version`
- `tool`
- `files`
- `issue_count`

See [docs/OUTPUT.md](docs/OUTPUT.md) for the output contract.

## Configuration

The current implemented configuration surface is CLI-first:

- `--max-length N`
- `--strict`
- `--enable RULE`
- `--disable RULE`
- `--exclude PATTERN`
- `--rules rules.json`

`pyproject.toml` `[[tool.mdguard]]` configuration is supported alongside the CLI flags.

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Autofix policy](docs/AUTOFIX_POLICY.md)
- [Configuration](docs/CONFIGURATION.md)
- [Development](docs/DEVELOPMENT.md)
- [Output](docs/OUTPUT.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Roadmap](docs/ROADMAP.md)
- [Rules](docs/RULES.md)

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python scripts/validate.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
