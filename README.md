# mdguard

`mdguard` is a tiny, dependency-light Markdown linter and conservative autofixer
for READMEs, docs folders, notes, and agent-generated repository documentation.

It is intentionally smaller than the full Markdown linting ecosystem. The goal is
practical guardrails for solo developers, small repos, Windows/PowerShell users,
and AI-assisted coding workflows where documentation can get messy fast.

## Status

Working MVP. The package has a `src/mdguard/` implementation, console entry
point, recursive Markdown discovery, built-in rules, JSON output, conservative
autofix, tests, and GitHub Actions CI.

The next release-hardening work is tracked in GitHub issues. Current priorities
are broader real-project usability, config, output schema polish, Markdown-aware
edge cases, and release validation.

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
- `--rules rules.json`

`pyproject.toml` support is planned but not implemented yet.

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
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
