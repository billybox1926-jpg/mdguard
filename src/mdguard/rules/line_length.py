"""Markdown lint rule for line length."""

from __future__ import annotations

from mdguard.core import LintIssue, display_width

NAME = "line-length"
DEFAULT_ENABLED = True


def _configured_max(config: dict) -> int | None:
    rule = config.get(NAME)
    if rule is False:
        return None
    if isinstance(rule, dict):
        return rule.get("max", config.get("max_length", 120))
    return config.get("max_length", 120)


def check(file, line, lineno, ctx, config):
    if ctx.get("in_code_block"):
        return []
    max_len = _configured_max(config)
    if max_len is None:
        return []

    width = display_width(line.rstrip("\n"))
    if width > max_len:
        return [LintIssue(file, lineno, NAME, f"line exceeds {max_len} columns ({width})")]
    return []
