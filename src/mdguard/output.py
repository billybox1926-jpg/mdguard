"""Output formatting helpers for mdguard."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import TypedDict

from mdguard.core import LintIssue


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


class JsonLintReport(TypedDict):
    schema_version: int
    tool: JsonTool
    files: list[JsonFileReport]
    issue_count: int


def _version() -> str:
    try:
        return metadata.version("mdguard")
    except metadata.PackageNotFoundError:
        return "0+unknown"


def build_json_report(file_issues: list[tuple[Path, list[LintIssue]]]) -> JsonLintReport:
    files: list[JsonFileReport] = []
    issue_count = 0
    for path, issues in file_issues:
        serialized_issues: list[JsonIssue] = []
        for issue in issues:
            serialized_issues.append(
                {
                    "line": issue.line,
                    "rule": issue.rule,
                    "message": issue.message,
                }
            )
        files.append({"path": str(path), "issues": serialized_issues})
        issue_count += len(serialized_issues)
    return {
        "schema_version": 1,
        "tool": {"name": "mdguard", "version": _version()},
        "files": files,
        "issue_count": issue_count,
    }
