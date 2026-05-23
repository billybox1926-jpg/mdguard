"""Command-line interface entry points for mdguard."""

from __future__ import annotations

import argparse
import json
import sys
from json import JSONDecodeError
from pathlib import Path

from mdguard.core import load_rules, process_file
from mdguard.discovery import discover_markdown_files
from mdguard.output import build_json_report


def _format_valid_rule_names(rules: dict[str, object]) -> str:
    return ", ".join(sorted(rules))


def _unknown_rule_message(source: str, rule_name: str, rules: dict[str, object]) -> str:
    return (
        f"Unknown rule '{rule_name}' in {source}. "
        f"Valid rule names: {_format_valid_rule_names(rules)}"
    )


def _validate_rule_names(selected_rules: list[str], source: str, rules: dict[str, object]) -> str | None:
    for name in selected_rules:
        if name not in rules:
            return _unknown_rule_message(source, name, rules)
    return None


def _load_ignore_file() -> list[str]:
    ignore_file = Path(".mdguardignore")
    if not ignore_file.exists():
        return []
    try:
        lines = ignore_file.read_text(encoding="utf-8").splitlines()
        return [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]
    except Exception as exc:
        print(f"⚠️  Could not read .mdguardignore: {exc}", file=sys.stderr)
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown Linter")
    parser.add_argument("files", nargs="*", help="Markdown files")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe issues")
    parser.add_argument("--strict", action="store_true", help="Strict mode (enables all rules, max_length=100)")
    parser.add_argument("--list-rules", action="store_true")
    parser.add_argument("--max-length", type=int, default=120)
    parser.add_argument("--disable", action="append", default=[], help="Disable specific rules (can be used multiple times)")
    parser.add_argument("--enable", action="append", default=[], help="Enable specific rules (can be used multiple times)")
    parser.add_argument("--rules", type=Path, help="JSON config file with a rules object for enabling/disabling rules")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude files or directories using slash-separated glob patterns (can be used multiple times)",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit lint results as JSON")
    args = parser.parse_args()

    rules = load_rules()
    if args.list_rules:
        print("Available rules:")
        for name in sorted(rules):
            status = "enabled" if rules[name]["default_enabled"] else "disabled"
            print(f"  • {name} ({status})")
        return 0

    if not args.files:
        print("No files specified.", file=sys.stderr)
        return 1

    config: dict[str, object] = {"max_length": args.max_length}
    if args.rules:
        try:
            rules_config = json.loads(args.rules.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"rules config file not found: {args.rules}", file=sys.stderr)
            return 2
        except JSONDecodeError as exc:
            print(f"invalid JSON in rules config {args.rules}: {exc.msg}", file=sys.stderr)
            return 2

        if not isinstance(rules_config, dict):
            print("rules config must contain a JSON object", file=sys.stderr)
            return 2

        configured_rules = rules_config.get("rules", {})
        if not isinstance(configured_rules, dict):
            print("rules config must contain an object at 'rules'", file=sys.stderr)
            return 2

        unknown_from_config = _validate_rule_names(list(configured_rules), f"--rules {args.rules}", rules)
        if unknown_from_config:
            print(unknown_from_config, file=sys.stderr)
            return 2

        config.update(configured_rules)

    if args.strict:
        config["max_length"] = 100
        for name in rules:
            if name not in args.disable:
                config[name] = True

    unknown_enabled = _validate_rule_names(args.enable, "--enable", rules)
    if unknown_enabled:
        print(unknown_enabled, file=sys.stderr)
        return 2

    unknown_disabled = _validate_rule_names(args.disable, "--disable", rules)
    if unknown_disabled:
        print(unknown_disabled, file=sys.stderr)
        return 2

    for name in args.enable:
        config[name] = True
    for name in args.disable:
        config[name] = False

    markdown_files, missing_targets, empty_directories = discover_markdown_files(
        args.files,
        exclude_patterns=_load_ignore_file() + args.exclude,
    )

    if missing_targets:
        for target in missing_targets:
            print(f"{target} not found", file=sys.stderr)
        return 1

    if empty_directories:
        for directory in empty_directories:
            print(f"No Markdown files found under directory: {directory}", file=sys.stderr)
        return 1

    if not markdown_files:
        print("No Markdown files found in provided targets.", file=sys.stderr)
        return 1

    unfixed_issues_global = []
    json_file_issues = []
    for path in markdown_files:
        issues = process_file(path, rules, config, fix=args.fix)
        if issues:
            if args.fix:
                unfixed_issues = [iss for iss in issues if not rules.get(iss.rule, {}).get("fix")]
                fixed_count = len(issues) - len(unfixed_issues)
                if fixed_count and not args.json_output:
                    print(f"🔧 Fixed {fixed_count} auto-fixable issue(s) in {path}.", file=sys.stderr)
                if unfixed_issues:
                    if not args.json_output:
                        for issue in unfixed_issues:
                            print(issue, file=sys.stderr)
                    n = len(unfixed_issues)
                    if not args.json_output:
                        print(f"⚠️  {n} issue{'s' if n != 1 else ''} remaining (not auto-fixable).", file=sys.stderr)
                unfixed_issues_global.extend(unfixed_issues)
                json_file_issues.append((path, unfixed_issues))
            else:
                if not args.json_output:
                    for issue in issues:
                        print(issue, file=sys.stderr)
                n = len(issues)
                if not args.json_output:
                    print(f"⚠️  {n} issue{'s' if n != 1 else ''} found.", file=sys.stderr)
                unfixed_issues_global.extend(issues)
                json_file_issues.append((path, issues))
        else:
            if not args.json_output:
                print(f"✅ No issues found in {path}.", file=sys.stderr)
            json_file_issues.append((path, []))

    if args.json_output:
        print(json.dumps(build_json_report(json_file_issues)))

    return 1 if unfixed_issues_global else 0


if __name__ == "__main__":
    sys.exit(main())
