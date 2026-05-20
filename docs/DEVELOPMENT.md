# Development

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e .
```

## Planned test command

```bash
python -m pytest
```

## Style goals

- Keep modules small and focused.
- Prefer standard library utilities.
- Add tests for every new rule and autofix path.

## Suggested implementation order

1. Bootstrap `src/mdguard` package and CLI.
2. Implement file discovery.
3. Implement finding/output model.
4. Port/implement MVP rules.
5. Add autofix plumbing and tests.
