"""Markdown lint rule requiring a final newline."""

from pathlib import Path
from typing import List

from mdguard.core import LintIssue

NAME = "final-newline"
DEFAULT_ENABLED = True
ALLOW_ADD_LINE_ENDING = True


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> List[LintIssue]:
    """Report when the last line of a non-empty file has no trailing newline."""
    lines = ctx.get("lines", [])
    if not lines or lineno != len(lines):
        return []

    last_line = lines[-1]
    if last_line and not last_line.endswith(("\n", "\r")):
        return [LintIssue(file, lineno, NAME, "file must end with a final newline")]
    return []


def fix(line: str) -> str:
    """Add exactly one final newline when it is missing."""
    if line.endswith(("\n", "\r")):
        return line
    return line + "\n"
