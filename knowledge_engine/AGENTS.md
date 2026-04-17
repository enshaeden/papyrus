# AGENTS.md

This file governs work under `knowledge_engine/`.

## Purpose

`knowledge_engine/` contains the core knowledge-model material that Papyrus uses to author, validate, and govern knowledge objects.
Knowledge object definition material resides here, including `schemas/`, `taxonomies/`, and `templates/`.
Use `knowledge_engine/` for structural, model-level content that defines how knowledge objects are shaped, classified, validated, and rendered.
Do not use `knowledge_engine/` for repository commentary, Papyrus system knowledge articles, or published production knowledge content.

Use it to maintain the authoring and governance model behind Papyrus content, not to store the governed content corpus itself.

## Rules

- Treat `knowledge_engine/` as the source of truth for knowledge object structure, classification, and authoring rules.
- Keep published or publishable knowledge objects out of `knowledge_engine/`. They belong in `docs/` unless the repository model explicitly says otherwise.
- Keep Papyrus implementation notes, temporary migration logic, and developer scratch material out of `knowledge_engine/` unless they directly define the knowledge model.
- Update the existing schema, taxonomy, or template instead of creating a parallel version when a valid source of truth already exists.
- Do not create duplicate or conflicting definitions for the same object type, field, taxonomy term, or template behavior.
- Keep terminology consistent across schemas, taxonomies, templates, validation logic, and related decisions.
- Preserve stable identifiers, field names, taxonomy keys, and template contracts unless the model is intentionally being changed.
- When changing one part of the model, update dependent material in the same task where practical, including templates, validations, examples, and docs that rely on it.
- Mark deprecated fields, legacy taxonomy terms, compatibility shims, and transitional template behavior explicitly. Do not let them read like the active model.
- Keep examples and sample structures aligned with the current model. Do not leave stale field names, object types, or taxonomy paths in place.
- Prefer a single clear model path over preserving redundant or transitional definitions.

## Model Integrity

- Every schema, taxonomy, and template in `knowledge_engine/` should correspond to a real part of the Papyrus knowledge-object model.
- Keep boundaries clear between structure, classification, and presentation. Schemas define object shape, taxonomies define classification, and templates define authoring or rendering scaffolds.
- Respect object type contracts. A runbook, known error, service record, policy, or other governed type should not drift through inconsistent field definitions or template assumptions.
- Preserve relationships between schemas, taxonomy terms, templates, and validation rules where they are part of the active model.
- If an object type, field, or taxonomy branch is superseded, merged, split, withdrawn, or renamed, update dependent model material together.

## Decisions

- `decisions/` defines governance, publication, terminology, and model rules that may constrain material stored in `knowledge_engine/`.
- Keep content in `knowledge_engine/` consistent with active decisions on object structure, naming, lifecycle, review flow, and publication behavior.
- If a decision changes the meaning of fields, object types, taxonomy structure, or template responsibilities, update affected material in `knowledge_engine/` to match.
- Do not invent local conventions in `knowledge_engine/` that conflict with repository decisions, schemas, or validation rules.

## Validation

- Validate all changes in `knowledge_engine/` against the current schemas, model rules, repository checks, and any contract tests that depend on them.
- If a schema, taxonomy entry, or template claim cannot be verified against the active repository model, remove it or label it explicitly as pending.
- Run relevant validation, linting, and contract checks when changing field structure, identifiers, taxonomy terms, template inputs, or rendered model behavior.
- Update or remove stale examples, deprecated keys, broken references, and contradictory terminology before merging changes under `knowledge_engine/`.