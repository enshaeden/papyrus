# Governance

Papyrus uses a strict source-of-truth model to prevent documentation sprawl and derived-artifact drift.

## Core Rules

- Canonical articles live only in `knowledge/` and `archive/knowledge/`.
- Explanatory documentation lives only in `docs/`.
- Structural decisions live only in `decisions/`.
- Sanitized migration inputs live only in `migration/`.
- Sanitized review artifacts live only in `reports/`.
- Derived pages, indexes, and rendered site output are not authoritative.

## Change Control

- Schema or taxonomy changes require rationale in `decisions/`.
- New top-level folders require rationale in `decisions/`.
- Validation is the completion gate for content, schema, taxonomy, template, migration, and build changes.
- Deprecated or archived content must retain metadata and lifecycle history instead of being silently replaced.

## Anti-Sprawl Policy

- Do not duplicate canonical article content in `docs/`.
- Do not create overlapping templates for the same use case.
- Do not create parallel taxonomy files for the same concept.
- Prefer extending the existing schema, taxonomy, template set, or report structure over adding a fork.

## Generated Artifact Policy

- `generated/` holds derived site-source pages only.
- `build/` holds derived local data.
- `site/` holds rendered static site output.
- If a generated artifact is stale or incorrect, rebuild it. Do not patch it manually.
