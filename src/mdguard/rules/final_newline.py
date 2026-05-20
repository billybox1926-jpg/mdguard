"""Markdown lint rule requiring a final newline."""

from __future__ import annotations

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


def fix(line: str, ctx: dict | None = None) -> str:
    """Add exactly one final newline when it is missing, preserving style."""
    if line.endswith(("\n", "\r")):
        return line

    newline = "\n"
    if ctx is not None:
        for existing_line in ctx.get("lines", []):
            if existing_line.endswith("\r\n"):
                newline = "\r\n"
                break
            if existing_line.endswith("\n"):
                newline = "\n"
                break
            if existing_line.endswith("\r"):
                newline = "\r"
                break

    return line + newline
