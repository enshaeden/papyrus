# Governance

Papyrus uses a strict source-of-truth model so the control plane stays auditable, local-first, and rebuildable.

## Governance Boundaries

- Canonical authored knowledge lives only in `knowledge/` and `archive/knowledge/`.
- Explanatory architecture and workflow documentation lives only in `docs/`.
- Structural decisions live only in `decisions/`.
- Application runtime code lives in `src/papyrus/`.
- Generated artifacts under `generated/`, `build/`, and `site/` are derived and non-authoritative.

## Canonical Source Versus Runtime State

- Markdown source is the authoritative authored record.
- Runtime state is a rebuildable local projection used for validation, search, reporting, and governance workflows.
- Export surfaces, including MkDocs output, must be derivable from source plus application logic.
- If runtime state or exported output disagrees with source, source wins and the projection must be rebuilt.

## Change Control

- Schema or taxonomy changes require rationale in `decisions/`.
- New top-level folders require rationale in `decisions/`.
- Validation is the completion gate for content, schema, taxonomy, runtime, and export changes.
- Deprecated or archived source must retain lifecycle history instead of being silently replaced.

## Anti-Sprawl Rules

- Do not duplicate canonical knowledge in `docs/`.
- Do not keep extending a universal flat article model as the primary domain model.
- Do not create parallel schemas, templates, or taxonomies without an explicit migration bridge and deprecation path.
- Do not let generated exports or browse views become the primary product surface.
- Do not leave durable business logic trapped in ad hoc scripts when it belongs in the application package.

## Static Export Policy

- MkDocs and generated site content are optional export surfaces.
- Static export is gated by runtime approval state and is limited to approved knowledge content plus supporting repository material.
- Export content may help with publishing and browsing, but it is secondary to authored source and application runtime behavior.
- If export output is stale or incorrect, rebuild it. Do not patch generated files by hand.
