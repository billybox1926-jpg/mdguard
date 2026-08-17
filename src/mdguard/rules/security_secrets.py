"""Security rule: detect potential secrets, tokens, and credentials in Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from mdguard.core import LintIssue

NAME = "security-secrets"
DEFAULT_ENABLED = False
DESCRIPTION = "Detect API keys, tokens, passwords, and credential patterns"
TAGS = ("security", "secrets")
ALIASES = ()

# Patterns that indicate potential secrets.
# Each entry: (compiled_regex, label, requires_surrounding_context)
#
# We use word-boundary and lookbehind/ahead to reduce false positives.
# A match is only reported if it looks like an assigned value
# (e.g. KEY=value, "key": "value", $ENV, etc.) rather than a doc example.

# Common API key prefixes / patterns
_API_KEY_PATTERNS = (
    # Generic high-entropy hex/base64-looking tokens after common key names
    (
        re.compile(
            r"""\b(?:api[_-]?key|apikey|api_secret|apisecret|access_token|"""
            r"""auth_token|token|secret|private_key|public_key|"""
            r"""api[_-]?id|client[_-]?id|client[_-]?secret|"""
            r"""aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key|"""
            r"""authorization|bearer)\s*[=:]\s*["']?([A-Za-z0-9+/=]{8,})["']?"""
        ),
        "potential API key / token assignment",
    ),
    # ENV-style: KEY=VALUE or export KEY=VALUE
    (
        re.compile(
            r"""(?:^|\s)(?:export\s+)?"""
            r"""([A-Za-z_][A-Z_A-Z_0-9]*_?(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|"""
            r"""API[_-]?KEY|BEARER|AUTH))["']?\s*[=:]\s*["']?([^\s"']{8,})["']?"""
        ),
        "environment-style secret assignment",
    ),
    # JSON / YAML style: "key": "value" or key: value
    (
        re.compile(
            r"""["']?(?:api[_-]?key|apikey|api_secret|apisecret|access_token|"""
            r"""auth_token|token|secret|private_key|public_key|"""
            r"""client[_-]?secret|aws[_-]?secret)["']?\s*[:=]\s*["']?(\S{8,})["']?"""
        ),
        "structured secret assignment (JSON/YAML/TOML)",
    ),
    # Generic bearer token in header-like context
    (
        re.compile(r"""bearer\s+[A-Za-z0-9\-._~+/]+=*""", re.IGNORECASE),
        "Bearer token in plain text",
    ),
    # AWS access key ID pattern (AKIA + 16 chars)
    (
        re.compile(r"""\bAKIA[0-9A-Z]{16}\b"""),
        "AWS access key ID pattern (AKIA...)",
    ),
    # GitHub token patterns (ghp_, github_pat_, gho_)
    (
        re.compile(
            r"""\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9]{82}|gho_[A-Za-z0-9]{36})\b"""
        ),
        "GitHub token pattern detected",
    ),
    # Generic high-entropy string assignment (heuristic — may have false positives)
    # Only fires on assignments with long alphanumeric strings
    (
        re.compile(
            r"""\b(?:key|secret|token|password)\s*[=:]\s*["']?([A-Za-z0-9]{16,})["']?"""
        ),
        "long secret-like value assigned to key/token/password",
    ),
)

# Password in cleartext assignment (broader, lower confidence)
_PASSWORD_PATTERN = re.compile(
    r"""\bpassword\s*[=:]\s*["']?([^"'@\s]{4,})["']?""", re.IGNORECASE
)

# Google API key pattern (AIza...)
_GOOGLE_API_KEY_RE = re.compile(r"""\bAIza[0-9A-Za-z\-_]{35}\b""")

# Stripe secret key pattern (sk_live_ / sk_test_)
_STRIPE_KEY_RE = re.compile(r"""\bsk_(?:live|test)_[0-9a-zA-Z]{24,}\b""")

# Slack bot/user token patterns
_SLACK_TOKEN_RE = re.compile(r"""\bxox[baprs]-[0-9a-zA-Z]{10,}\b""", re.IGNORECASE)

# Generic private key header
_PEM_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)


def check(
    file: Path, line: str, lineno: int, ctx: dict, config: dict
) -> list[LintIssue]:
    """Flag lines containing patterns that resemble secrets or credentials."""
    if ctx.get("in_code_block") or ctx.get("in_front_matter"):
        return []

    issues: list[LintIssue] = []

    # 1. High-confidence secret patterns
    for pattern, label in _API_KEY_PATTERNS:
        if pattern.search(line):
            issues.append(LintIssue(file, lineno, NAME, label))

    # 2. Generic password assignment
    m = _PASSWORD_PATTERN.search(line)
    if m:
        issues.append(
            LintIssue(file, lineno, NAME, "password assignment in plain text")
        )

    # 3. Specific well-known key formats
    if _GOOGLE_API_KEY_RE.search(line):
        issues.append(LintIssue(file, lineno, NAME, "Google API key pattern (AIza...)"))

    if _STRIPE_KEY_RE.search(line):
        issues.append(
            LintIssue(
                file, lineno, NAME, "Stripe secret key pattern (sk_live_/sk_test_)"
            )
        )

    if _SLACK_TOKEN_RE.search(line):
        issues.append(
            LintIssue(file, lineno, NAME, "Slack token pattern (xoxb/xoxp/xoxa/xoxr)")
        )

    # 4. PEM private key header
    if _PEM_PRIVATE_KEY_RE.search(line):
        issues.append(LintIssue(file, lineno, NAME, "PEM private key header detected"))

    return issues
