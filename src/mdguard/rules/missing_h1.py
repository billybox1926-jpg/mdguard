"""Markdown lint rule for missing h1."""

from pathlib import Path
from typing import List

from mdguard.core import LintIssue

NAME = "missing-h1"
DEFAULT_ENABLED = False


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> List[LintIssue]:
    """Collect heading data during the line-by-line pass."""
    if ctx.get("in_code_block"):
        return []
    if match := ctx["heading_re"].match(line):
        if len(match.group(1)) == 1:
            ctx["has_h1"] = True
    return []


def post_check(file: Path, ctx: dict, config: dict) -> List[LintIssue]:
    """Report an issue if no h1 was found after scanning the whole file."""
    if not ctx.get("has_h1"):
        return [LintIssue(file, 1, NAME, "document has no top-level heading (h1)")]
    return []
