# Seed Migration Rationale

## Scope

This repository seed follows a curated migration model captured in this rationale and does not redesign the information architecture. Draft source pages are excluded from the migration review set. The legacy knowledge export is treated only as temporary migration input; canonical Markdown with YAML front matter lives under `knowledge/`.

## What Was Kept

- Canonical article titles and collection structure were preserved where they could be sanitized safely.
- Collection indexes were created for each planned collection path so the KMDB remains navigable even when source material came from folder-heavy exports.
- Useful landing-page context was retained only when it could be generalized without preserving company-specific operating details.

## What Was Generalized

- Company identity, people, contact details, host details, and location-specific references were replaced with consistent placeholders.
- Product, platform, and vendor branding were replaced with functional placeholders.
- Source-specific screenshots, binary attachments, and embedded exports were excluded from canonical seed content when they could not be sanitized safely.

## What Was Not Preserved

- No reversible source-to-seed crosswalk is kept in the repository.
- Source archive paths, raw export identifiers, and branded source labels were removed from migration artifacts.
- Detailed alias and exclusion history was reduced to non-reversible sanitized metadata where retaining the original label set would expose sensitive or proprietary context.

## Synthetic Pages

The migration creates collection pages for top-level and nested sections so the seeded structure is navigable without relying on the original portal hierarchy.

## Determinism And Auditability

- `docs/migration/seed-migration-rationale.md` is the maintained migration record for the sanitized seed structure and provenance boundary.
- Canonical collection indexes live directly under `knowledge/` and remain the source used by the runtime and validators.
- `scripts/validate_migration.py` verifies that the maintained migration rationale is present, does not refer to removed migration artifacts, and that the required top-level collection indexes still exist.
