# Papyrus

Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.

Canonical knowledge remains in workspace Markdown trees such as `knowledge/` and `archive/knowledge/`; the shipped/read-only runtime boots from the runtime database plus retained derived artifacts, and those runtime surfaces are not source of truth.

## Run It Now

```bash
./scripts/bootstrap.sh
./scripts/build.sh
python3 scripts/run.py --operator
```

Start at `/operator` for the operator home surface. Reader and Admin surfaces are mounted under `/reader/*` and `/admin/*`.

Current primary entrypoints:

- Web runtime: `python3 scripts/run.py --operator`
- Formatter: `./scripts/format.sh`
- Lint: `./scripts/lint.sh`
- Type check: `./scripts/typecheck.sh`
- Route map: `python3 scripts/build_route_map.py`
- Full engineering gate: `./scripts/check.sh`
- CLI queue view: `python3 scripts/operator_view.py queue --db build/knowledge.db`
- Validation: `python3 scripts/validate.py`
- Tests: `python3 -m unittest discover -s tests`
- Build: `./scripts/build.sh`

Useful operator commands:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db --format json
```

## Source Of Truth

- Canonical knowledge: `knowledge/` and `archive/knowledge/`
- Schemas and policy: `schemas/`
- Taxonomies: `taxonomies/`
- Templates: `templates/`
- Governance and decisions: `decisions/`
- Explanatory and operator docs: `docs/`
- Derived artifacts only: `build/` and `generated/`

Runtime/workspace contract:
- Read-only runtime uses `build/knowledge.db` plus retained runtime artifacts such as `generated/route-map.json` and `generated/route-map.md`.
- Source-backed authoring, ingest, review writeback, and sync require an explicit workspace source root.
- The repository is a workspace by default for local development, but the runtime product must not assume repo-local source Markdown is present.

There is no separate MkDocs or static-export publication surface. Readers consume dependable content through the runtime product, while Operators and Admins stay on the retained backend and runtime surfaces.

`scripts/serve_api.py` remains an operator-oriented local API surface. It is not part of the role-scoped web experience contract, and any future role-scoped API contract requires a separate decision and migration.

## Read More

- Start here: [docs/getting-started.md](docs/getting-started.md)
- Content playbook: [docs/playbooks/read.md](docs/playbooks/read.md)
- Authoring playbook: [docs/playbooks/write.md](docs/playbooks/write.md)
- Oversight playbook: [docs/playbooks/manage.md](docs/playbooks/manage.md)
- System model: [docs/reference/system-model.md](docs/reference/system-model.md)
- Operator readiness: [docs/reference/operator-readiness.md](docs/reference/operator-readiness.md)
- Governance and decisions: [decisions/index.md](decisions/index.md)
