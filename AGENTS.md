# Repository Rules

This repository is a local-first knowledge system for IT support and systems operations. Keep the content model durable, low-drift, and auditable.

## Source Of Truth

- Canonical knowledge articles live only under `knowledge/` and `archive/knowledge/`.
- Canonical explanatory documentation lives under `docs/` and decisions live under `decisions/`.
- Controlled vocabularies live only under `taxonomies/`.
- Field and repository policy definitions live only under `schemas/`.
- Approved content templates live only under `templates/`.

## Derived Artifacts

- Generated and build outputs must live only under `generated/`, `build/`, or `site/`.
- Generated files are derived artifacts and must never be edited by hand.
- If a generated file is wrong, fix the source or generator and rebuild.
- Generated artifacts must remain reproducible from source files and the repository build scripts.

## Anti-Sprawl Rules

- Do not add new top-level folders without a documented rationale in `decisions/`.
- Do not create duplicate templates, parallel schemas, or parallel taxonomies.
- Reuse the existing schema, taxonomy, and approved templates instead of forking them.
- Do not copy canonical article content into `docs/`.
- Archive retired content instead of silently replacing or overwriting it.
- Delete obsolete derived artifacts or duplicate clutter instead of preserving it.

## Content Requirements

- Every knowledge item must declare `id`, `title`, `owner`, `object_lifecycle_state`, `created`, `updated`, `last_reviewed`, `review_cadence`, `canonical_path`, and `source_type`.
- Deprecated or archived content must include replacement or retirement rationale according to the lifecycle policy.
- Content lifecycle state must follow the documented lifecycle: `draft -> active -> deprecated -> archived`.
- Changes to schema or taxonomy files require rationale in `decisions/`.

## Completion Gate

- Validation must pass before work is considered complete.
- Do not treat rendered, indexed, exported, or copied outputs as authoritative.
- If source and derived artifacts disagree, the source wins and the derived artifact must be rebuilt.
