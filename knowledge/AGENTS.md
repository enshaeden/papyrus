# AGENTS.md

## Purpose

This subtree contains Papyrus canonical knowledge objects.

Optimise for durability, auditability, low drift, provenance, lifecycle clarity, and strict alignment with repository schemas, taxonomies, and approved templates.

Knowledge content is not freeform repository prose.
It is structured system content.
Treat every change as a change to the product’s canonical knowledge layer.

## Authority

Within this subtree, use this order of authority:

1. `schemas/` for field definitions, validation rules, and policy requirements
2. `taxonomies/` for controlled vocabularies and classification structures
3. `templates/` for approved object and entry structures
4. `knowledge/` content files as canonical content
5. `decisions/` for explicit rationale and approved deviations
6. `docs/` for explanatory guidance only
7. generated, indexed, exported, rendered, or copied outputs as derived only

If a knowledge file conflicts with schema, taxonomy, or approved structure, fix the source content or governing definition. Do not work around the conflict in rendering layers.

## Core Rules

- Content in this subtree is canonical unless explicitly marked otherwise by repository policy.
- Do not treat rendered views, generated exports, or search indexes as source.
- Do not duplicate canonical knowledge content into `docs/`, fixtures, demos, or convenience files.
- Do not introduce parallel knowledge models, alternate metadata schemes, or ad hoc field names.
- Do not weaken structure for convenience in display or ingestion layers.
- Prefer explicit structure over inferred meaning.

## Knowledge Object Rules

Papyrus knowledge objects may contain multiple structured entries or sections.
Preserve the distinction between:

- the knowledge object as the canonical unit
- entries or subordinate structured content within the object
- lifecycle and governance metadata
- taxonomic classification
- provenance and canonical path

Do not flatten object-level and entry-level concerns into one undifferentiated blob unless the governing template explicitly requires it.

When editing content:

- preserve object identity
- preserve stable identifiers
- preserve object-to-entry relationships
- preserve traceability between visible content and source structure

## Required Fields

Every canonical knowledge item must include the required fields defined by schema.

At minimum, each item must include:

- `id`
- `title`
- `owner`
- `object_lifecycle_state`
- `created`
- `updated`
- `last_reviewed`
- `review_cadence`
- `canonical_path`
- `source_type`

Additional rules:

- field names must match schema exactly
- do not invent undocumented fields
- do not silently drop required fields
- do not repurpose existing fields for new meaning without updating schema and rationale
- `canonical_path` must continue to point to the canonical source location
- `updated` must reflect substantive source changes, not unrelated rebuilds elsewhere

## Lifecycle Rules

Lifecycle state must follow the documented progression:

`draft -> active -> deprecated -> archived`

Rules:

- do not skip lifecycle logic casually
- do not mark content active if it is structurally incomplete or lacks required metadata
- deprecated content must include replacement guidance or retirement rationale according to policy
- archived content must retain enough metadata and rationale to remain auditable
- do not silently replace deprecated or archived content with new content under the same identity unless policy explicitly allows it

When retiring or replacing content, preserve historical traceability.

## Taxonomy and Classification Rules

- Use only approved vocabularies from `taxonomies/`.
- Do not create near-duplicate tags, categories, or classifications inside content files.
- Do not encode classification logic in prose when it belongs in structured taxonomy fields.
- If existing taxonomy is insufficient, update the governing taxonomy with rationale in `decisions/` rather than improvising locally.
- Keep classification precise enough to support retrieval, filtering, and governance.

## Template Rules

- New knowledge content must follow approved templates from `templates/`.
- Do not fork templates inside individual content files.
- Do not drift from approved structure merely because one item is awkward.
- If a template is broadly insufficient, update the template and record the rationale rather than inventing one-off local structure.
- Preserve consistency across similar content types.

## Provenance and Auditability Rules

- Preserve provenance fields and source indicators.
- Do not remove metadata needed to trace where a knowledge item came from, who owns it, or how it entered the system.
- Imported or transformed content is not automatically canonical until it has been mapped into approved structure and stored in its canonical location.
- Do not overwrite provenance with display-oriented summaries.
- Prefer additive auditability over destructive cleanup.

## Change Discipline

- Make the smallest correct source change.
- Edit canonical files directly when the task is a canonical content correction.
- Do not patch downstream renderers, indexes, or exports to mask bad source content.
- Do not perform bulk formatting churn unless the task explicitly requires it.
- Do not rename or move canonical content casually; update all affected references when such a change is required.
- Preserve stable IDs wherever possible.

## Archive Handling

- Archive retired content instead of deleting it when repository policy requires preservation.
- Archived content must remain distinguishable from active content.
- Do not mix archived and active material in ways that obscure lifecycle state.
- Do not restore archived content to active use without explicitly updating lifecycle state and supporting metadata.
- Preserve retirement or replacement rationale.

## Writing and Content Quality Rules

- Prefer precise operational language over narrative filler.
- Keep guidance structured, scannable, and reusable.
- Avoid redundant explanations across multiple knowledge objects when one canonical object should serve that role.
- Do not let explanatory prose obscure actionable content.
- Preserve clarity for both human readers and system use.

## Validation Expectations

Use the repository’s canonical content verification entrypoints.

- validate content: `python3 scripts/validate.py`
- lint or schema check: `python3 scripts/report_content_health.py --section duplicates --section citation-health --section knowledge-like-docs`
- rebuild derived artifacts if needed: `./scripts/build_static_export.sh`

For changes in this subtree, completion requires:

- schema validation passes
- required fields remain present
- taxonomy values remain valid
- lifecycle state remains valid
- canonical path remains correct
- derived artifacts are regenerated if affected
- no duplicate canonical copy was introduced
- related documentation is updated if the meaning or workflow changed

## Reporting Format

At the end of each task affecting this subtree, report in this order:

1. knowledge objects changed
2. whether object structure, metadata, taxonomy, or lifecycle changed
3. validation results
4. derived artifacts regenerated
5. unresolved risks, policy questions, or follow-up work

Do not state that content is correct unless this evidence is present.

## Planning Trigger

Create a written plan before editing when the task:

- changes many knowledge objects at once
- changes shared metadata patterns
- changes lifecycle handling
- introduces or modifies taxonomy usage
- requires template changes
- involves migration from imported content into canonical structure
- has any ambiguity about object-level versus entry-level responsibility
