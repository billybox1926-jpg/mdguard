"""File discovery helpers for mdguard."""

from __future__ import annotations

from pathlib import Path

_MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def discover_markdown_files(targets: list[str]) -> tuple[list[Path], list[Path], list[Path]]:
    """Resolve targets into markdown files.

    Returns a tuple of (markdown_files, missing_targets, empty_directories).
    """
    markdown_files: list[Path] = []
    missing_targets: list[Path] = []
    empty_directories: list[Path] = []

    for raw_target in targets:
        target = Path(raw_target)
        if not target.exists():
            missing_targets.append(target)
            continue

        if target.is_file():
            if target.suffix.lower() in _MARKDOWN_EXTENSIONS:
                markdown_files.append(target)
            continue

        if target.is_dir():
            found = sorted(
                p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in _MARKDOWN_EXTENSIONS
            )
            if found:
                markdown_files.extend(found)
            else:
                empty_directories.append(target)

    # Preserve stable ordering while deduplicating.
    unique_markdown_files = list(dict.fromkeys(markdown_files))
    return unique_markdown_files, missing_targets, empty_directories
