"""Markdown lint rule for trailing whitespace."""

from pathlib import Path
from typing import List

from markdown_lint import LintIssue

NAME = "trailing-whitespace"
DEFAULT_ENABLED = True


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> List[LintIssue]:
    """Flag trailing whitespace."""
    if line != line.rstrip():
        return [LintIssue(file, lineno, NAME, "trailing whitespace")]
    return []


def fix(line: str) -> str:
    """Remove trailing whitespace, preserving line ending exactly."""
    # Extract original ending
    if line.endswith("\r\n"):
        ending = "\r\n"
        content = line[:-2]
    elif line.endswith("\n"):
        ending = "\n"
        content = line[:-1]
    elif line.endswith("\r"):
        ending = "\r"
        content = line[:-1]
    else:
        ending = ""
        content = line
    return content.rstrip() + ending
