# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-08-17

### Added
- Initial release of `mdguard`, a dependency-light Markdown linter and conservative autofixer.
- Built-in rules:
  - `empty-link` – detect empty link destinations.
  - `final-newline` – ensure files end with a newline.
  - `heading-jump` – report skipped heading levels.
  - `line-length` – warn on lines exceeding a configurable length (default 120).
  - `trailing-whitespace` – detect and fix trailing spaces.
- Optional rules (disabled by default):
  - `duplicate-headings` – flag repeated headings.
  - `missing-h1` – require a top-level heading.
- Security rules (opt-in):
  - `security-xss` – detect raw HTML/JS in Markdown.
  - `security-urls` – flag dangerous URI schemes.
  - `security-secrets` – alert on API keys and tokens (GitHub, AWS, Stripe, Slack, PEM).
- CLI with `--fix`, `--json`, `--format github`, `--baseline`, `--write-baseline`, and inline suppression comments.
- Recursive file discovery with `.mdguardignore` support.
- `pyproject.toml` configuration via `[tool.mdguard]`.
- Public API (`mdguard.api.lint_paths`) for embedding.
- GitHub Actions annotation output.
- Baseline support for incremental adoption.
- Conservative autofix (trailing whitespace, final newline).

### Fixed
- Security hardening: path traversal protection, secure temporary file handling, file size cap (10 MB), and proper escaping for GitHub Actions annotations.
- Robust UTF-8 and UTF-16 file encoding support.

### Changed
- N/A (initial release)
