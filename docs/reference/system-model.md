# System Model

Use this page when you need the minimum shared model behind Papyrus. Each rule is defined once here so operators do not have to reconstruct the system from multiple architecture notes.

## Operating Boundary

Papyrus keeps governed mutation meaning in shared backend contracts, rebuildable derived state, and two governed construction flows:

- Canonical source: Markdown knowledge under `knowledge/` and `archive/knowledge/`
- Runtime derived state: rebuildable relational state and local workbench artifacts under `build/` used for validation, search, reporting, revision history, trust, governance views, ingestion review, and demo seeding
- Export derived state: approved-content publication output under `generated/` and `site/`
- Blueprint authoring flow: structured draft creation and revision driven by blueprint sections
- Import workbench flow: upload, parse with extraction warnings and quality signals, classify, generate and review mapping, and convert external files into the same structured draft model

If these layers disagree, canonical source wins and the runtime or export must be rebuilt.

## Reference

| Topic | What It Is | Why It Exists | What Breaks If Misunderstood |
| --- | --- | --- | --- |
| Knowledge object model | Papyrus treats runbooks, known errors, service records, policies, and system designs as first-class knowledge objects with stable identity. | Stable identity lets the runtime track revisions, relationships, services, and evidence over time. | Duplicate or forked objects fragment history, trust, and ownership. |
| Blueprint model | Blueprints define section structure, ordering, required content, validation rules, evidence requirements, and lifecycle defaults for each knowledge object type. | Papyrus needs one central definition of valid operational knowledge instead of ad-hoc form rules or freeform blobs. | Different surfaces drift, validation becomes inconsistent, and drafts stop converging on a reliable structure. |
| Blueprint versus template boundary | Approved templates may still scaffold source files, but blueprints are the authoritative structure for guided authoring and ingestion. | Source scaffolding and runtime authoring solve different problems and should not be confused. | Operators mistake a file scaffold for governed authoring behavior and bypass progress, validation, or evidence expectations. |
| Source sync | Approved revisions can write back to canonical Markdown through a journaled mutation flow with explicit `source_sync_state`. Preview and apply run canonical-path policy, conflict detection, and recovery rules before changing source. | Runtime governance must close the loop back to the authoritative source without manual sync work or silent overwrite. | Runtime and source drift, hostile path handling bugs, reviewers approve one state while operators read another, or people patch files outside the governed path. |
| Revision lifecycle | Revisions move independently of object lifecycle so draft, in-review, approved, rejected, and superseded states can be tracked cleanly. | Review decisions apply to a revision, not to an abstract file snapshot. | Review history becomes ambiguous and operators cannot tell which version was approved. |
| Unified draft model | Native drafts and imported drafts both use the same runtime revision shape with `blueprint_id`, structured section content, completion state, and derived Markdown. | Papyrus should not carry a separate imported-content lifecycle after conversion. | Imported content behaves like a special case, lifecycle rules diverge, and review posture becomes inconsistent. |
| Object lifecycle | Source objects still use `draft`, `active`, `deprecated`, and `archived` lifecycle states. | Lifecycle answers whether the object should appear in normal operational use. | Deprecated or archived guidance may be treated as current, or active guidance may disappear from the wrong views. |
| Trust model | Trust posture is separate from lifecycle and can degrade to `suspect`, `stale`, or `weak_evidence`. | Operators need to know whether current guidance is safe to rely on, not just whether it exists. | Active objects may be used even when evidence is broken, ownership is unclear, or upstream change invalidated them. |
| Citation model | Citations are runtime-tracked evidence records tied to claims and targets, not passive front matter decoration. Governed Papyrus references are lightweight internal references, while stronger external or manual evidence depends on capture metadata and any required snapshot. | Evidence needs to stay inspectable, degradable, and auditable as targets change. | Broken, vague, migration-era, or weakly captured citations can be mistaken for healthy evidence. |
| Ingestion model | External files are stored as ingestion jobs with normalized artifacts, parser warnings, extraction quality, classification output, mapping review, and explicit conversion into a draft. PDF support is limited to text-based PDFs; degraded extraction, mapping conflicts, low-confidence matches, and unmapped content stay visible before conversion. | Imported content must be inspectable and reviewable before it can influence canonical knowledge. | Low-signal parse output, mapping conflicts, or unmapped content get hidden and governance review starts after structure has already drifted. |
| Event model | Structured change, validation, and evidence events are ingested locally and stored in the runtime. | Papyrus needs explicit change inputs before it can propagate consequence and queue revalidation work. | Trust degradation becomes hidden, impact reasoning stays anecdotal, and operators cannot trace why posture changed. |
| Accountability model | Governed actions always record an actor. Web, API, CLI, demo, and scenario flows all route actor identity through the application layer. | Review, rejection, evidence, and source updates need a clear accountable actor in audit history. | Audit trails become ambiguous and governance actions cannot be defended or replayed safely. |
| Variant modeling | Shared procedures should live once, while site or room differences stay in overview pages, access pages, or narrowly scoped exceptions. | A single base procedure reduces drift and keeps local deltas visible without forking the workflow body. | Operators update one site copy and assume the family changed everywhere, leaving hidden divergence in sibling articles. |
| Validation and reporting | Validation enforces schema, taxonomy, metadata, link, citation, and repository rules; reporting exposes stale, duplicate, broken, isolated, or suspect content. | Papyrus depends on controlled structure and visible drift signals. | Invalid or low-quality knowledge enters the corpus and governance problems stay hidden. |
| Runtime versus source of truth | The runtime is a rebuildable projection of canonical source plus governance state. | Search, trust, queue, and impact views need relational state without making generated data authoritative. | People patch derived state by hand or trust stale runtime output over source. |
| Export model | Static export is an approval-gated publication surface for approved knowledge only. | Publishing and browseability are useful, but they are not the operational control plane. | Draft or unreviewed material leaks into published output, or operators mistake export pages for the live governance surface. |

