# Information Architecture

Papyrus separates canonical content from explanatory docs and derived outputs.

## Directory Contract

- `knowledge/`: active canonical knowledge articles only.
- `archive/knowledge/`: archived canonical knowledge articles with preserved metadata.
- `taxonomies/`: controlled vocabularies referenced by schema and validation.
- `schemas/`: article schema and repository-policy definitions.
- `templates/`: approved reusable content templates only.
- `migration/`: sanitized migration plans, manifests, and supporting inputs. Never canonical article source.
- `reports/`: sanitized migration and review reports. Never canonical article source.
- `docs/`: explanatory documentation about the repository, workflow, governance, and architecture.
- `decisions/`: ADR-style records for structural changes.
- `generated/`: derived site-source pages created by build scripts.
- `build/`: derived local data such as the search index.
- `site/`: rendered site output.

## Discoverability Strategy

- Use controlled `systems`, `services`, and `tags` vocabularies.
- Prefer cross-links and generated indexes over duplicate summary documents.
- Use generated start-here and by-service, by-system, and by-tag views to improve findability.

## Canonical Path Rule

Every article declares `canonical_path`, and validation enforces that it matches the repository path. This prevents copies from masquerading as canonical content.
