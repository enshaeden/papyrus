# Information Architecture

Papyrus separates canonical content from explanatory docs and derived outputs.

## Directory Contract

- `knowledge/`
  Allowed: active canonical knowledge articles.
  Forbidden: generated pages, exports, copied site content, or ad hoc templates.
- `archive/knowledge/`
  Allowed: archived canonical knowledge articles with preserved metadata.
  Forbidden: active articles or generated exports.
- `taxonomies/`
  Allowed: controlled vocabularies referenced by schema and validation.
  Forbidden: duplicate or overlapping taxonomies for the same concept.
- `schemas/`
  Allowed: article schema and repository policy definitions.
  Forbidden: ad hoc copies of schema files.
- `templates/`
  Allowed: approved reusable content templates only.
  Forbidden: duplicate or one-off templates.
- `docs/`
  Allowed: explanatory docs about the repository, workflow, governance, and architecture.
  Forbidden: canonical article copies or generated article mirrors.
- `decisions/`
  Allowed: ADR-style records for structural changes.
  Forbidden: operational runbooks or copied knowledge articles.
- `generated/`
  Allowed: derived site-input pages created by build scripts.
  Forbidden: canonical source content or manual edits.
- `build/`
  Allowed: derived local data such as SQLite indexes.
  Forbidden: source files or hand-maintained datasets.
- `site/`
  Allowed: rendered static site output.
  Forbidden: source edits.

## Discoverability Strategy

- Use controlled `systems`, `services`, and `tags` vocabularies.
- Prefer cross-links and generated indexes over duplicate “summary” documents.
- Use generated start-here and by-service/by-system/by-tag pages to improve findability.

## Canonical Path Rule

Every article declares `canonical_path`, and validation enforces that it matches the repository path. This prevents copies from masquerading as originals.
