# Getting Started

Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.

Use this path when you need a working Papyrus runtime quickly and want the current operator workflow, not just the underlying repository surfaces.

The committed seed corpus was removed from this repository. When you need source-backed authoring or sync, point Papyrus at an explicit external workspace root that contains trees such as `knowledge/` and `archive/knowledge/`.

## 1. Prepare The Environment

```bash
./scripts/bootstrap.sh
```

Outcome:

- The environment is bootstrapped.
- Formatter, lint, and type-check tooling are installed into `.venv/`.
- Repository policy, knowledge-model files, system knowledge docs, route-map artifacts, and runtime dependencies validate cleanly.
- Any content created under `build/` remains local derived state and is not source of truth.
- Read-only runtime can later start from `build/knowledge.db` plus retained derived artifacts without any repo-local knowledge corpus.

Failure signals:

- `validate.py` reports schema, taxonomy, metadata, citation, or link errors.
- `build_index.py --source-root /path/to/workspace` cannot rebuild the runtime database when you run a source-backed build.

## 2. Choose Your Entry Point

For the default operator path:

```bash
python3 scripts/build_index.py --source-root /path/to/workspace
python3 scripts/run.py --operator
```

- Shared application entrypoint: `/`
- Reader landing: `/read`
- Operator landing: `/review`
- Admin landing: `/admin/overview`
- API entrypoint: local API health route `/health`
- Runtime DB: `build/knowledge.db`
- Read-only startup does not require `knowledge/` or `archive/knowledge/` when the runtime DB and retained runtime artifacts are already present.

What to expect:

- Reader-visible reading surfaces use canonical paths under `/read`.
- Operator work surfaces use canonical paths under `/write`, `/import`, `/review`, and `/governance`.
- Admin control surfaces use canonical paths such as `/admin/overview`, `/admin/users`, and `/admin/audit`.
- Request-scoped role context comes from runtime or authenticated identity, not from path prefixes.
- `/write/new` starts the primary template flow for runbooks, known errors, and service records.
- `/write` resolves to the canonical authoring entrypoint.
- Guided drafting stays on the shared `normal` shell, so sidebar navigation and the top bar remain visible while you author.
- `/import` starts the guided upload, extract, map, review, and convert flow for external files before draft creation.
- Browser upload is the normal web ingest path. Browser-submitted local file paths are disabled unless you explicitly enable `--allow-web-ingest-local-paths` on the local operator web surface.
- Import accepts Markdown, plain text, reStructuredText, RTF, DOCX, ODT, HTML, CSV, and text-based PDFs through the same local workflow.
- Read, write, import, review, and governance screens consume backend projection and action contracts. If a screen needs governed truth that is missing, extend the backend contract layer rather than adding route-local lifecycle logic.

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
python3 scripts/operator_view.py create-draft --db build/knowledge.db --source-root /path/to/workspace --type runbook --object-id kb-example --title "Example" --summary "Example" --owner it_operations --team "IT Operations" --canonical-path knowledge/examples/example.md
python3 scripts/operator_view.py edit-section --db build/knowledge.db --source-root /path/to/workspace --object kb-example --revision <revision_id> --section purpose --field use_when="Use this when the blueprint applies."
python3 scripts/operator_view.py show-progress --db build/knowledge.db --source-root /path/to/workspace --object kb-example --revision <revision_id>
python3 scripts/ingest.py --source-root /path/to/workspace path/to/source.docx
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

Guardrail:

