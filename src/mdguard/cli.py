"""Command-line interface entry points for mdguard."""

from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from json import JSONDecodeError
from pathlib import Path
from typing import Optional

from mdguard.annotations import render_github_annotations
from mdguard.baseline import filter_baselined, load_baseline, write_baseline
from mdguard.config import apply_tool_config, load_pyproject_config
from mdguard.core import load_rules, process_file
from mdguard.discovery import discover_markdown_files
from mdguard.models import RunResult
from mdguard.output import build_json_report, build_summary


def _format_valid_rule_names(rules: dict[str, object]) -> str:
    return ", ".join(sorted(rules))


def _unknown_rule_message(source: str, rule_name: str, rules: dict[str, object]) -> str:
    return f"Unknown rule '{rule_name}' in {source}. Valid rule names: {_format_valid_rule_names(rules)}"


def _validate_rule_names(selected_rules: list[str], source: str, rules: dict[str, object]) -> Optional[str]:
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
        return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    except Exception as exc:
        print(f"⚠️  Could not read .mdguardignore: {exc}", file=sys.stderr)
        return []


def _read_stdin(stdin_filename: str) -> Path:
    synthetic = Path(stdin_filename)
    text = sys.stdin.read()
    temp = Path.cwd() / ".mdguard-stdin.md"
    temp.write_text(text, encoding="utf-8", newline="")
    return temp if stdin_filename == "<stdin>" else synthetic


def _package_version() -> str:
    try:
        return version("mdguard")
    except PackageNotFoundError:
        return "0+unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown Linter")
    parser.add_argument("files", nargs="*", help="Markdown files, directories, or '-' for stdin")
    parser.add_argument("--version", action="version", version=f"mdguard {_package_version()}")
    parser.add_argument("--fix", action="store_true", help="Auto-fix safe issues")
    parser.add_argument("--strict", action="store_true", help="Strict mode (enables all rules, max_length=100)")
    parser.add_argument("--list-rules", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="Show verbose rule metadata with --list-rules")
    parser.add_argument("--max-length", type=int, default=None)
    parser.add_argument("--disable", action="append", default=[], help="Disable specific rules (can be used multiple times)")
    parser.add_argument("--enable", action="append", default=[], help="Enable specific rules (can be used multiple times)")
    parser.add_argument("--rules", type=Path, help="JSON config file with a rules object for enabling/disabling rules")
    parser.add_argument("--exclude", action="append", default=[], help="Exclude files or directories using slash-separated glob patterns")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit lint results as JSON")
    parser.add_argument("--format", choices=["human", "json", "github"], default="human")
    parser.add_argument("--stdin-filename", default="<stdin>", help="Display path to use when reading '-' from stdin")
    parser.add_argument("--baseline", type=Path, help="Suppress issues already present in baseline JSON")
    parser.add_argument("--write-baseline", type=Path, help="Write current issues to baseline JSON and exit 0")
    args = parser.parse_args()

    rules = load_rules()
    if args.list_rules:
        print("Available rules:")
        for name in sorted(rules):
            status = "enabled" if rules[name]["default_enabled"] else "disabled"
            if args.verbose:
                fixable = "fixable" if rules[name].get("fixable") else "manual"
                print(f"  • {name} ({status}, {fixable}) - {rules[name].get('description', '')}")
            else:
                print(f"  • {name} ({status})")
        return 0

    if not args.files:
        print("No files specified.", file=sys.stderr)
        return 1

    config: dict[str, object] = {"max_length": 120}
    tool_config, _, config_error = load_pyproject_config(Path.cwd())
    if config_error:
        print(config_error, file=sys.stderr)
        return 2
    pyproject_excludes: list[str] = []
    if tool_config:
        config, pyproject_excludes = apply_tool_config(config, tool_config)
    if args.max_length is not None:
        config["max_length"] = args.max_length

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

    for selected, source in ((args.enable, "--enable"), (args.disable, "--disable")):
        unknown = _validate_rule_names(selected, source, rules)
        if unknown:
            print(unknown, file=sys.stderr)
            return 2
    for name in args.enable:
        config[name] = True
    for name in args.disable:
        config[name] = False

    targets = list(args.files)
    stdin_temp: Optional[Path] = None
    if "-" in targets:
        if args.fix:
            print("--fix is not supported for stdin", file=sys.stderr)
            return 2
        stdin_temp = Path.cwd() / ".mdguard-stdin.md"
        stdin_temp.write_text(sys.stdin.read(), encoding="utf-8", newline="")
        targets = [str(stdin_temp) if t == "-" else t for t in targets]

    markdown_files, missing_targets, empty_directories = discover_markdown_files(
        targets,
        exclude_patterns=_load_ignore_file() + pyproject_excludes + args.exclude,
    )
    if stdin_temp and args.stdin_filename != "<stdin>":
        display_map = {stdin_temp: Path(args.stdin_filename)}
    else:
        display_map = {stdin_temp: Path("<stdin>")} if stdin_temp else {}

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

    result = RunResult(files_checked=[display_map.get(p, p) for p in markdown_files], config=config)
    json_file_issues = []
    all_original_issues = []
    for path in markdown_files:
        issues = process_file(path, rules, config, fix=args.fix)
        display_path = display_map.get(path, path)
        for issue in issues:
            issue.file = display_path
        all_original_issues.extend(issues)
        if args.fix:
            fixed = [iss for iss in issues if rules.get(iss.rule, {}).get("fix")]
            unfixed = [iss for iss in issues if not rules.get(iss.rule, {}).get("fix")]
            result.fixed_issue_count += len(fixed)
            issues = unfixed
        result.issues.extend(issues)
        json_file_issues.append((display_path, issues))

    if args.baseline and args.baseline.exists():
        result.issues = filter_baselined(result.issues, load_baseline(args.baseline))
        json_file_issues = result.issues_by_file()
    if args.write_baseline:
        write_baseline(args.write_baseline, all_original_issues)
        print(f"Wrote baseline with {len(all_original_issues)} issue(s) to {args.write_baseline}", file=sys.stderr)
        return 0

    output_format = "json" if args.json_output else args.format
    if output_format == "json":
        print(json.dumps(build_json_report(json_file_issues, result=result)))
    elif output_format == "github":
        annotations = render_github_annotations(result.issues)
        if annotations:
            print(annotations)
    else:
        for path, issues in json_file_issues:
            if issues:
                for issue in issues:
                    print(issue, file=sys.stderr)
            else:
                print(f"✅ No issues found in {path}.", file=sys.stderr)
        summary = build_summary(result)
        if result.fixed_issue_count:
            print(f"🔧 Fixed {result.fixed_issue_count} auto-fixable issue(s).", file=sys.stderr)
        if result.issues:
            print(summary, file=sys.stderr)

    if stdin_temp and stdin_temp.exists():
        stdin_temp.unlink()
    return 1 if result.issues else 0


if __name__ == "__main__":
    sys.exit(main())
