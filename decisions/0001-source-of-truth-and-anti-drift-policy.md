# 0001 - Source Of Truth And Anti-Drift Policy

## Status

Accepted

## Context

The repository needs stronger controls against documentation sprawl, duplicate artifacts, and drift between canonical content and rendered or indexed outputs.

## Decision

- Keep canonical operational content only in `knowledge/` and `archive/knowledge/`.
- Keep explanatory repository docs only in `docs/`.
- Keep structural decisions in `decisions/`.
- Keep site-input copies and indexes derived under generated/build paths only.
- Enforce lifecycle, duplicate, directory, and metadata rules through validation.
- Restrict article creation to the approved template families defined in `templates/`.

## Consequences

- Contributors must update source files rather than editing rendered outputs.
- Schema and taxonomy changes now require explicit rationale.
- The repository is stricter, but drift risk is materially lower.