## Explicit State Machines

- `object_lifecycle_state`: `draft -> active -> deprecated -> archived`
- `revision_review_state`: `draft -> in_review -> approved`, `in_review -> rejected`, `approved -> superseded`, `rejected -> draft`
- `draft_progress_state`: `blocked`, `in_progress`, `ready_for_review`
- `ingestion_state`: `uploaded -> parsed -> classified -> mapped -> converted`
- `source_sync_state`: `not_required`, `pending`, `applied`, `conflicted`, `restored`

Papyrus does not treat compatibility aliases such as `status`, `revision_state`, `draft_state`, or `approval_state` as part of the knowledge-object contract. Knowledge-object surfaces use the explicit lifecycle and review state fields directly.

## Backend/UI Cut Line

- Backend contracts define governed meaning. `papyrus.domain.lifecycle`, `papyrus.application.policy_authority`, `papyrus.application.ui_projection`, workflow projections, and action descriptors decide lifecycle semantics, safe-to-use guidance, operator messages, and acknowledgement requirements.
- CLI, API, and web render those contracts. They may choose different presentation formats, but they should not compute governed action availability, acknowledgement rules, or lifecycle meaning from raw database state.
- If a surface needs governed truth that is missing, add it to the backend contract or projection layer first.

## Commands That Exercise The Model

```bash
python3 scripts/validate.py
python3 scripts/build_index.py
python3 scripts/ingest.py path/to/source.md
python3 scripts/operator_view.py create-draft --type runbook --object-id kb-example --title "Example" --summary "Example" --owner service_owner --team "IT Operations" --canonical-path knowledge/examples/example.md
python3 scripts/operator_view.py show-progress --object kb-example --revision <revision_id>
python3 scripts/operator_view.py list-ingestions
python3 scripts/report_stale.py
python3 scripts/report_content_health.py --section citation-health --section suspect-objects
python3 scripts/run.py --operator
python3 scripts/source_sync.py writeback-all
python3 scripts/ingest_event.py --type service_change --entity Remote\\ Access --payload payload.json
python3 scripts/operator_view.py events --db build/knowledge.db --format json
./scripts/build_static_export.sh
```

## Practical Rules

- Edit canonical knowledge in `knowledge/` or `archive/knowledge/`.
- Start new authoring from a blueprint, not from a blank editor.
- Route external documents through the import workbench before they become drafts.
- In web mode, browser upload is the normal import path; browser-submitted local file reads require explicit local-operator opt-in, an absolute host path, and an allowlisted local read root.
- Use guided section editing as the primary web authoring path. Citation lookup and searchable multi-select controls now live inside the guided flow.
- Do not reintroduce route-local policy checks, template-local acknowledgement rules, or page-local governed action availability logic.
- Treat `build/ingestions/` and any demo source created under `build/` as disposable runtime artifacts, not repository source.
- Use governed source sync rather than manual file sync when an approved runtime revision becomes canonical.
- Prefer one canonical procedure plus linked site deltas over copy-based regional variants.
- Do not patch generated files in `generated/`, `build/`, or `site/`.
- Validate before treating a revision as ready.
- Use queue, trust, revision, service, event, evidence, and impact views to govern runtime posture.
- Use the static export for approved publication, not for live review or trust decisions.
