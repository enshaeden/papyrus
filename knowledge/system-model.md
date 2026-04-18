# System Model

Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.

Use this page when you need the minimum shared model behind Papyrus. Each rule is defined once here so operators do not have to reconstruct the system from multiple architecture notes.

## Operating Boundary

Papyrus keeps governed mutation meaning in shared backend contracts, rebuildable derived state, and two governed construction flows:

- Canonical source: explicit workspace Markdown knowledge under trees such as `knowledge/` and `archive/knowledge/`
- Runtime derived state: relational state and local workbench artifacts under `build/` used for validation, search, reporting, revision history, trust, governance views, ingestion review, and demo seeding
- Derived build outputs: artifacts under `generated/` for retained runtime and build contracts such as the route map
- Blueprint authoring flow: structured draft creation and revision driven by blueprint sections
- Import flow: upload, parse with extraction warnings and quality signals, classify, generate and review mapping, and convert external files into the same structured draft model

If these layers disagree, canonical source wins and the runtime or derived build output must be rebuilt.

Read-only runtime boundary:

- Runtime startup depends on the runtime database plus retained runtime artifacts such as `generated/route-map.json` and `generated/route-map.md`.
- Read-only runtime does not require a repo-local canonical corpus.
- Source-backed authoring, ingest conversion, source sync, and other canonical-source mutations require an explicit workspace source root.

## Reference

| Topic | What It Is | Why It Exists | What Breaks If Misunderstood |
| --- | --- | --- | --- |
| Knowledge object model | Papyrus supports typed knowledge objects with stable identity, governed revisions, relationships, services, citations, and evidence posture. | Stable identity lets the runtime track revisions, relationships, services, and evidence over time without flattening everything into one generic document blob. | Duplicate or forked objects fragment history, trust, and ownership. |
| Blueprint model | Blueprints define section structure, ordering, required content, validation rules, evidence requirements, lifecycle defaults, and authoring scope. | Papyrus needs one central definition of valid operational knowledge instead of ad-hoc form rules or freeform blobs. | Different surfaces drift and validation becomes inconsistent. |
| Blueprint versus template boundary | Approved templates may scaffold source files, but blueprints are the authoritative structure for guided authoring and ingestion. | Source scaffolding and runtime authoring solve different problems and should not be confused. | Operators mistake a file scaffold for governed authoring behavior and bypass progress, validation, or evidence expectations. |
| Source sync | Approved revisions can write back to canonical Markdown through a journaled mutation flow with explicit `source_sync_state`. | Runtime governance must close the loop back to authoritative source without silent overwrite. | Runtime and source drift or people patch files outside the governed path. |
| Revision lifecycle | Revisions move independently of object lifecycle so `in_progress`, `in_review`, `approved`, `rejected`, and `superseded` can be tracked cleanly. | Review decisions apply to a revision, not to an abstract file snapshot. | Review history becomes ambiguous. |
| Draft progress | Draft readiness is separate from review state and is stored as optional `draft_progress_state`. | Papyrus needs to distinguish drafting readiness from actual review queue state. | The system blurs blocked work with in-review work. |
| Object lifecycle | Source objects use `draft`, `active`, `deprecated`, and `archived`. | Lifecycle answers whether the object should appear in normal operational use. | Deprecated or archived guidance may be treated as current. |
| Trust model | Trust posture is separate from lifecycle and can degrade to `suspect`, `stale`, or `weak_evidence`. | Operators need to know whether current guidance is safe to rely on, not just whether it exists. | Active objects may be used even when evidence is broken or ownership is unclear. |
| Citation model | Citations are runtime-tracked evidence records tied to claims and targets, not passive front matter decoration. | Evidence needs to stay inspectable, degradable, and auditable as targets change. | Broken or weak citations can be mistaken for healthy evidence. |
| Ingestion model | External files are stored as ingestion jobs with normalized artifacts, parser warnings, extraction quality, classification output, mapping review, and explicit conversion into a draft. | Imported content must be inspectable and reviewable before it can influence canonical knowledge. | Low-signal parse output or mapping conflicts get hidden before review. |
| Accountability model | Governed actions always record an actor. Web, API, CLI, demo, and scenario flows all route actor identity through the application layer. | Review, rejection, evidence, and source updates need a clear accountable actor in audit history. | Audit trails become ambiguous. |
| Runtime versus source of truth | The runtime is a rebuildable projection backed by the runtime database plus retained derived artifacts, while canonical source remains in workspace source trees. | Search, trust, queue, and impact views need relational state without making generated data authoritative or requiring source trees in the shipped runtime image. | People patch derived state by hand or couple runtime startup to repo-local Markdown. |

