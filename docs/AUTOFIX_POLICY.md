# Autofix Policy

`mdguard` only applies conservative fixes by default.

## Safe-by-default fixes

The initial safe autofixes are:

- trim trailing whitespace
- ensure exactly one final newline at end of file

## Non-goals for early autofix

The tool should not rewrite document structure in early versions, including:

- heading level rewrites
- title synthesis from ambiguous content
- broad link text rewrites

## Principles

1. **Low surprise:** fixes should be predictable and minimal.
2. **Easy review:** diffs should be small and obvious.
3. **Reversible:** users should be able to undo without losing semantic content.
4. **Rule-local behavior:** each rule owns its own fix logic.

## Safety controls

- `--fix` must be explicit.
- Findings should still be reported for transparency.
- Future high-impact fixes should require opt-in flags.
