#!/usr/bin/env python3
"""Markdown Linter — Plugin-Based Rule Engine"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pkgutil
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# --- Display width -------------------------------------------------------
def display_width(text: str) -> int:
    """Return an approximate terminal column width using only the stdlib."""
    import unicodedata

    width = 0
    for char in text:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
    return width


@dataclass
class LintIssue:
    file: Path
    line: int
    rule: str
    message: str

    def __str__(self):
        return f"{self.file}:{self.line}: {self.message} [{self.rule}]"


# --- File Reader ---------------------------------------------------------
def read_file_text(path: Path) -> tuple[str | None, str | None]:
    """Read file content. Tries UTF-8, then UTF-16 (Windows echo fallback)."""
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


# --- Rule Loader ---------------------------------------------------------
def load_rules(rules_dir: Path) -> dict[str, Any]:
    rules = {}
    if not rules_dir.exists():
        return rules

    for m in pkgutil.iter_modules([str(rules_dir)]):
        if m.name.startswith("_"):
            continue
        path = rules_dir / f"{m.name}.py"
        try:
            spec = importlib.util.spec_from_file_location(m.name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "NAME") and hasattr(module, "check"):
                rules[module.NAME] = {
                    "check": module.check,
                    "default_enabled": getattr(module, "DEFAULT_ENABLED", True),
                    "fix": getattr(module, "fix", None),
                    "post_check": getattr(module, "post_check", None),
                }
        except Exception as e:
            print(f"Failed to load rule {m.name}: {e}", file=sys.stderr)
    return rules


# --- Cached regexes (shared across files) --------------------------------
_HEADING_RE = re.compile(r"^(#{1,6})\s*(.+?)\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")


def _get_line_ending(line: str) -> str:
    """Extract the line ending (\n, \r\n, or empty) from a line."""
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    if line.endswith("\r"):
        return "\r"
    return ""


def _validate_fix(original: str, fixed: str, rule_name: str) -> str:
    """Ensure a fix preserves the line ending. Warn and fall back if not."""
    orig_ending = _get_line_ending(original)
    fixed_ending = _get_line_ending(fixed)
    if orig_ending and not fixed_ending:
        print(
            f"⚠️  Rule '{rule_name}' fix stripped line ending. Preserving it.",
            file=sys.stderr,
        )
        return fixed + orig_ending
    if not orig_ending and fixed_ending:
        print(
            f"⚠️  Rule '{rule_name}' fix added line ending where none existed. Removing it.",
            file=sys.stderr,
        )
        return fixed.rstrip("\n\r")
    return fixed


# --- Process File --------------------------------------------------------
def process_file(
    path: Path, rules: dict, config: dict, fix: bool = False
) -> list[LintIssue]:
    issues: list[LintIssue] = []

    text, original_encoding = read_file_text(path)
    if text is None:
        return issues

    lines = text.splitlines(keepends=True)

    ctx = {
        "heading_re": _HEADING_RE,
        "link_re": _LINK_RE,
        "prev_level": 0,
        "seen_headings": {},
        "has_h1": False,
    }

    fixed_lines = lines[:]

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip("\n\r")

        for rule_name, rule in rules.items():
            if config.get(rule_name, rule["default_enabled"]):
                new_issues = rule["check"](path, stripped, i, ctx, config)
                issues.extend(new_issues)

                # Apply per-rule auto-fix if the rule provides one
                if fix and new_issues and rule.get("fix"):
                    raw_fixed = rule["fix"](fixed_lines[i - 1])
                    fixed_lines[i - 1] = _validate_fix(
                        fixed_lines[i - 1], raw_fixed, rule_name
                    )
                    # Re-evaluate stripped for subsequent rules on this line
                    stripped = fixed_lines[i - 1].rstrip("\n\r")

    # --- Post-pass: rules that need whole-file context --------------------
    for rule_name, rule in rules.items():
        if config.get(rule_name, rule["default_enabled"]) and rule.get("post_check"):
            new_issues = rule["post_check"](path, ctx, config)
            issues.extend(new_issues)

    # Write if changed
    if fix and fixed_lines != lines:
        path.write_text("".join(fixed_lines), encoding="utf-8")
        if original_encoding != "utf-8":
            print(
                f"💡 Converted {path} from {original_encoding.upper()} to UTF-8.",
                file=sys.stderr,
            )

    return issues


# --- Main ----------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Markdown Linter")
    parser.add_argument("files", nargs="*", help="Markdown files")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe issues")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode (enables all rules, max_length=100)",
    )
    parser.add_argument("--list-rules", action="store_true")
    parser.add_argument("--max-length", type=int, default=120)
    parser.add_argument(
        "--disable",
        action="append",
        default=[],
        help="Disable specific rules (can be used multiple times)",
    )
    parser.add_argument(
        "--enable",
        action="append",
        default=[],
        help="Enable specific rules (can be used multiple times)",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        help="JSON config file with a rules object for enabling/disabling rules",
    )
    args = parser.parse_args()

    # Make this module importable as 'markdown_lint' for rule plugins.
    if "markdown_lint" not in sys.modules:
        sys.modules["markdown_lint"] = sys.modules["__main__"]

    rules_dir = Path(__file__).parent / "rules"
    rules = load_rules(rules_dir)

    if args.list_rules:
        print("Available rules:")
        for name in sorted(rules.keys()):
            status = "enabled" if rules[name]["default_enabled"] else "disabled"
            print(f"  • {name} ({status})")
        return 0

    if not args.files:
        print("No files specified.", file=sys.stderr)
        return 1

    # Build config: start with global settings
    config = {"max_length": args.max_length}

    if args.rules:
        rules_config = json.loads(args.rules.read_text(encoding="utf-8"))
        configured_rules = rules_config.get("rules", {})
        if not isinstance(configured_rules, dict):
            print("rules config must contain an object at 'rules'", file=sys.stderr)
            return 2
        config.update(configured_rules)

    # Strict mode: lower max_length and enable all rules by default
    if args.strict:
        config["max_length"] = 100
        for name in rules:
            # Only set if not explicitly disabled
            if name not in args.disable:
                config[name] = True

    # Explicit --enable / --disable overrides everything
    for name in args.enable:
        config[name] = True
    for name in args.disable:
        config[name] = False

    all_issues = []
    unfixed_issues_global = []

    for f in args.files:
        p = Path(f)
        if not p.is_file():
            print(f"{p} not found", file=sys.stderr)
            continue

        issues = process_file(p, rules, config, fix=args.fix)
        all_issues.extend(issues)

        if issues:
            if args.fix:
                unfixed_issues = [
                    iss for iss in issues if not rules.get(iss.rule, {}).get("fix")
                ]
                fixed_count = len(issues) - len(unfixed_issues)

                if fixed_count:
                    print(
                        f"🔧 Fixed {fixed_count} auto-fixable issue(s) in {p}.",
                        file=sys.stderr,
                    )

                if unfixed_issues:
                    for issue in unfixed_issues:
                        print(issue, file=sys.stderr)
                    print(
                        f"⚠️  {len(unfixed_issues)} issue{'s' if len(unfixed_issues) != 1 else ''} remaining (not auto-fixable).",
                        file=sys.stderr,
                    )

                unfixed_issues_global.extend(unfixed_issues)
            else:
                for issue in issues:
                    print(issue, file=sys.stderr)
                print(
                    f"⚠️  {len(issues)} issue{'s' if len(issues) != 1 else ''} found.",
                    file=sys.stderr,
                )
                unfixed_issues_global.extend(issues)
        else:
            print(f"✅ No issues found in {p}.", file=sys.stderr)

    # Return 0 if all issues were fixed, 1 if unfixed issues remain
    return 1 if unfixed_issues_global else 0


if __name__ == "__main__":
    sys.exit(main())
