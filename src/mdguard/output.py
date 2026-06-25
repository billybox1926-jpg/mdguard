"""Output formatting helpers for mdguard."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import Optional, TypedDict

from mdguard.core import LintIssue
from mdguard.models import RunResult


class JsonTool(TypedDict):
    name: str
    version: str


class JsonIssue(TypedDict):
    line: int
    rule: str
    message: str


class JsonFileReport(TypedDict):
    path: str
    issues: list[JsonIssue]


class JsonLintReport(TypedDict, total=False):
    schema_version: int
    tool: JsonTool
    files: list[JsonFileReport]
    issue_count: int
    fixed_issue_count: int
    files_checked: int
    skipped_files: list[dict[str, str]]
    elapsed_seconds: float
    summary: dict[str, dict[str, int]]


def _version() -> str:
    try:
        return metadata.version("mdguard")
    except metadata.PackageNotFoundError:
        return "0+unknown"


def build_summary(result: RunResult) -> str:
    by_rule: dict[str, int] = {}
    by_file: dict[str, int] = {}
    for issue in result.issues:
        by_rule[issue.rule] = by_rule.get(issue.rule, 0) + 1
        by_file[str(issue.file)] = by_file.get(str(issue.file), 0) + 1
    return (
        f"⚠️  {len(result.issues)} issue{'s' if len(result.issues) != 1 else ''} remaining; "
        f"{result.fixed_issue_count} fixed; by_rule={by_rule}; by_file={by_file}"
    )


def build_json_report(
    file_issues: list[tuple[Path, list[LintIssue]]], result: Optional[RunResult] = None
) -> JsonLintReport:
    files: list[JsonFileReport] = []
    issue_count = 0
    by_rule: dict[str, int] = {}
    by_file: dict[str, int] = {}
    for path, issues in file_issues:
        serialized_issues: list[JsonIssue] = []
        for issue in issues:
            serialized_issues.append(
                {"line": issue.line, "rule": issue.rule, "message": issue.message}
            )
            by_rule[issue.rule] = by_rule.get(issue.rule, 0) + 1
        files.append({"path": str(path), "issues": serialized_issues})
        issue_count += len(serialized_issues)
        by_file[str(path)] = len(serialized_issues)
    report: JsonLintReport = {
        "schema_version": 1,
        "tool": {"name": "mdguard", "version": _version()},
        "files": files,
        "issue_count": issue_count,
        "summary": {"by_rule": by_rule, "by_file": by_file},
    }
    if result is not None:
        report["fixed_issue_count"] = result.fixed_issue_count
        report["files_checked"] = len(result.files_checked)
        report["skipped_files"] = [
            {"path": str(skipped.path), "reason": skipped.reason}
            for skipped in result.skipped_files
        ]
        report["elapsed_seconds"] = round(result.elapsed_seconds, 6)
    return report
