"""Security rule: validate URL schemes in Markdown links."""

from __future__ import annotations

import re
from pathlib import Path

from mdguard.core import LintIssue

NAME = "security-urls"
DEFAULT_ENABLED = False
DESCRIPTION = "Flag dangerous or suspicious URL schemes in Markdown links"
TAGS = ("security", "urls")
ALIASES = ()

# Safe URI schemes that are commonly used in Markdown
_SAFE_SCHEMES = frozenset(
    {
        "http",
        "https",
        "ftp",
        "ftps",
        "mailto",
        "tel",
        "file",
        "webcal",
        "irc",
        "ircs",
        "magnet",
        "git",
        "ssh",
        "sftp",
    }
)

# Dangerous or suspicious schemes
_DANGEROUS_SCHEMES = frozenset(
    {
        "javascript",
        "vbscript",
        "data",
        "file",
    }
)

# Regex to find URI schemes in Markdown link destinations and autolinks
_URI_SCHEME_RE = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+\-.]*):", re.IGNORECASE)
# Matches Markdown link URLs: [text](url) and <url> autolinks
_LINK_URL_RE = re.compile(r"(?:\]\()([^\s)]+)|(^|\s)<([^>]+)>")
# Matches bare URLs in text
_BARE_URL_RE = re.compile(
    r"""(?i)\b((?:https?|ftp|mailto|tel)://[^\s<>"']+|javascript\s*:[^\s<>"']+)"""
)


def _extract_scheme(url: str) -> str | None:
    """Extract the URI scheme from a URL string, or None if no scheme found."""
    m = _URI_SCHEME_RE.match(url)
    if m:
        return m.group(0)[:-1].lower()  # strip trailing colon
    return None


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> list[LintIssue]:
    """Flag lines containing dangerous URL schemes."""
    if ctx.get("in_code_block") or ctx.get("in_front_matter"):
        return []

    issues: list[LintIssue] = []

    # Check Markdown link URLs ([text](url))
    for m in _LINK_URL_RE.finditer(line):
        url = m.group(1) or m.group(2)
        if not url:
            continue
        scheme = _extract_scheme(url)
        if scheme is None:
            continue
        if scheme in _DANGEROUS_SCHEMES:
            label = {
                "javascript": "javascript: URI (XSS vector)",
                "vbscript": "vbscript: URI (XSS vector)",
                "data": "data: URI (potential injection)",
                "file": "file: URI (local file access)",
            }.get(scheme, f"{scheme}: URI (unusual scheme)")
            issues.append(
                LintIssue(file, lineno, NAME, f"dangerous URL scheme: {label}")
            )
        elif scheme not in _SAFE_SCHEMES:
            issues.append(
                LintIssue(
                    file,
                    lineno,
                    NAME,
                    f"unusual URL scheme: {scheme}: (not in common safe list)",
                )
            )

    # Check bare URLs not inside Markdown link syntax
    for m in _BARE_URL_RE.finditer(line):
        url = m.group(1)
        scheme = _extract_scheme(url)
        if scheme and scheme in _DANGEROUS_SCHEMES:
            # Avoid duplicate issues if already caught by link URL check
            already = any(i.line == lineno and url in i.message for i in issues)
            if not already:
                issues.append(
                    LintIssue(
                        file,
                        lineno,
                        NAME,
                        f"dangerous URL scheme in bare URL: {scheme}:",
                    )
                )

    return issues
