"""Structured mdguard result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mdguard.core import LintIssue


@dataclass
class SkippedFile:
    path: Path
    reason: str


@dataclass
class RunResult:
    files_checked: list[Path] = field(default_factory=list)
    skipped_files: list[SkippedFile] = field(default_factory=list)
    issues: list[LintIssue] = field(default_factory=list)
    fixed_issue_count: int = 0
    elapsed_seconds: float = 0.0
    config: dict[str, object] = field(default_factory=dict)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def issues_by_file(self) -> list[tuple[Path, list[LintIssue]]]:
        grouped: dict[Path, list[LintIssue]] = {path: [] for path in self.files_checked}
        for issue in self.issues:
            grouped.setdefault(issue.file, []).append(issue)
        return list(grouped.items())
