# 0003 Sanitized Reports And Public Seed Artifacts

## Status

Accepted

## Context

The repository now produces sanitized migration reports and placeholder glossaries that help review the public seed set. Those artifacts are useful for audit and handoff, but they are not canonical knowledge articles.

## Decision

- Allow a top-level `reports/` directory for sanitized review artifacts only.
- Keep `reports/` non-canonical and exclude it from article discovery.
- Require reports to avoid reversible mappings to legacy source values.
- Treat reports as validation inputs only where explicitly configured.

## Consequences

- Review artifacts can be versioned without polluting canonical article roots.
- The repository can document sanitization outcomes and residual manual-review risks in a stable location.
- Contributors must not use `reports/` as a substitute for canonical content or decision records.
