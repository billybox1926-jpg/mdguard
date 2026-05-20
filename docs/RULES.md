# Rules

## Built-in rule set

Enabled by default:

| Rule ID | Purpose | Autofix |
| --- | --- | --- |
| `empty-link` | Reports inline links with empty destinations. | No |
| `final-newline` | Reports files that do not end with a newline. | Yes |
| `heading-jump` | Reports heading levels that skip more than one level. | No |
| `line-length` | Reports lines that exceed the configured display width. | No |
| `trailing-whitespace` | Reports trailing spaces or tabs. | Yes |

Available but disabled by default:

| Rule ID | Purpose | Autofix |
| --- | --- | --- |
| `duplicate-headings` | Reports repeated heading text. | No |
| `missing-h1` | Reports documents without a top-level H1 heading. | No |

Use `mdguard --list-rules` to inspect the installed rule set.

## Rule IDs and stability

Rule IDs are public API for CLI flags, JSON output, config files, CI scripts, and
future suppressions. Renaming a rule ID is a breaking change.

## Rule behavior principles

- Report only what can be explained clearly.
- Avoid false positives where possible.
- Prefer conservative defaults over aggressive style enforcement.
- Keep autofix limited to low-risk, well-tested formatting edits.
- Do not perform semantic document rewrites in autofix mode.

## Built-in rule contract

Built-in rules live under `src/mdguard/rules/`. A rule module is expected to
provide these fields/functions:

| Name | Required | Description |
| --- | --- | --- |
| `NAME` | Yes | Stable rule ID, such as `line-length`. |
| `DEFAULT_ENABLED` | Yes | Whether the rule runs with default config. |
| `check(lines, config)` | Yes | Returns zero or more `LintIssue` objects. |
| `fix(text, config)` | Optional | Returns fixed text for safe autofix rules. |
| `post_check(text, config)` | Optional | Reports issues needing whole-file checks. |
| `ALLOW_ADD_LINE_ENDING` | Optional | Allows fix validation to add a final newline. |

`load_rules()` converts these module attributes into the runtime rule registry.

### `check(lines, config)`

`check` receives decoded lines and the merged config dictionary. It should return
`LintIssue` values with:

- 1-based `line`
- stable `rule` ID
- concise `message`

`check` should not mutate files or perform I/O.

### `fix(text, config)`

`fix` receives the full decoded file text. It should return the full replacement
text. Fixes must be conservative and deterministic.

The core validates fixes before writing. A fix is rejected if it changes more
than the owning rule is allowed to change.

### `post_check(text, config)`

`post_check` is optional and intended for whole-file checks that are awkward to
express line-by-line, such as final-newline detection.

## Current rule notes

### `line-length`

Uses Unicode-aware display width instead of plain `len(...)`. Combining marks are
zero-width, East Asian wide/full-width characters count as width 2, and other
characters count as width 1.

Configuration:

```json
{
  "rules": {
    "line-length": { "max": 100 }
  }
}
```

If no rule-specific `max` is set, `line-length` uses the top-level `max_length`.

### `duplicate-headings`

Disabled by default because repeated headings can be intentional in long docs.
Enable it explicitly or use `--strict`.

### `missing-h1`

Disabled by default because fragments, includes, and generated docs often omit a
single document-level H1. Enable it for standalone document checks.
