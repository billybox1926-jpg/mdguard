# mdguard

`mdguard` is a tiny, dependency-light Markdown linter and conservative autofixer for READMEs, docs folders, notes, and agent-generated repository documentation.

It is intentionally smaller than the full Markdown linting ecosystem. The goal is practical guardrails for solo developers, small repos, Windows/PowerShell users, and AI-assisted coding workflows where documentation can get messy fast.

## Status

Early bootstrap. The package metadata exists, but the working source package, tests, rule modules, and CI workflow are still being built.

## Goals

- Stay small, fast, and easy to understand.
- Prefer the Python standard library wherever possible.
- Support a simple `src/mdguard/` package layout.
- Provide useful human-readable output first.
- Provide JSON output for scripts and CI.
- Autofix only conservative, low-risk issues at first.
- Make rule behavior easy to test and extend.

## Planned MVP rules

The first built-in rules should cover:

- line length
- trailing whitespace
- duplicate headings
- heading jumps
- missing H1
- empty links
- final newline

The line-length rule should use Unicode-aware display width rather than plain `len(...)` so emoji and wide characters are handled correctly.

## Planned usage

```powershell
mdguard README.md
mdguard docs/
mdguard . --json
mdguard . --fix
```

## Autofix policy

`mdguard` should only make conservative fixes by default. Safe early fixes include trimming trailing whitespace and ensuring a final newline. Structural or semantic document changes should be reported, not rewritten, unless the behavior is obvious and well-tested.

See [docs/AUTOFIX_POLICY.md](docs/AUTOFIX_POLICY.md) for the full policy.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Autofix policy](docs/AUTOFIX_POLICY.md)
- [Configuration](docs/CONFIGURATION.md)
- [Development](docs/DEVELOPMENT.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Roadmap](docs/ROADMAP.md)
- [Rules](docs/RULES.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
