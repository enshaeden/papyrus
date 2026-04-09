# Getting Started

Use this path when you need a working Papyrus runtime quickly and want the lifecycle-guided operator path, not just the underlying repository surfaces.

## 1. Prepare The Environment

```bash
./scripts/bootstrap.sh
```

Outcome:
- The environment is bootstrapped.
- Canonical source validates cleanly.
- The local runtime database is rebuilt in `build/knowledge.db`.

Failure signals:
- `validate.py` reports schema, taxonomy, metadata, citation, or link errors.
- `build_index.py` cannot rebuild the runtime database.

## 2. Choose Your Entry Point

For the default operator path:

```bash
python3 scripts/run.py --operator
```

- Web entrypoint: local web root route `/`
- API entrypoint: local API health route `/health`
- Runtime DB: `build/knowledge.db`

What to expect:
- `/` is the lifecycle-guided home page.
- The home page shows likely next actions, work-area counts, recent activity, and the lifecycle model.
- Navigation is organized as `Read`, `Write`, `Import`, `Review / Approvals`, `Knowledge Health`, `Services`, and `Activity / History`.
- `/write` starts blueprint-driven section authoring.
- `/ingest` starts the upload, parse, classify, map, review, and convert flow for external files.

For terminal-first work:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
python3 scripts/operator_view.py review <object_id> <revision_id> --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db --format json
```

For structured drafting and import from the terminal:

```bash
python3 scripts/operator_view.py create-draft --type runbook --object-id kb-example --title "Example" --summary "Example" --owner service_owner --team "IT Operations" --canonical-path knowledge/examples/example.md
python3 scripts/operator_view.py edit-section --object kb-example --revision <revision_id> --section purpose --field use_when="Use this when the blueprint applies."
python3 scripts/operator_view.py show-progress --object kb-example --revision <revision_id>
python3 scripts/ingest.py path/to/source.docx
python3 scripts/operator_view.py list-ingestions --db build/knowledge.db
python3 scripts/operator_view.py review-ingestion <ingestion_id> --db build/knowledge.db
```

For a fast demo/runtime review path:

```bash
python3 scripts/run.py --demo
python3 scripts/run_scenario.py service-degradation
python3 scripts/operator_view.py queue --db build/demo-knowledge.db
python3 scripts/operator_view.py health --db build/demo-knowledge.db
```

For advanced surface-specific startup:

```bash
python3 scripts/serve_web.py --db build/knowledge.db --source-root .
python3 scripts/serve_api.py --db build/knowledge.db --source-root .
```

Guardrail:
- `python3 scripts/run.py --operator` only permits the canonical repository source root for writeback. Use `--demo` for sandboxed writable source roots.
- `python3 scripts/serve_web.py` and `python3 scripts/serve_api.py` also reject non-canonical source roots unless you pass `--allow-noncanonical-source-root`.
- If you embed the WSGI apps directly in tests or local tooling, `papyrus.interfaces.web.app(...)` and `papyrus.interfaces.api.app(...)` enforce the same rule. Use `allow_noncanonical_source_root=True` only for sandboxed demo/test roots.

## 3. Pick The Right Playbook

- Need to find or verify current guidance safely: [Read](playbooks/read.md)
- Need to create, import, or revise lifecycle-managed guidance: [Write](playbooks/write.md)
- Need to make review or stewardship decisions: [Manage](playbooks/manage.md)

## 4. Use The Right Source

- Canonical knowledge lives in `knowledge/` and `archive/knowledge/`.
- Repository decisions live in `decisions/`.
- Operator and reference docs live in `docs/`.
- Derived output in `generated/`, `build/`, and `site/` is rebuildable and not authoritative.
- Approved revisions write back deterministically to canonical Markdown through the governed application layer.
- Papyrus constructs drafts from blueprints and converts imported files into the same draft model after review.
- Writeback is inspectable: use review pages or `scripts/source_sync.py preview` before approval or explicit source sync, and use `scripts/source_sync.py restore-last` when you need to recover the previous canonical state.
