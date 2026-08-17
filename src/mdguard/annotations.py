"""GitHub Actions annotation output."""

from __future__ import annotations

from mdguard.core import LintIssue


def _escape(value: str) -> str:
    # Escape % first so our own %XX codes (introduced below) don't get
    # double-escaped. CRLF pairs are preserved via a placeholder so bare
    # \r and \n replacements don't split them.
    value = value.replace("\r\n", "\x00")
    value = value.replace("%", "%25")
    value = (
        value.replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
        .replace('"', "%22")
        .replace("::", "%3A%3A")
    )
    value = value.replace("\x00", "%0D%0A")
    return value


def render_github_annotations(issues: list[LintIssue]) -> str:
    lines = []
    for issue in issues:
        lines.append(
            f"::warning file={_escape(str(issue.file))},line={issue.line},title={_escape(issue.rule)}::{_escape(issue.message)}"
        )
    return "\n".join(lines)
