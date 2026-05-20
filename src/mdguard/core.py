"""Core orchestration primitives for mdguard."""

from __future__ import annotations

import importlib
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LintIssue:
    file: Path
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.message} [{self.rule}]"


_HEADING_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")


def display_width(text: str) -> int:
    """Return an approximate terminal column width using only stdlib."""
    width = 0
    for char in text:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
    return width


def read_file_text(path: Path) -> tuple[str | None, str | None]:
    """Read file text as UTF-8(-sig) then UTF-16 fallback."""
    try:
        return path.read_text(encoding="utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-16"), "utf-16"
        except UnicodeDecodeError:
            print(
                f"⚠️ Skipping {path}: could not decode as UTF-8 or UTF-16.",
                file=sys.stderr,
            )
            return None, None


def load_rules() -> dict[str, Any]:
    """Load built-in rules from the package rule namespace."""
    rules: dict[str, Any] = {}
    for module_name in (
        "duplicate_headings",
        "empty_link",
        "heading_jump",
        "line_length",
        "missing_h1",
        "trailing_whitespace",
    ):
        fqmn = f"mdguard.rules.{module_name}"
        try:
            module = importlib.import_module(fqmn)
            if hasattr(module, "NAME") and hasattr(module, "check"):
                rules[module.NAME] = {
                    "check": module.check,
                    "default_enabled": getattr(module, "DEFAULT_ENABLED", True),
                    "fix": getattr(module, "fix", None),
                    "post_check": getattr(module, "post_check", None),
                }
        except Exception as exc:
            print(f"Failed to load rule {fqmn}: {exc}", file=sys.stderr)
    return rules


def _get_line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    if line.endswith("\r"):
        return "\r"
    return ""


def _validate_fix(original: str, fixed: str, rule_name: str) -> str:
    orig_ending = _get_line_ending(original)
    fixed_ending = _get_line_ending(fixed)
    if orig_ending and not fixed_ending:
        print(f"⚠️  Rule '{rule_name}' fix stripped line ending. Preserving it.", file=sys.stderr)
        return fixed + orig_ending
    if not orig_ending and fixed_ending:
        print(
            f"⚠️  Rule '{rule_name}' fix added line ending where none existed. Removing it.",
            file=sys.stderr,
        )
        return fixed.rstrip("\n\r")
    return fixed


def process_file(path: Path, rules: dict[str, Any], config: dict[str, Any], fix: bool = False) -> list[LintIssue]:
    issues: list[LintIssue] = []
    text, original_encoding = read_file_text(path)
    if text is None:
        return issues

    lines = text.splitlines(keepends=True)
    fixed_lines = lines[:]
    ctx: dict[str, Any] = {
        "heading_re": _HEADING_RE,
        "link_re": _LINK_RE,
        "prev_level": 0,
        "seen_headings": {},
        "has_h1": False,
    }

    for i, _ in enumerate(lines, 1):
        stripped = fixed_lines[i - 1].rstrip("\n\r")
        for rule_name, rule in rules.items():
            if config.get(rule_name, rule["default_enabled"]):
                new_issues = rule["check"](path, stripped, i, ctx, config)
                issues.extend(new_issues)
                if fix and new_issues and rule.get("fix"):
                    raw_fixed = rule["fix"](fixed_lines[i - 1])
                    fixed_lines[i - 1] = _validate_fix(fixed_lines[i - 1], raw_fixed, rule_name)
                    stripped = fixed_lines[i - 1].rstrip("\n\r")

    for rule_name, rule in rules.items():
        if config.get(rule_name, rule["default_enabled"]) and rule.get("post_check"):
            issues.extend(rule["post_check"](path, ctx, config))

    if fix and fixed_lines != lines:
        path.write_text("".join(fixed_lines), encoding="utf-8")
        if original_encoding != "utf-8":
            print(f"💡 Converted {path} from {original_encoding.upper()} to UTF-8.", file=sys.stderr)

    return issues
