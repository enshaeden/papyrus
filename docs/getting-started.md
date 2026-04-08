# Getting Started

Use this path when you need a working Papyrus runtime quickly.

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

For terminal-first work:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py dashboard --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
```

For a fast demo/runtime review path:

```bash
python3 scripts/run.py --demo
python3 scripts/run_scenario.py service-degradation
python3 scripts/operator_view.py queue --db build/demo-knowledge.db
```

For advanced surface-specific startup:

```bash
python3 scripts/serve_web.py --db build/knowledge.db --source-root .
python3 scripts/serve_api.py --db build/knowledge.db --source-root .
```

## 3. Pick The Right Playbook

- Need to find or verify guidance: [Read](playbooks/read.md)
- Need to create or revise canonical source: [Write](playbooks/write.md)
- Need to review, audit, or govern the corpus: [Manage](playbooks/manage.md)

## 4. Use The Right Source

- Canonical knowledge lives in `knowledge/` and `archive/knowledge/`.
- Repository decisions live in `decisions/`.
- Operator and reference docs live in `docs/`.
- Derived output in `generated/`, `build/`, and `site/` is rebuildable and not authoritative.
- Approved revisions write back deterministically to canonical Markdown through the governed application layer.
