"""Markdown lint rule for duplicate headings."""

from pathlib import Path
from typing import List

from markdown_lint import LintIssue

NAME = "duplicate-headings"
DEFAULT_ENABLED = False


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> List[LintIssue]:
    if not (match := ctx["heading_re"].match(line)):
        return []
    title = match.group(2).strip().lower()
    original_title = match.group(2).strip()
    issues: List[LintIssue] = []

    if title in ctx["seen_headings"]:
        issues.append(
            LintIssue(
                file,
                lineno,
                NAME,
                f"duplicate heading '{original_title}' "
                f"(first at line {ctx['seen_headings'][title]})",
            )
        )
    else:
        ctx["seen_headings"][title] = lineno
    return issues
