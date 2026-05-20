"""Markdown lint rule for empty link."""

from pathlib import Path
from typing import List

from mdguard.core import LintIssue

NAME = "empty-link"
DEFAULT_ENABLED = True


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> List[LintIssue]:
    """Flag markdown links with empty URLs."""
    issues: List[LintIssue] = []
    for _, url in ctx["link_re"].findall(line):
        if not url.strip():
            issues.append(LintIssue(file, lineno, NAME, "empty markdown link URL"))
    return issues
