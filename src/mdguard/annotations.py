"""GitHub Actions annotation output."""

from __future__ import annotations

from mdguard.core import LintIssue


def _escape(value: str) -> str:
    return (
        value.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


def render_github_annotations(issues: list[LintIssue]) -> str:
    lines = []
    for issue in issues:
        lines.append(
            f"::warning file={_escape(str(issue.file))},line={issue.line},title={_escape(issue.rule)}::{_escape(issue.message)}"
        )
    return "\n".join(lines)
