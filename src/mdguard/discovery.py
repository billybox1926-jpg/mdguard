"""File discovery helpers for mdguard."""

from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path
from typing import Optional

_MARKDOWN_EXTENSIONS = {".md", ".markdown"}
_IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "build",
    "dist",
    ".eggs",
}


def _normalize_pattern(pattern: str) -> str:
    return pattern.replace("\\", "/").strip("/")


def _is_excluded(relative_path: Path, exclude_patterns: list[str]) -> bool:
    path_text = relative_path.as_posix().strip("/")
    for raw_pattern in exclude_patterns:
        pattern = _normalize_pattern(raw_pattern)
        if not pattern:
            continue
        if fnmatchcase(path_text, pattern):
            return True
        if pattern.endswith("/**") and path_text.startswith(pattern[:-3].rstrip("/") + "/"):
            return True
        if not any(char in pattern for char in "*?[") and (
            path_text == pattern or path_text.startswith(pattern + "/")
        ):
            return True
    return False


def discover_markdown_files(
    targets: list[str],
    exclude_patterns: Optional[list[str]] = None,
) -> tuple[list[Path], list[Path], list[Path]]:
    """Resolve targets into markdown files.

    Returns a tuple of (markdown_files, missing_targets, empty_directories).
    """
    exclude_patterns = exclude_patterns or []
    markdown_files: list[Path] = []
    missing_targets: list[Path] = []
    empty_directories: list[Path] = []

    for raw_target in targets:
        target = Path(raw_target)
        if not target.exists():
            missing_targets.append(target)
            continue

        if target.is_file():
            if target.suffix.lower() in _MARKDOWN_EXTENSIONS and not _is_excluded(Path(target.name), exclude_patterns):
                markdown_files.append(target)
            continue

        if target.is_dir():
            found = sorted(
                p
                for p in target.rglob("*")
                if p.is_file()
                and p.suffix.lower() in _MARKDOWN_EXTENSIONS
                and not any(part in _IGNORED_DIRECTORIES for part in p.relative_to(target).parts[:-1])
                and not _is_excluded(p.relative_to(target), exclude_patterns)
            )
            if found:
                markdown_files.extend(found)
            else:
                empty_directories.append(target)

    # Preserve stable ordering while deduplicating.
    unique_markdown_files = list(dict.fromkeys(markdown_files))
    return unique_markdown_files, missing_targets, empty_directories
