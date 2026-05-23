# Configuration

## Current configuration surfaces

`mdguard` is currently CLI-first. These options are implemented:

- `--max-length N` sets the default line-length threshold.
- `--strict` enables every built-in rule and sets `max_length` to 100.
- `--enable RULE` enables a rule by ID. It can be repeated.
- `--disable RULE` disables a rule by ID. It can be repeated.
- `--rules PATH` loads a JSON rules configuration file.
- `--exclude PATTERN` excludes matching Markdown files or directories during
  discovery. It can be repeated.
- `.mdguardignore` (in the current working directory) provides persistent
  exclusion patterns.

Unknown rule names are rejected with a nonzero exit code and a list of valid rule
names.

## Exclude patterns

Use repeated `--exclude` flags or a `.mdguardignore` file to skip
project-specific generated, vendored, or otherwise noisy Markdown paths.

Patterns are slash-separated globs matched against paths relative to each
directory target. Backslashes in patterns are normalized to slashes so the same
pattern style works on Windows and POSIX shells.

### .mdguardignore

If a `.mdguardignore` file exists in the current working directory, its lines
are added to the exclusion patterns. Lines starting with `#` are treated as
comments. Empty lines are ignored.

Example `.mdguardignore`:

```text
# Ignore generated documentation
docs/generated/**
# Ignore vendored files
vendor
```

### Pattern behavior

Useful forms:

- `docs/generated/**` excludes all Markdown files under `docs/generated/`.
- `vendor` excludes a directory named `vendor` below the target.
- `README.md` excludes a direct file target named `README.md`.

For now, exclude patterns are CLI-only. Project-level excludes will move into
`pyproject.toml` when project configuration is implemented.

## JSON rules file

`--rules` expects a JSON object with a `rules` object.

Example:

```json
{
  "rules": {
    "line-length": { "max": 100 },
    "trailing-whitespace": true,
    "duplicate-headings": true,
    "missing-h1": false
  }
}
```

Rule values can be:

- `true` to enable a rule
- `false` to disable a rule
- an object for rule-specific settings, when supported by that rule

The `line-length` rule supports a rule-specific `max` value. If omitted, it uses
`--max-length` or the default threshold.

## CLI precedence

Configuration is applied in this order:

1. CLI defaults
2. `--rules` JSON file
3. `--strict`
4. repeated `--enable` flags
5. repeated `--disable` flags

Later entries override earlier entries.

## Exit codes for config errors

Configuration and rule-selection errors exit with code 2. Examples include:

- missing `--rules` file
- invalid JSON
- top-level JSON value is not an object
- `rules` value is not an object
- unknown rule IDs in JSON, `--enable`, or `--disable`

## Planned project configuration

`pyproject.toml` support is planned for a later phase under a `[tool.mdguard]`
table. It is not implemented yet.

Proposed example:

```toml
[tool.mdguard]
line_length = 100
ignore = ["docs/generated/**"]
enable = ["duplicate-headings"]
disable = ["line-length"]
```

Because mdguard currently supports Python 3.9 and stays dependency-light,
`pyproject.toml` support needs an explicit compatibility decision before
implementation.
