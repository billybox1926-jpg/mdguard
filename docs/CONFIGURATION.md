# Configuration

## Current state

In foundation mode, configuration is intentionally minimal and may evolve as the package is implemented.

## Planned configuration surfaces

- CLI flags (primary interface)
- optional project config file in a later phase
- per-rule enable/disable controls
- line-length threshold overrides

## Proposed config file (future)

A likely future file is `pyproject.toml` under a `[tool.mdguard]` table.

Example (proposed):

```toml
[tool.mdguard]
line_length = 100
ignore = ["docs/generated/**"]
enable = ["line-length", "trailing-whitespace"]
```

This is not yet implemented.
