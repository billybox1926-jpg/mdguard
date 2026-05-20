# Architecture

## Overview

`mdguard` is a small `src/`-layout Python package with a clear split between
CLI wiring, file discovery, rule execution, output formatting, and optional
autofix application.

## Package layout

```text
src/mdguard/
  __init__.py
  cli.py
  core.py
  discovery.py
  output.py
  rules/
```

## Core flow

1. Parse CLI arguments in `cli.py`.
2. Resolve input targets into Markdown files in `discovery.py`.
3. Run rule checks in `core.py` using rule modules under `rules/`.
4. Return findings in a shared in-memory model.
5. Render human-readable or JSON output in `output.py`.
6. Apply safe autofixes when `--fix` is enabled.

## Rule model

Each rule exposes a stable identifier and a check entrypoint that can return zero
or more findings. Some rules also expose an autofix function or a whole-file
post-check function.

Rules should be deterministic, isolated, and easy to test. See `docs/RULES.md`
for the built-in rule contract.

## Performance principles

- Prefer single-pass scans where practical.
- Avoid external dependencies in the MVP.
- Keep file IO predictable and explicit.
- Do not traverse known noisy directories such as `.git`, virtualenvs,
  `node_modules`, build outputs, or Python caches.

## Compatibility target

- Python 3.9+
- Cross-platform command-line behavior on Linux, macOS, and Windows
- Windows-friendly newline handling during autofix
