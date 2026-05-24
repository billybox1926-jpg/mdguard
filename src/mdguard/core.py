"""Core orchestration primitives for mdguard."""

from __future__ import annotations

import importlib
import inspect
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple


@dataclass
class LintIssue:
    file: Path
    line: int
    rule: str
    message: str
    fixed: bool = False

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.message} [{self.rule}]"


_HEADING_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")
_CODE_FENCE_RE = re.compile(r"^(?:`{3,}|~{3,})")


def display_width(text: str) -> int:
    """Return an approximate terminal column width using only stdlib."""
    width = 0
    for char in text:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
    return width


def read_file_text(path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Read file text as UTF-8(-sig) then UTF-16 fallback without newline conversion."""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return f.read(), "utf-8"
    except UnicodeDecodeError:
        try:
            with path.open("r", encoding="utf-16", newline="") as f:
                return f.read(), "utf-16"
        except UnicodeDecodeError:
            print(
                f"⚠️ Skipping {path}: could not decode as UTF-8 or UTF-16.",
                file=sys.stderr,
            )
            return None, None


def load_rules() -> dict[str, Any]:
    """Load built-in rules from the package rule namespace."""
    builtins = (
        "duplicate_headings",
        "empty_link",
        "heading_jump",
        "line_length",
        "missing_h1",
        "trailing_whitespace",
        "final_newline",
        "internal_anchor",
    )
    rules: dict[str, Any] = {}
    import_errors: list[str] = []
    for module_name in builtins:
        fqmn = f"mdguard.rules.{module_name}"
        try:
            module = importlib.import_module(fqmn)
            if hasattr(module, "NAME") and hasattr(module, "check"):
                rules[module.NAME] = {
                    "check": module.check,
                    "default_enabled": getattr(module, "DEFAULT_ENABLED", True),
                    "fix": getattr(module, "fix", None),
                    "post_check": getattr(module, "post_check", None),
                    "allow_add_line_ending": getattr(
                        module, "ALLOW_ADD_LINE_ENDING", False
                    ),
                    "description": getattr(module, "DESCRIPTION", ""),
                    "tags": getattr(module, "TAGS", ()),
                    "aliases": getattr(module, "ALIASES", ()),
                    "fixable": hasattr(module, "fix"),
                }
            else:
                import_errors.append(f"{fqmn} missing NAME/check")
        except Exception as exc:
            import_errors.append(f"{fqmn}: {exc}")

    if import_errors:
        details = "; ".join(import_errors)
        raise RuntimeError(f"Failed to load built-in rule(s): {details}")

    if "line-length" not in rules:
        raise RuntimeError("Failed to load built-in rule: line-length")
    return rules


def _get_line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    if line.endswith("\r"):
        return "\r"
    return ""


def _validate_fix(
    original: str, fixed: str, rule_name: str, allow_add_line_ending: bool = False
) -> str:
    orig_ending = _get_line_ending(original)
    fixed_ending = _get_line_ending(fixed)
    if orig_ending and not fixed_ending:
        print(
            f"⚠️  Rule '{rule_name}' fix stripped line ending. Preserving it.",
            file=sys.stderr,
        )
        return fixed + orig_ending
    if not allow_add_line_ending and not orig_ending and fixed_ending:
        print(
            f"⚠️  Rule '{rule_name}' fix added line ending where none existed. Removing it.",
            file=sys.stderr,
        )
        return fixed.rstrip("\n\r")
    return fixed


def process_file(
    path: Path, rules: dict[str, Any], config: dict[str, Any], fix: bool = False
) -> list[LintIssue]:
    issues: list[LintIssue] = []
    text, original_encoding = read_file_text(path)
    if text is None:
        return issues

    lines = text.splitlines(keepends=True)
    fixed_lines = lines[:]
    ctx: dict[str, Any] = {
        "heading_re": _HEADING_RE,
        "link_re": _LINK_RE,
        "code_fence_re": _CODE_FENCE_RE,
        "prev_level": 0,
        "seen_headings": {},
        "has_h1": False,
        "in_code_block": False,
        "in_front_matter": False,
        "front_matter_done": False,
        "headings": [],
        "lines": fixed_lines,
    }

    for i, _ in enumerate(lines, 1):
        stripped = fixed_lines[i - 1].rstrip("\n\r")
        if i == 1 and stripped in {"---", "+++"}:
            ctx["in_front_matter"] = stripped
        elif ctx.get("in_front_matter") and stripped == ctx["in_front_matter"]:
            ctx["in_front_matter"] = False
            ctx["front_matter_done"] = True

        is_fence = bool(_CODE_FENCE_RE.match(stripped))
        if is_fence:
            ctx["in_code_block"] = not ctx["in_code_block"]

        suppressed_all = bool(ctx.get("suppressed_all"))
        disabled_specific = set(ctx.get("suppressed_rules", set()))
        next_specific = set(ctx.pop("suppress_next_rules", set()))
        if "mdguard-enable" in stripped:
            ctx["suppressed_all"] = False
            ctx["suppressed_rules"] = set()
            suppressed_all = False
            disabled_specific = set()
        if (
            "mdguard-disable" in stripped
            and "next-line" not in stripped
            and "disable-line" not in stripped
        ):
            tokens = stripped.replace("-->", "").split()
            rules_to_disable = [
                t for t in tokens if t not in {"<!--", "mdguard-disable"}
            ]
            if rules_to_disable:
                ctx.setdefault("suppressed_rules", set()).update(rules_to_disable)
            else:
                ctx["suppressed_all"] = True
        same_line_rules: set[str] = set()
        if "mdguard-disable-line" in stripped:
            tokens = stripped.replace("-->", "").split()
            same_line_rules = {
                t for t in tokens if t not in {"<!--", "mdguard-disable-line"}
            }
            if not same_line_rules:
                suppressed_all = True
        if "mdguard-disable-next-line" in stripped:
            tokens = stripped.replace("-->", "").split()
            rules_next = {
                t for t in tokens if t not in {"<!--", "mdguard-disable-next-line"}
            }
            ctx["suppress_next_rules"] = rules_next or {"*"}

        for rule_name, rule in rules.items():
            if (
                suppressed_all
                or "*" in next_specific
                or rule_name in disabled_specific
                or rule_name in next_specific
                or rule_name in same_line_rules
            ):
                continue
            if config.get(rule_name, rule["default_enabled"]):
                new_issues = rule["check"](path, stripped, i, ctx, config)
                issues.extend(new_issues)
                if fix and new_issues and rule.get("fix"):
                    fix_fn = rule["fix"]
                    params = inspect.signature(fix_fn).parameters
                    if len(params) >= 2:
                        raw_fixed = fix_fn(fixed_lines[i - 1], ctx)
                    else:
                        raw_fixed = fix_fn(fixed_lines[i - 1])
                    fixed_lines[i - 1] = _validate_fix(
                        fixed_lines[i - 1],
                        raw_fixed,
                        rule_name,
                        allow_add_line_ending=rule.get("allow_add_line_ending", False),
                    )
                    stripped = fixed_lines[i - 1].rstrip("\n\r")

    for rule_name, rule in rules.items():
        if config.get(rule_name, rule["default_enabled"]) and rule.get("post_check"):
            issues.extend(rule["post_check"](path, ctx, config))

    if fix and fixed_lines != lines:
        if original_encoding not in {"utf-8", "utf-16"}:
            print(
                f"⚠️ Skipping autofix for {path}: unsupported write encoding {original_encoding!r}.",
                file=sys.stderr,
            )
            return issues

        with path.open("w", encoding=original_encoding, newline="") as f:
            f.write("".join(fixed_lines))

    return issues
