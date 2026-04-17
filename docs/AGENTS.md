# AGENTS.md

This file governs work under `docs/`.

## Purpose

`docs/` is reserved for future in-repository governed production knowledge content when Papyrus is used as a live production authoring environment.
In this repository state, `docs/` should contain only structure folders, scaffolding, guidance files, and supporting assets.
Papyrus system knowledge about Papyrus itself belongs under `knowledge/`, not `docs/`.
When production-governed content is intentionally brought in-repository, organize it under the `policy/`, `end-user/`, `services/`, and `systems/` hierarchy.
Do not use `docs/` as a scratch space, migration holding area, or parallel notes location.

## Rules

- Treat `docs/` as reserved production-content structure and guidance in the current repository state, not as the active Papyrus system knowledge base.
- Keep Papyrus system design, platform behavior, developer guidance, and implementation notes out of `docs/`; they belong in `knowledge/`, `decisions/`, or code-adjacent sources unless they are intentional published knowledge objects for readers.
- Update the existing governed object instead of creating a parallel file when a valid document already exists.
- Do not create duplicate content to represent the same operational fact, procedure, or service state.
- Write for the intended audience of the object. Keep scope, language, and instructions consistent with the reader role and object type.
- Preserve the reserved content hierarchy. Keep the `policy/`, `end-user/`, `services/`, and `systems/` structure available, and do not introduce alternative top-level content groupings unless the repository model is explicitly changed.
- Preserve governance-visible structure and metadata needed by the system. Do not strip or casually rewrite identifying fields, review fields, status fields, or relationship fields.
- Keep object content aligned with the current approved state. Do not merge draft language, review commentary, or abandoned alternatives into published content.
- Mark deprecated guidance, temporary exceptions, and local-only deviations explicitly. Do not let them read like the stable default.
- Keep examples, commands, paths, and referenced identifiers current and internally consistent within the object.
- When importing or normalizing content, prefer a single clean governed object over preserving source-format quirks.
- Do not use `docs/` to archive raw exports, working notes, or migration leftovers unless they are intentionally stored as governed content with clear status and purpose.

Content currently kept in `docs/` should be limited to things like:
- Structure folders for future governed content
- Guidance files that explain how `docs/` is reserved and should be used later
- Supporting assets needed by those guidance files or future structure

## Object Integrity

- Every file in `docs/` should correspond to reserved structure, a guidance file, a supporting asset, or, when explicitly in live production-authoring scope, a real governed knowledge object.
- Keep object boundaries clear. One file should represent one governed content unit unless the format explicitly requires a supporting split.
- Respect the object type contract. A runbook, known error, and system procedure should not collapse into one another through careless editing.
- Preserve links, citations, relationships, and service associations where they are part of the governed object model.
- If an object is superseded, merged, split, withdrawn, or reclassified, update the affected content and references together.
- Preserve the established content hierarchy. Do not move scaffolding, guidance, or future governed objects across `policy/`, `end-user/`, `services/`, and `systems/` without a real classification reason.

## Decisions

- `decisions/` defines governance, publishing, review, and model rules that may constrain content stored in `docs/`.
- Keep content in `docs/` consistent with active decisions on object structure, terminology, review flow, and publication rules.
- If a decision changes the meaning of statuses, fields, object types, or relationship rules, update affected docs content to match.
- Do not invent local conventions in `docs/` that conflict with repository decisions or schemas.

## Validation

- Validate any `docs/` guidance, structure, or future governed content against the current repository checks that apply to `docs/`.
- If a content claim depends on a service fact, procedure, workflow, or identifier, verify it against the available source of truth before keeping it.
- If imported content cannot yet be verified or normalized, label it clearly as pending review instead of presenting it as fully governed fact.
- Run relevant validation, linting, or contract checks when changing object structure, metadata, references, or stable rendered content.
- Fix or remove stale examples, broken references, and contradictory status language before merging changes under `docs/`.
