# Papyrus

Papyrus is a local-first operational knowledge control plane for IT support and systems operations. It keeps canonical knowledge in Markdown under `knowledge/` and `archive/knowledge/`, builds a relational runtime on top of that source, constructs new knowledge through blueprint-driven authoring, and converts external documents into governed drafts without turning generated output into the source of truth.

## Repository Boundary

- Canonical source of truth lives in `knowledge/` and `archive/knowledge/`.
- Repository documentation lives in `docs/`.
- Repository decisions live in `decisions/`, except the active experience-governance records that live in `docs/decisions/`.
- `build/`, `generated/`, and `site/` are derived state. They are rebuildable and must not be treated as canonical source.
- Generated ingestion artifacts under `build/ingestions/` are reviewable runtime artifacts, not source of truth.
- Demo mode may create a disposable writable source root under `build/demo-source/`; it is regenerated local state, not repository source.
- Governed runtime mutations now persist explicit lifecycle state fields: `object_lifecycle_state`, `revision_review_state`, `draft_progress_state`, `ingestion_state`, and `source_sync_state`.

## Core Questions

- What is the current guidance?
- What should I do next?
- Is this safe to use right now?
- Why should we trust it?
- Who owns and reviewed it?
- What changed that may have invalidated it?
- What else is affected by this object or service?

## Experience Surfaces

- Reader routes: `/reader/browse`, `/reader/object/{object_id}`
- Operator routes: `/operator`, `/operator/read`, `/operator/write/new`, `/operator/import`, `/operator/review`, `/operator/review/governance`, `/operator/read/services`, `/operator/review/activity`
- Admin routes: `/admin/overview`, `/admin/inspect`, `/admin/review`, `/admin/governance`, `/admin/services`, `/admin/audit`

Legacy shared routes still redirect to operator-scoped routes during migration.
They are compatibility shims, not the stable product contract.

## Experience Direction

Papyrus uses strict role-scoped experiences for Reader, Operator, and Admin.
Local actor IDs remain useful for audit records, demo data, and development overlays, but they are not separate shipped product experiences.

Experience architecture is governed by the active records in `docs/decisions/`, especially:

- `docs/decisions/experience-principles.md`
- `docs/decisions/role-experience-visibility-matrix.md`
- `docs/decisions/route-separation-and-experience-boundaries.md`
- `docs/decisions/knowledge-workflows-and-lifecycle.md`

## Short Start

```bash
./scripts/bootstrap.sh
python3 scripts/run.py --operator
```

Start at `/operator` for the operator home surface.
Reader and Admin surfaces are mounted under `/reader/*` and `/admin/*`.

Primary authoring rules:

- no generic rich-text editor as the main authoring surface
- no direct freeform document blob storage for drafts
- guided section editing is the primary web authoring path
- guided drafting stays on the shared `normal` shell rather than a separate focus shell
- guided draft creation is explicit in the web surface: object setup eagerly creates the first draft, and later draft entrypoints use the governed start action instead of GET-side effects
- the bulk draft fallback remains a transitional operator route only because the guided path does not yet own searchable citation and multi-select controls; do not add new lifecycle or policy meaning there
- authored and imported drafts both converge on the same structured revision model
- imports stay in reviewable ingestion jobs until a human converts them into a draft
- browser upload is the normal web ingest path; browser-submitted local file paths stay disabled unless a local operator explicitly enables them
- PDF import is limited to text-based PDFs; scanned or image-only PDFs require external OCR or preprocessing and will surface degraded extraction warnings

Contract-driven surface boundary:

- `papyrus.application.ui_projection`, workflow projections, and action descriptors define governed status, safe-to-use guidance, action availability, operator messaging, and acknowledgement requirements.
- CLI, API, and web render those contracts. They may format the output differently, but they must not derive governed meaning from raw database state, presenter regexes, or template-local policy rules.
- If a surface needs truth that is not present in the current contract, extend the backend contract or projection first. Do not add page-local lifecycle, acknowledgement, or policy logic as a workaround.
- Guided authoring GET routes are load-only. Web draft creation or reuse must flow through application-owned helpers and explicit start actions, not route-local guesses.

