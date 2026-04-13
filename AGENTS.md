# AGENTS.md

## Purpose

Papyrus is a local-first knowledge system for IT support and systems operations.
Optimise for durability, auditability, low drift, reproducibility, and clean separation between canonical source content, application code, and derived outputs.

This root file defines repository-wide rules.
When a deeper `AGENTS.md` exists in a subdirectory, the deeper file governs work in that subtree.

## Repository Priorities

When making trade-offs, prioritise in this order:

1. Canonical source integrity
2. Schema and taxonomy consistency
3. Reproducible generation and build behaviour
4. Clear information architecture
5. UX clarity for operators and readers
6. Documentation accuracy
7. Cosmetic polish

Do not sacrifice structural correctness for visual polish or speed.

## Authority Order

When files or outputs disagree, use this order of authority unless a deeper `AGENTS.md` explicitly narrows it:

1. `schemas/` for field definitions, validation rules, and repository policy definitions
2. `taxonomies/` for controlled vocabularies and classification structures
3. `templates/` for approved content structures and authoring patterns
4. `knowledge/` and `archive/knowledge/` for canonical knowledge objects and entries
5. `decisions/` for intentional deviations, design rationale, and governance records
6. `src/` for application source code for system behaviour and interfaces
7. `docs/` for explanatory and operational documentation
8. `generated/`, `build/`, and `site/` for derived artifacts only

Rendered, indexed, exported, copied, cached, or generated outputs are never authoritative.

## Canonical Content Rules

- Canonical knowledge articles and objects live only under `knowledge/` and `archive/knowledge/`.
- Canonical explanatory documentation lives only under `docs/`.
- Architectural and governance decisions live under `decisions/`.
- Controlled vocabularies live only under `taxonomies/`.
- Field definitions and repository policy definitions live only under `schemas/`.
- Approved authoring and content templates live only under `templates/`.

Do not duplicate canonical content across directories.
Do not create shadow copies of knowledge objects in documentation, UI fixtures, or test helpers unless the task explicitly requires a controlled fixture.

## Derived Artifact Rules

- Generated and build outputs must live only under `generated/`, `build/`, or `site/`.
- Generated files are derived artifacts and must never be edited by hand.
- If a generated file is wrong, fix the source or generator and rebuild.
- Derived artifacts must remain reproducible from canonical source files and repository build scripts.
- If source and derived artifacts disagree, the source wins and the derived artifact must be regenerated.
- Delete obsolete derived artifacts, stale exports, and duplicate build clutter instead of preserving them.

## Anti-Sprawl Rules

- Do not add new top-level folders without recorded rationale in `decisions/`.
- Do not create duplicate templates, parallel schemas, parallel taxonomies, or alternate content pipelines.
- Reuse existing schema, taxonomy, and approved template structures instead of forking them.
- Do not copy canonical article content into `docs/`.
- Archive retired content instead of silently replacing or overwriting it.
- Prefer consolidation over expansion when resolving drift or inconsistency.

## Papyrus Product Rules

Papyrus is not just a file repository. It is a knowledge operations product.
Changes must preserve and strengthen the distinction between these layers:

- canonical knowledge objects
- entries or structured content within those objects
- taxonomic and policy controls
- ingestion and transformation flows
- operator-facing tools
- end-user reading surfaces

Do not flatten those concerns into one generic document model if the existing architecture intentionally separates them.

When changing product behaviour:

- preserve the distinction between canonical source content and rendered views
- preserve lifecycle state and auditability
- preserve traceability from displayed content back to canonical source
- prefer explicit structure over hidden inference
- prefer durable system rules over page-local hacks

## Role-Scoped Experience Rules

Papyrus must preserve strict separation between Reader, Operator, and Admin experiences.

- Do not implement cross-role UI by hiding or disabling shared controls inside one blended shell.
- Do not expose navigation, routes, actions, metadata panels, or search results to roles not explicitly permitted to see them.
- Treat route separation, visibility rules, and workflow boundaries as binding architecture.
- When touching navigation, routing, layouts, object views, or workflow actions, consult:
  - `decisions/role-experience-visibility-matrix.md`
  - `decisions/route-separation-and-experience-boundaries.md`
  - `decisions/layout-contracts-by-role.md`
  - `decisions/knowledge-workflows-and-lifecycle.md`
  - `decisions/experience-principles.md`
  - `decisions/actor-model-to-role-model-mapping.md`

