# Rules

## MVP rule set

The initial `mdguard` rules are:

- `line-length`
- `trailing-whitespace`
- `duplicate-headings`
- `heading-jump`
- `missing-h1`
- `empty-link`
- `final-newline`

## Rule IDs and stability

Rule IDs should be treated as public API for CI and scripts. Renaming a rule ID is a breaking change.

## Output expectations

Each finding should include:

- file path
- line number (and optional column)
- rule ID
- concise message

## Rule behavior principles

- Report only what can be explained clearly.
- Avoid false positives where possible.
- Prefer conservative defaults over aggressive style enforcement.

## Autofix tagging

Rules that support autofix should explicitly declare that capability so users can reason about `--fix` behavior.
