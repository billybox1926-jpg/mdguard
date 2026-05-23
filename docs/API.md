# mdguard public API (#49)

`mdguard.api.lint_paths(paths, *, config=None, fix=False, exclude_patterns=None)` is the supported embedding entrypoint.

It returns a `RunResult` with checked files, skipped files, issues, fixed issue count, remaining issue count, elapsed seconds, and schema metadata. The CLI is a thin wrapper around the same API path.

The public API is source-compatible within the 0.x line where practical. Internal rule context dictionaries are not public API.
