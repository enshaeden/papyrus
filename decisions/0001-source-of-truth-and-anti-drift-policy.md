# 0001 Source Of Truth And Anti-Drift Policy

## Status

Accepted

## Context

The repository needs clear controls against documentation sprawl, duplicate artifacts, and drift between canonical content and derived outputs.

## Decision

- Keep canonical operational content only in `knowledge/` and `archive/knowledge/`.
- Keep explanatory repository documentation only in `docs/`.
- Keep structural decisions in `decisions/`.
- Keep derived site sources, local indexes, and rendered output outside canonical directories.
- Enforce lifecycle, duplicate, directory, metadata, and sanitization rules through validation.
- Restrict article creation to the approved template families defined in `templates/`.

## Consequences

- Contributors must update source files rather than editing derived outputs.
- Schema and taxonomy changes require explicit rationale.
- The repository is stricter, but drift risk is materially lower.