- `python3 scripts/run.py --operator`, `python3 scripts/serve_web.py`, and `python3 scripts/serve_api.py` can start read-only runtime surfaces without a workspace source root.
- Source-backed commands and routes require `--source-root` or an equivalent workspace source root value when they author drafts, ingest for conversion, write back approved revisions, or restore canonical source.
- Workspace-scoped mutation entry points run pending mutation recovery before they proceed. Papyrus rolls back or reclaims stale journals and stale locks when safe, and blocks the operation with an explicit error when recovery cannot prove a safe result.
- Browser-submitted local path ingestion is off by default. Enable it only on a trusted local operator web surface with `python3 scripts/run.py --operator --allow-web-ingest-local-paths` or `python3 scripts/serve_web.py --allow-web-ingest-local-paths`.
- When web local-path ingest is enabled, Papyrus reads an absolute path from the machine running Papyrus, not from the browser device.
- Local-path ingest is still confined to allowlisted read roots from `knowledge_engine/schemas/repository_policy.yml`. The default read root is `build/local-ingest/`.
- If you embed the WSGI apps directly in tests or local tooling, `papyrus.interfaces.web.app(...)` and `papyrus.interfaces.api.app(...)` can be initialized without a workspace source root for read-only use.
- `papyrus.interfaces.api.app(...)` remains operator-oriented. It is not part of the role-scoped web experience contract.
- Any future role-scoped API contract requires a separate decision and migration.

## 3. Pick The Right Playbook

- Need to find or verify current guidance safely: [Read](read.md)
- Need to create, import, or revise lifecycle-managed guidance: [Write](write.md)
- Need to make review, governance, or admin decisions: [Review And Governance](manage.md)

## 4. Use The Right Source

- Canonical knowledge is not committed to this repository. When source-backed workflows are in scope, it lives in the explicit workspace source root you pass to Papyrus.
- Papyrus system knowledge in this repository lives under `knowledge/`.
- `knowledge_engine/` is the repository authority for `knowledge_engine/schemas/`, `knowledge_engine/taxonomies/`, `knowledge_engine/templates/`, and repository policy.
- Repository decisions live in `decisions/`.
- `docs/` is reserved for future governed production-content structure, scaffolding, and guidance files in this repository state.
- Derived output in `generated/` and `build/` is rebuildable and not authoritative.
- Read-only runtime depends on `build/knowledge.db` plus retained runtime artifacts such as `generated/route-map.json` and `generated/route-map.md`.
- Generated ingestion artifacts in `build/ingestions/` are reviewable runtime state, not source of truth.
- Demo source created under `build/demo-source/` is disposable local state, not canonical repository content.
- Approved revisions can become canonical Markdown through a governed source-sync mutation. Papyrus records a mutation journal under `build/mutations/`, persists explicit `source_sync_state`, and rejects root escapes or symlink traversal for governed source paths.
- Governed mutation contracts carry operator messages, transition payloads, and required acknowledgements. CLI, API, and web should display those contracts instead of restating the rules locally.
- Papyrus constructs drafts from the primary template set for the default web authoring flow and converts imported files into the same draft model after review.
- Source sync is inspectable: use review pages or `scripts/source_sync.py preview` before approval or explicit source sync, and use `scripts/source_sync.py restore-last` when you need to recover the previous canonical state. If live source drift is detected, Papyrus reports a conflict instead of claiming the sync is safe.

## 5. Script Inventory

Keep this list aligned with the current top-level `scripts/` directory. If a new top-level script is added, update this inventory in the same change.

Guardrail:

- Top-level Python scripts are stable operator entrypoints. Keep durable implementation in `src/papyrus/interfaces/` or `src/papyrus/jobs/` rather than growing new business logic directly under `scripts/`.

| Category | Scripts | Notes |
| --- | --- | --- |
| Bootstrap and build | `_bootstrap.py`, `bootstrap.sh`, `build.sh`, `build_index.py`, `build_route_map.py`, `validate.py` | Local environment setup, validation, route-map generation, and runtime rebuild entrypoints. |
| Serve and operator entrypoints | `run.py`, `serve.sh`, `serve_web.py`, `serve_api.py`, `operator_view.py`, `search.py` | Web, API, shell, and operator-facing read/manage entrypoints. |
| Authoring, import, and source mutation | `ingest.py`, `ingest_event.py`, `new_object.py`, `source_sync.py` | Create or ingest knowledge, scaffold source-backed objects, record events, and manage governed source synchronization. |
| Engineering gate | `check.sh`, `format.sh`, `lint.sh`, `typecheck.sh` | Formatter, lint, type-check, and full engineering gate commands. |
| Reporting and demo | `report_stale.py`, `report_content_health.py`, `demo_runtime.py`, `run_scenario.py` | Reporting, demo/runtime seeding, and scenario exercises. |