Current UX shape:

- route groups and navigation are role-scoped rather than actor-switched
- the web shell keeps Papyrus brand contrast centered on the plum/aubergine topbar, branded active states, and stronger command surfaces rather than low-contrast neutral chrome
- `Read` is split into a search/select workspace and a blueprint-aware article surface
- governance stays available as secondary context instead of dominating the top of every page
- `Services`, `Review`, `Knowledge Health`, and `Activity` each use distinct layouts and decision models

For terminal-first operator checks:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db
```

For structured drafting and import:

```bash
python3 scripts/operator_view.py create-draft --type runbook --object-id kb-example --title "Example" --summary "Example" --owner service_owner --team "IT Operations" --canonical-path knowledge/examples/example.md
python3 scripts/operator_view.py edit-section --object kb-example --revision <revision_id> --section purpose --field use_when="Use this when the blueprint applies."
python3 scripts/operator_view.py show-progress --object kb-example --revision <revision_id>
python3 scripts/ingest.py path/to/source.docx
python3 scripts/operator_view.py list-ingestions --db build/knowledge.db
```

For a review/demo runtime with realistic workflow tension:

```bash
python3 scripts/run.py --demo
python3 scripts/run_scenario.py service-degradation
```

Source sync inspection and recovery remain explicit:

```bash
python3 scripts/source_sync.py preview --object kb-troubleshooting-vpn-connectivity
python3 scripts/source_sync.py writeback --object kb-troubleshooting-vpn-connectivity
python3 scripts/source_sync.py restore-last --object kb-troubleshooting-vpn-connectivity
python3 scripts/source_sync.py writeback-all
python3 scripts/ingest_event.py --type service_change --entity Remote\\ Access --payload payload.json
python3 scripts/operator_view.py activity --db build/knowledge.db --format json
python3 scripts/serve_web.py --db build/knowledge.db --source-root .
python3 scripts/serve_api.py --db build/knowledge.db --source-root .
```

`scripts/serve_api.py` remains an operator-oriented local API surface.
It is not currently documented as a separate role-scoped public API contract.

Guardrail:
- `scripts/run.py --operator` only permits the canonical repository source root for governed writeback and draft validation. Use `--demo` for sandboxed writable roots.
- `scripts/serve_web.py`, `scripts/serve_api.py`, and `scripts/operator_view.py` accept `--source-root` but reject non-canonical roots unless you explicitly pass `--allow-noncanonical-source-root`.
- The same source-root policy now runs inside `papyrus.interfaces.web.app(...)`, `papyrus.interfaces.api.app(...)`, and the operator CLI. Test or demo embeddings must opt in explicitly with `allow_noncanonical_source_root=True`.
- Browser-submitted local path ingest is off by default. Enable it only on a trusted local operator web surface with `--allow-web-ingest-local-paths`.
- When local-path ingest is enabled, Papyrus still restricts reads to allowlisted roots from `schemas/repository_policy.yml`. The default read roots are `build/local-ingest/` and `migration/`.
- Source sync is journaled under `build/mutations/`. Operator startup and governed mutation entry points run pending mutation recovery before continuing. Recovery reclaims stale journals and stale locks when it can do so safely, and fails closed with an explicit operator-facing reason when it cannot.
- Preview, apply, restore, and archive report the proposed or recorded `source_sync_state`, transition payload, required acknowledgements, and any assumptions invalidated by the mutation. If live canonical Markdown drifted, Papyrus marks the object `conflicted` instead of silently overwriting it.

## Operator Docs

- Start here: [docs/getting-started.md](docs/getting-started.md)
- Read playbook: [docs/playbooks/read.md](docs/playbooks/read.md)
- Write playbook: [docs/playbooks/write.md](docs/playbooks/write.md)
- Manage playbook: [docs/playbooks/manage.md](docs/playbooks/manage.md)
- System model: [docs/reference/system-model.md](docs/reference/system-model.md)
- Operator readiness: [docs/reference/operator-readiness.md](docs/reference/operator-readiness.md)
- Operator governance and decisions: [docs/decisions/index.md](docs/decisions/index.md)
