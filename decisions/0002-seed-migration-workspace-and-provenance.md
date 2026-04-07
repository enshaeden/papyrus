# 0002 Seed Migration Workspace And Sanitized Provenance

## Status

Accepted

## Context

The repository needs a deterministic and auditable way to seed canonical knowledge from a legacy export without treating raw export artifacts as long-term source of truth. The migration also needs provenance fields that remain useful after sanitization, without preserving reversible mappings back to sensitive source material.

## Decision

- Allow a top-level `migration/` workspace for sanitized seed plans, manifests, and migration-only validation inputs.
- Keep `migration/` non-canonical. Articles remain authoritative only under `knowledge/` and `archive/knowledge/`.
- Require `source_system` and `source_title` on articles and templates so imported and native content retain sanitized provenance.
- Preserve migration selection outcomes in sanitized manifests instead of retaining raw export paths, source ids, or branded labels.
- Validate the curated seed structure separately from the canonical article schema.

## Consequences

- Migration metadata can be versioned and reviewed without polluting canonical article directories.
- Validation can enforce title uniqueness, planned structure, and repeatable imports without retaining sensitive source detail.
- Canonical articles must carry sanitized provenance fields going forward.
