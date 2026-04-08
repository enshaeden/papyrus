# Getting Started

Use this path when you need a working Papyrus runtime quickly.

## 1. Prepare The Environment

```bash
./scripts/bootstrap.sh
python3 scripts/validate.py
python3 scripts/build_index.py
```

Outcome:
- The environment is bootstrapped.
- Canonical source validates cleanly.
- The local runtime database is rebuilt in `build/knowledge.db`.

Failure signals:
- `validate.py` reports schema, taxonomy, metadata, citation, or link errors.
- `build_index.py` cannot rebuild the runtime database.

## 2. Choose Your Entry Point

For browser-based work:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
```

- Web entrypoint: local web root route `/`
- API entrypoint: local API health route `/health`

For terminal-first work:

```bash
python3 scripts/search.py vpn
python3 scripts/report_stale.py
python3 scripts/report_content_health.py
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
