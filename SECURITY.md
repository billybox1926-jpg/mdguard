# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the maintainers rather than opening a public issue.

Include:

- affected version/commit
- reproduction details
- potential impact
- suggested remediation (if known)

## Response goals

- Acknowledge report receipt promptly.
- Validate and triage impact.
- Publish a fix and disclosure timeline when ready.

## Security Capabilities (Opt-In)

mdguard includes three optional security-aware rules that detect potentially unsafe
content in Markdown files:

| Rule | Detects | Default |
|------|---------|---------|
| `security-xss` | Script tags, event handlers, data URIs, iframe/embed tags | Disabled |
| `security-urls` | Dangerous URI schemes (`javascript:`, `vbscript:`, `file:`) | Disabled |
| `security-secrets` | API keys and tokens (GitHub `ghp_`/`gho_`/`github_pat_`, AWS `AKIA`, Stripe `sk_live_`/`sk_test_`, Slack `xoxb-`/`xoxp-`, PEM headers) | Disabled |

**Important:** These rules are **opt-in** and heuristic-based. They may produce
false positives on documentation containing code examples, and false negatives on
novel attack patterns. They are not a substitute for dedicated security tooling.

Enable during linting:

```bash
mdguard docs/ --enable security-xss,security-urls,security-secrets
```

## What mdguard Is NOT

mdguard is **not** a substitute for:

- Dedicated SAST/DAST scanners
- Content sanitization libraries (e.g., DOMPurify equivalents)
- Secret management tools (e.g., `git-secrets`, `gitleaks` for production repos)
- Web application firewalls or runtime protection

Think of mdguard's security rules as **early-warning signals** for documentation
authors, not guarantees of content safety.
