# Papyrus

Papyrus is a local-first operational knowledge control plane for IT support and systems operations. It keeps canonical knowledge in Markdown under `knowledge/` and `archive/knowledge/`, builds a relational runtime on top of that source, constructs new knowledge through blueprint-driven authoring, and converts external documents into governed drafts without turning generated output into the source of truth.

## Repository Boundary

- Canonical source of truth lives in `knowledge/` and `archive/knowledge/`.
- Repository documentation lives in `docs/`, and repository decisions live in `decisions/`.
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

## Use Modes

- `Read`: find the right runbook, known error, service record, policy, or system design and decide whether it is safe to use now.
- `Write`: create an object shell, choose a blueprint, complete guided sections, record citations and evidence posture, validate progress, and submit the draft for review.
- `Import`: upload Markdown, DOCX, or text-based PDF files; inspect parser warnings, extraction quality, mapping gaps, and mapping conflicts; and convert reviewed imports into the same draft lifecycle used by native authoring.
- `Review / Approvals`: inspect what changed, what evidence supports it, what is unresolved, and whether it should become canonical guidance.
- `Knowledge Health`: monitor stale guidance, weak evidence, suspect objects, and review pressure as stewardship work.
- `Services`: move from a service context into the right operational guidance path.
- `Activity / History`: understand what changed, what it affected, and what now needs review or revalidation.

## Short Start

```bash
./scripts/bootstrap.sh
python3 scripts/run.py --operator
```

Start at the web home page. Papyrus now opens on a lifecycle-guided landing page instead of dropping straight into a raw queue.

Primary authoring rules:

- no generic rich-text editor as the main authoring surface
- no direct freeform document blob storage for drafts
- guided section editing is the primary web authoring path
- the bulk draft fallback is a separate operator route for cross-section editing, citation lookup, and searchable multi-select helpers
- authored and imported drafts both converge on the same structured revision model
- imports stay in reviewable ingestion jobs until a human converts them into a draft
- browser upload is the normal web ingest path; browser-submitted local file paths stay disabled unless a local operator explicitly enables them
- PDF import is limited to text-based PDFs; scanned or image-only PDFs require external OCR or preprocessing and will surface degraded extraction warnings

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

Guardrail:
- `scripts/run.py --operator` only permits the canonical repository source root for governed writeback and draft validation. Use `--demo` for sandboxed writable roots.
- `scripts/serve_web.py`, `scripts/serve_api.py`, and `scripts/operator_view.py` accept `--source-root` but reject non-canonical roots unless you explicitly pass `--allow-noncanonical-source-root`.
- The same source-root policy now runs inside `papyrus.interfaces.web.app(...)`, `papyrus.interfaces.api.app(...)`, and the operator CLI. Test or demo embeddings must opt in explicitly with `allow_noncanonical_source_root=True`.
- Browser-submitted local path ingest is off by default. Enable it only on a trusted local operator web surface with `--allow-web-ingest-local-paths`.
- When local-path ingest is enabled, Papyrus still restricts reads to allowlisted roots from `schemas/repository_policy.yml`. The default read roots are `build/local-ingest/` and `migration/`.
- Source sync is journaled under `build/mutations/`. Preview and apply report the proposed `source_sync_state`, required acknowledgements, and any assumptions invalidated by the mutation. If live canonical Markdown drifted, Papyrus marks the object `conflicted` instead of silently overwriting it.

## Operator Docs

- Start here: [docs/getting-started.md](docs/getting-started.md)
- Read playbook: [docs/playbooks/read.md](docs/playbooks/read.md)
- Write playbook: [docs/playbooks/write.md](docs/playbooks/write.md)
- Manage playbook: [docs/playbooks/manage.md](docs/playbooks/manage.md)
- System model: [docs/reference/system-model.md](docs/reference/system-model.md)
- Operator readiness: [docs/reference/operator-readiness.md](docs/reference/operator-readiness.md)
- Operator governance and decisions: [decisions/index.md](decisions/index.md)