## Product Experience Principle

Papyrus must present itself as a knowledge system, not a generic dashboard or generic text editor.
Interface-specific execution rules belong in subtree `AGENTS.md` files for the relevant application surfaces.

## Canonical Content Governance

Canonical knowledge content must comply with the governing schemas, taxonomies, templates, and lifecycle policy.
Detailed knowledge-object and metadata rules are defined in `knowledge/AGENTS.md`.
Changes to schemas or taxonomies require rationale recorded in `decisions/`.

## Ingestion and Transformation Rules

Papyrus may ingest external content, but imported material is not automatically canonical.

When working on importers, parsers, ingestion flows, or transformation pipelines:

- preserve provenance
- distinguish imported source from canonical normalised output
- do not discard metadata needed for audit or traceability
- map imported content into approved structures instead of inventing parallel storage formats
- fail early and clearly when source material cannot be mapped safely
- prefer explicit transformation stages over hidden mutation during render
- update documentation when ingestion capabilities, supported formats, or transformation guarantees change

## Documentation Rules

Documentation must explain the system that exists now, not the system that used to exist and not the system hoped for later.

When code, content model, generation flows, UX flows, or CLI commands change:

- update any affected documentation in the same task when practical
- remove stale claims rather than leaving drift in place
- verify examples, paths, and command names against implementation
- do not let README, docs, or diagrams overstate shipped capability

If documentation and implementation conflict, correct the documentation or fix the implementation before declaring completion.

## Working Rules

- Make the smallest correct change that resolves the issue at the source.
- Do not patch derived artifacts to simulate a fix.
- Do not perform broad rewrites when a targeted structural change will solve the problem cleanly.
- Do not rename, move, or split canonical content without updating references, generation flows, and rationale where required.
- When a task affects shared primitives, schemas, taxonomies, templates, or navigation architecture, plan first before editing.
- When touching UI, verify the affected route or flow directly instead of assuming a shared component change solved it everywhere.
- When touching generators or importers, verify both source correctness and regenerated output correctness.
- When touching documentation, verify that file paths, commands, and screenshots or examples still match the current repo.

## Commands

Keep this section current.
Replace placeholders with the exact repository commands and do not leave obsolete commands here.

- install: `./scripts/bootstrap.sh`
- dev web: `python3 scripts/run.py --operator`
- dev cli: `python3 scripts/operator_view.py queue --db build/knowledge.db`
- lint: `not separately configured; do not claim lint coverage until a dedicated lint command exists`
- typecheck: `not separately configured; do not claim typecheck coverage until a dedicated typecheck command exists`
- test: `python3 -m unittest discover -s tests`
- build: `./scripts/build.sh`
- validate content: `python3 scripts/validate.py`
- regenerate derived artifacts: `./scripts/build_static_export.sh`

Do not claim completion without running the relevant verification commands for the files changed.

## Completion Gate

Work is not complete until all applicable checks pass.

Minimum completion bar:

- validation passes
- relevant tests pass
- relevant lint and type checks pass
- build succeeds when build-relevant files changed
- derived artifacts are regenerated when required
- no canonical-versus-derived drift remains
- affected documentation is updated or explicitly confirmed current
- affected routes, views, or flows are manually checked for obvious regressions
- schema or taxonomy changes include rationale in `decisions/`

## Reporting Format

At the end of each task, report in this order:

1. summary of what changed
2. validation, lint, typecheck, test, and build results
3. documentation updated
4. unresolved risks, follow-up work, or intentional deferrals

Do not state or imply success without this evidence.

## Planning Trigger

Create a written plan before editing when the task:

- touches multiple top-level directories
- changes shared schemas, taxonomies, or templates
- changes ingestion or transformation behaviour
- restructures canonical content
- modifies generators, build flows, or publishing flows
- changes shared navigation, layout primitives, or design system rules
- has ambiguous source-of-truth implications
- is large enough that failure to sequence work would create drift or rework

## Subtree Guidance Expectations

Add deeper `AGENTS.md` files where local rules materially differ.
Strong candidates include:

- `apps/web/` for layout, navigation, reading mode, and design-system rules
- `apps/cli/` for command behaviour and output expectations
- `docs/` for documentation drift and evidence standards
- `knowledge/` for content object and lifecycle handling
- generator or importer directories for transformation-specific guardrails

The deeper file must narrow or extend these rules, not contradict them without explicit rationale.
