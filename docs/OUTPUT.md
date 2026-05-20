# Output

## Streams

`mdguard` separates human output and machine output:

- Human-readable lint messages are written to stderr.
- `--json` output is written to stdout.
- In `--json` mode, stdout contains only JSON.

This makes it safe for scripts to parse stdout while still allowing diagnostics
on stderr.

## Human output

Default human output is optimized for local terminal use. It may include Unicode
symbols such as check marks, warning signs, and tool icons.

Examples:

```text
README.md:2: trailing whitespace [trailing-whitespace]
⚠️  1 issue found.
```

```text
✅ No issues found in README.md.
```

A future phase may add `--no-emoji` or another conservative terminal mode.

## JSON output

`--json` emits a single JSON object.

Current schema version: `1`

Top-level fields:

| Field | Type | Description |
| --- | --- | --- |
| `schema_version` | integer | JSON report schema version. |
| `tool` | object | Tool metadata. |
| `files` | array | Per-file lint results. |
| `issue_count` | integer | Total number of reported issues. |

`tool` fields:

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Always `mdguard`. |
| `version` | string | Installed package version or `0+unknown`. |

Each `files` entry contains:

| Field | Type | Description |
| --- | --- | --- |
| `path` | string | Path as processed by the CLI. |
| `issues` | array | Issues reported for that file. |

Each issue contains:

| Field | Type | Description |
| --- | --- | --- |
| `line` | integer | 1-based line number. |
| `rule` | string | Stable rule ID. |
| `message` | string | Human-readable issue message. |

Example:

```json
{
  "schema_version": 1,
  "tool": {
    "name": "mdguard",
    "version": "0.1.0"
  },
  "files": [
    {
      "path": "README.md",
      "issues": [
        {
          "line": 2,
          "rule": "trailing-whitespace",
          "message": "trailing whitespace"
        }
      ]
    }
  ],
  "issue_count": 1
}
```

## JSON and autofix

When `--fix --json` is used, the current report contains remaining unfixed
issues after safe fixes are applied. Autofixable issues that were fixed are not
included as active issues in the JSON report.

A future issue tracks richer fixed-vs-remaining reporting.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Completed and no remaining lint issues were found. |
| 1 | Lint issues remain, targets were missing, or no Markdown files were found. |
| 2 | CLI configuration or rule-selection error. |
