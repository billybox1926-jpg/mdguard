"""Validate same-file Markdown heading anchors."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from mdguard.core import LintIssue

NAME = "internal-anchor"
DEFAULT_ENABLED = True
DESCRIPTION = "Validate links to same-file heading anchors."
TAGS = ("links", "headings")
ALIASES = ("MD051",)

_LINK_TARGET_RE = re.compile(r"\[[^\]]+\]\((#[^)]+|[^)#\s]+\.md#[^)]+)\)")


def github_slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).strip().lower()
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug


def _links(line: str) -> list[str]:
    anchors = []
    for target in _LINK_TARGET_RE.findall(line):
        if "#" in target:
            anchors.append(target.rsplit("#", 1)[1].strip())
    return anchors


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> list[LintIssue]:
    if ctx.get("in_code_block") or ctx.get("in_front_matter"):
        return []
    match = ctx["heading_re"].match(line)
    if match:
        slug = github_slug(match.group(2))
        counts = ctx.setdefault("anchor_counts", {})
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        ctx.setdefault("anchors", set()).add(slug if count == 0 else f"{slug}-{count}")
    for anchor in _links(line):
        ctx.setdefault("anchor_refs", []).append((lineno, anchor))
    return []


def post_check(file: Path, ctx: dict, config: dict) -> list[LintIssue]:
    anchors = ctx.get("anchors", set())
    issues = []
    for lineno, anchor in ctx.get("anchor_refs", []):
        if anchor and anchor not in anchors:
            issues.append(
                LintIssue(
                    file, lineno, NAME, f"internal heading anchor not found: #{anchor}"
                )
            )
    return issues
