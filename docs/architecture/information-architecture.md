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

## User-Facing Areas

The generated site separates repository content into three user-facing areas:

- Knowledge Base: canonical operator-facing procedures and references sourced from `knowledge/` and `archive/knowledge/`
- System & Design Docs: explanatory repository, schema, taxonomy, generator, and workflow documentation sourced from `docs/`
- Governance & Decisions: policy and ADR-style structural rationale sourced from `decisions/` with supporting governance references from `docs/`

This separation is a browse-layer concern only. It does not change the repository source-of-truth model.

## Placement Rubric

- Put content in `knowledge/` when it tells operators how to do the work.
- Put content in `docs/` when it explains how the knowledge system or repository design works.
- Put content in `decisions/` when it records a durable structural choice with rationale and tradeoffs.

## Discoverability Strategy

- Use controlled `systems`, `services`, and `tags` vocabularies.
- Prefer cross-links and generated indexes over duplicate summary documents.
- Use generated start-here and by-service, by-system, and by-tag views to improve findability.
- Cross-link between knowledge, docs, and decisions where useful without copying canonical article content into `docs/`.

## Canonical Path Rule

Every article declares `canonical_path`, and validation enforces that it matches the repository path. This prevents copies from masquerading as canonical content.