## Explicit State Machines

- `object_lifecycle_state`: `draft -> active -> deprecated -> archived`
- `revision_review_state`: `in_progress -> in_review -> approved`, `in_review -> rejected`, `approved -> superseded`, `rejected -> in_progress`
- `draft_progress_state`: optional until evaluated, then `blocked` or `ready_for_review`
- `ingestion_state`: `uploaded -> parsed -> classified -> mapped -> converted`
- `source_sync_state`: `not_required`, `pending`, `applied`, `conflicted`, `restored`

Papyrus does not treat compatibility aliases such as `status`, `revision_state`, `draft_state`, or `approval_state` as part of the knowledge-object contract. Knowledge-object surfaces use the explicit lifecycle and review state fields directly.

## Backend/UI Cut Line

- Backend contracts define governed meaning. `papyrus.domain.lifecycle`, `papyrus.application.policy_authority`, `papyrus.application.ui_projection`, workflow projections, and action descriptors decide lifecycle semantics, safe-to-use guidance, operator messages, and acknowledgement requirements.
- CLI, API, and web render those contracts. They may choose different presentation formats, but they should not compute governed action availability, acknowledgement rules, or lifecycle meaning from raw database state.
- The JSON API remains an operator-oriented local surface. It is not part of the role-scoped web route contract, and role-prefixed API aliases require a separate decision and migration.
- If a surface needs governed truth that is missing, add it to the backend contract or projection layer first.
- Guided web authoring follows the same rule: GET routes load existing revision context only, while draft creation or reuse semantics live in the application layer and are reached through explicit start actions.

## Commands That Exercise The Model

```bash
python3 scripts/validate.py
python3 scripts/build_index.py --source-root /path/to/workspace
python3 scripts/ingest.py --source-root /path/to/workspace path/to/source.md
python3 scripts/operator_view.py create-draft --db build/knowledge.db --source-root /path/to/workspace --type runbook --object-id kb-example --title "Example" --summary "Example" --owner it_operations --team "IT Operations" --canonical-path knowledge/examples/example.md
python3 scripts/operator_view.py show-progress --db build/knowledge.db --source-root /path/to/workspace --object kb-example --revision <revision_id>
python3 scripts/operator_view.py list-ingestions
python3 scripts/report_stale.py
python3 scripts/report_content_health.py --section citation-health --section suspect-objects
python3 scripts/run.py --operator
python3 scripts/source_sync.py --source-root /path/to/workspace writeback-all
python3 scripts/ingest_event.py --type service_change --entity Remote\\ Access --payload payload.json
python3 scripts/operator_view.py events --db build/knowledge.db --format json
```

## Practical Rules

- Edit canonical knowledge only in the explicit workspace source tree supplied for source-backed operations.
- Start new authoring from the primary template set.
- Route external documents through the import workbench before they become drafts.
- In web mode, browser upload is the normal import path; browser-submitted local file reads require explicit local-operator opt-in, an absolute host path, and an allowlisted local read root.
- Use guided section editing as the primary web authoring path. Citation lookup and searchable multi-select controls live inside the guided flow.
- Do not reintroduce route-local policy checks, template-local acknowledgement rules, or page-local governed action availability logic.
- Treat `build/ingestions/` and any demo source created under `build/` as disposable runtime artifacts, not repository source.
- Use governed source sync rather than manual file sync when an approved runtime revision becomes canonical.
- Do not require repo-local source trees to boot read-only runtime surfaces.
- Do not patch generated files in `generated/` or `build/`.
- Validate before treating a revision as ready.
- Use review, governance, service, event, evidence, and impact views to govern runtime posture.
- There is no separate MkDocs or static-export publication surface; Readers consume dependable content through the runtime product.
