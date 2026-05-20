"""Markdown lint rule for heading jump."""

from pathlib import Path
from typing import List

from mdguard.core import LintIssue

NAME = "heading-jump"
DEFAULT_ENABLED = True


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> List[LintIssue]:
    """Flag heading level jumps greater than 1 (e.g., h1 -> h3)."""
    if not (match := ctx["heading_re"].match(line)):
        return []
    level = len(match.group(1))
    issues: List[LintIssue] = []

    if ctx["prev_level"] and level > ctx["prev_level"] + 1:
        issues.append(
            LintIssue(
                file,
                lineno,
                NAME,
                f"heading level jumps from {ctx['prev_level']} to {level}",
            )
        )

    ctx["prev_level"] = level
    return issues
