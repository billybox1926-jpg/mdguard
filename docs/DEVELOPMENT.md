# Development

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -e .
```

## Test command

```bash
python -m unittest discover -s tests -v
```

The project currently uses the Python standard-library `unittest` runner and has
no runtime dependencies.

## Python compatibility

`pyproject.toml` declares Python `>=3.9`. Keep implementation and tests compatible
with Python 3.9 unless the supported version range is intentionally changed.

One known compatibility pitfall: `Path.write_text(..., newline="")` is not
available on Python 3.9. Use `path.open("w", encoding="utf-8", newline="")` when
newline control is required.

## Style goals

- Keep modules small and focused.
- Prefer standard library utilities.
- Add tests for every new rule and autofix path.
- Keep CLI behavior documented before relying on it in CI.
- Avoid adding dependencies without an explicit dependency-policy decision.

## Current package shape

- `src/mdguard/cli.py` contains the command-line entry point.
- `src/mdguard/core.py` contains issue modeling, rule loading, file decoding, and
  autofix orchestration.
- `src/mdguard/discovery.py` contains Markdown target discovery.
- `src/mdguard/output.py` contains machine-readable output helpers.
- `src/mdguard/rules/` contains built-in rule modules.
- `tests/` contains the unittest suite.

## Adding or changing a rule

1. Add or update the rule module in `src/mdguard/rules/`.
2. Keep the rule ID stable once public.
3. Add focused tests in `tests/test_rules.py`.
4. Add CLI/core tests if the change affects flags, output, config, or autofix.
5. Update `docs/RULES.md` if behavior or config changes.
6. Run the full unittest suite.
