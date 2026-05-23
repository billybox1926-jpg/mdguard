# mdguard design notes

This document records the Phase 4/5 integration decisions that are intentionally design-first.

## Dependency and extras policy (#57)

The default `mdguard` install remains stdlib-only and Python >=3.9 compatible. Features that need third-party packages must be optional extras and must not change default lint behavior.

Proposed extras:

- `mdguard[gfm]`: parser-backed CommonMark/GFM experiments.
- `mdguard[lsp]`: editor/LSP protocol helpers.
- `mdguard[docs]`: documentation-site generation tooling.

Default rules, CLI linting, JSON output, baselines, suppressions, and annotations must stay dependency-light unless the supported Python range is changed deliberately.

## Remote link cache design (#56)

Remote link checking, if implemented, is opt-in. Cache entries should include URL, method, status, checked timestamp, optional content headers, and an error summary. The cache should live under a user cache directory by default with a project-local override. Tests must use fake transports, never live network calls. Offline mode must never make requests.

## Docs site plan (#55)

The first docs site should use generated Markdown plus GitHub Pages. MkDocs/Sphinx remain docs-only optional extras. README remains a short landing page; docs should include rule reference, CLI/configuration, integrations, release checklist, and examples.

## Editor integration path (#53, #54)

The preferred first integration is CLI JSON plus GitHub/VS Code problem matcher documentation. A dedicated VS Code extension or LSP server is deferred until the public API and batch result model are stable. A future LSP prototype should map findings to diagnostics with one-line ranges and warning severity by default.

## CommonMark/GFM parser strategy (#47)

mdguard remains line-oriented by default. Parser-backed behavior may be added behind an optional extra after compatibility is proven. Current built-ins deliberately handle common low-risk states: fenced code blocks and front matter. Advanced GFM tables, HTML blocks, and slug behavior should be documented before enabling parser-specific semantics by default.

## markdownlint compatibility (#48)

mdguard does not claim markdownlint parity. Rule docs may list near-equivalent markdownlint IDs as migration hints, but aliases must only be added when behavior is close enough and tested.
