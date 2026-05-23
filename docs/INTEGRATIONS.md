# mdguard integrations

## pre-commit hook (#42)

Repository hook metadata is provided in `.pre-commit-hooks.yaml`.

Example:

```yaml
repos:
  - repo: https://github.com/billybox1926-jpg/mdguard
    rev: v0.1.0
    hooks:
      - id: mdguard
        args: [--strict]
```

Use `--fix` locally when you want safe rewrites. In CI, prefer lint-only mode or run `--fix` in a separate formatting step so changed files are visible.

## GitHub Actions annotations (#46)

Use `--format github` to emit workflow command annotations:

```bash
mdguard README.md docs --format github
```

Annotations are derived from the same structured issues as human and JSON output.

## Editor integrations (#53)

Recommended first path: run `mdguard --json` from an editor task or problem matcher. LSP is deferred until the public API remains stable across releases.
