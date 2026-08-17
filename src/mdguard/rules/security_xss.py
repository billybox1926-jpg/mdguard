"""Security rule: detect potential XSS vectors in Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from mdguard.core import LintIssue

NAME = "security-xss"
DEFAULT_ENABLED = False
DESCRIPTION = (
    "Detect script tags, javascript URIs, event handlers, and iframe/embed injection"
)
TAGS = ("security", "xss")
ALIASES = ()

_SCRIPT_TAG_RE = re.compile(r"<script[\s>]", re.IGNORECASE)
_JAVASCRIPT_URI_RE = re.compile(r"javascript\s*:", re.IGNORECASE)
_DATA_URI_HTML_RE = re.compile(r"data\s*:\s*text/html", re.IGNORECASE)
_EVENT_HANDLER_RE = re.compile(r"\bon\w+\s*=", re.IGNORECASE)
_IFRAME_RE = re.compile(r"<iframe[\s>]", re.IGNORECASE)
_EMBED_RE = re.compile(r"<embed[\s>]", re.IGNORECASE)
_OBJECT_RE = re.compile(r"<object[\s>]", re.IGNORECASE)
_FORM_ACTION_RE = re.compile(
    r'<form[^>]*\s+action\s*=\s*["\']?\s*javascript:', re.IGNORECASE
)


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> list[LintIssue]:
    """Flag lines containing potential XSS vectors."""
    if ctx.get("in_code_block") or ctx.get("in_front_matter"):
        return []

    issues: list[LintIssue] = []

    if _SCRIPT_TAG_RE.search(line):
        issues.append(
            LintIssue(file, lineno, NAME, "potential XSS: <script> tag detected")
        )

    if _JAVASCRIPT_URI_RE.search(line):
        issues.append(
            LintIssue(file, lineno, NAME, "dangerous URI scheme: javascript:")
        )

    if _DATA_URI_HTML_RE.search(line):
        issues.append(
            LintIssue(file, lineno, NAME, "potentially unsafe data:text/html URI")
        )

    if _EVENT_HANDLER_RE.search(line):
        issues.append(
            LintIssue(
                file, lineno, NAME, "HTML event handler attribute detected (on*=)"
            )
        )

    if _IFRAME_RE.search(line):
        issues.append(LintIssue(file, lineno, NAME, "iframe embed tag detected"))

    if _EMBED_RE.search(line):
        issues.append(LintIssue(file, lineno, NAME, "embed tag detected"))

    if _OBJECT_RE.search(line):
        issues.append(LintIssue(file, lineno, NAME, "object tag detected"))

    if _FORM_ACTION_RE.search(line):
        issues.append(
            LintIssue(file, lineno, NAME, "form with javascript: action detected")
        )

    return issues
