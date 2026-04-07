# Governance

Papyrus uses a strict source-of-truth model to prevent documentation sprawl and artifact drift.

## Core Rules

- Canonical articles live only in `knowledge/` and `archive/knowledge/`.
- Explanatory documentation lives only in `docs/`.
- Decisions for structural changes live only in `decisions/`.
- Rendered pages, SQLite indexes, and site output are derived artifacts.
- Generated or exported artifacts must never be edited by hand.

## Change Control

- Schema or taxonomy changes require rationale in `decisions/`.
- New top-level folders require rationale in `decisions/`.
- Validation is the completion gate for content, schema, taxonomy, template, and build changes.
- Deprecated or archived content must retain metadata and lifecycle history instead of being silently replaced.

## Anti-Sprawl Policy

- Do not duplicate canonical article content in `docs/`.
- Do not create overlapping templates for the same use case.
- Do not create parallel taxonomy files that describe the same concept.
- Prefer extending the existing schema, taxonomy, or template set over adding a fork.

## Generated Artifact Policy

- `generated/` holds derived site-input pages only.
- `build/` holds derived local data such as SQLite databases.
- `site/` holds rendered static site output.
- If a generated artifact is stale or incorrect, rebuild it. Do not patch it manually.
