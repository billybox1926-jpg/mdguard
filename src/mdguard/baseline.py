"""Baseline file support for incremental mdguard adoption."""

from __future__ import annotations

import json
from pathlib import Path

from mdguard.core import LintIssue


def issue_key(issue: LintIssue) -> str:
    return f"{Path(issue.file).as_posix()}:{issue.line}:{issue.rule}:{issue.message}"


def load_baseline(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(item["key"]) for item in data.get("issues", [])}


def write_baseline(path: Path, issues: list[LintIssue]) -> None:
    payload = {
        "issues": [
            {
                "key": issue_key(issue),
                "path": str(issue.file),
                "line": issue.line,
                "rule": issue.rule,
                "message": issue.message,
            }
            for issue in issues
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def filter_baselined(
    issues: list[LintIssue], baseline_keys: set[str]
) -> list[LintIssue]:
    return [issue for issue in issues if issue_key(issue) not in baseline_keys]
