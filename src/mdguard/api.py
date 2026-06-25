"""Public API for embedding mdguard."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Union

from mdguard.core import load_rules, process_file
from mdguard.discovery import discover_markdown_files
from mdguard.models import RunResult, SkippedFile


def lint_paths(
    paths: Iterable[Union[str, Path]],
    *,
    config: Optional[dict[str, object]] = None,
    fix: bool = False,
    exclude_patterns: Optional[list[str]] = None,
) -> RunResult:
    rules = load_rules()
    markdown_files, missing_targets, empty_dirs = discover_markdown_files(
        [str(path) for path in paths], exclude_patterns=exclude_patterns or []
    )
    result = RunResult(files_checked=markdown_files, config=dict(config or {}))
    for target in missing_targets:
        result.skipped_files.append(SkippedFile(target, "missing"))
    for target in empty_dirs:
        result.skipped_files.append(SkippedFile(target, "no-markdown-files"))
    for path in markdown_files:
        issues = process_file(path, rules, dict(config or {}), fix=fix)
        if fix:
            fixed = [issue for issue in issues if rules.get(issue.rule, {}).get("fix")]
            result.fixed_issue_count += len(fixed)
            issues = [
                issue for issue in issues if not rules.get(issue.rule, {}).get("fix")
            ]
        result.issues.extend(issues)
    return result
