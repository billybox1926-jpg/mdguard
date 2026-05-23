"""Markdown lint rule for line length."""

from __future__ import annotations

from typing import Optional

from mdguard.core import LintIssue, display_width

NAME = "line-length"
DEFAULT_ENABLED = True
DESCRIPTION = "Flag lines wider than the configured maximum with Markdown-aware exceptions."
TAGS = ("formatting",)
ALIASES = ("MD013",)


def _configured_max(config: dict) -> Optional[int]:
    rule = config.get(NAME)
    if rule is False:
        return None
    if isinstance(rule, dict):
        return rule.get("max", config.get("max_length", 120))
    return config.get("max_length", 120)


def _is_markdown_exception(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped.startswith("|")
        or stripped.startswith("[!")
        or stripped.startswith("<")
        or (stripped.startswith("[") and "]:" in stripped)
        or "http://" in stripped
        or "https://" in stripped
    )


def check(file, line, lineno, ctx, config):
    if ctx.get("in_code_block") or ctx.get("in_front_matter") or _is_markdown_exception(line):
        return []
    max_len = _configured_max(config)
    if max_len is None:
        return []

    width = display_width(line.rstrip("\n"))
    if width > max_len:
        return [LintIssue(file, lineno, NAME, f"line exceeds {max_len} columns ({width})")]
    return []
