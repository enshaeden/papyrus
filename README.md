# Papyrus

Papyrus is a local-first knowledge system for IT support and systems operations. Canonical knowledge lives in Markdown under `knowledge/` and `archive/knowledge/`; the runtime database, web surface, CLI, and exports are derived from that source rather than replacing it.

## Run It Now

```bash
./scripts/bootstrap.sh
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
- Derived artifacts only: `build/`, `generated/`, and `site/`

`scripts/serve_api.py` remains an operator-oriented local API surface. It is not part of the role-scoped web experience contract, and any future role-scoped API contract requires a separate decision and migration.

## Read More

- Start here: [docs/getting-started.md](docs/getting-started.md)
- Read playbook: [docs/playbooks/read.md](docs/playbooks/read.md)
- Write playbook: [docs/playbooks/write.md](docs/playbooks/write.md)
- Manage playbook: [docs/playbooks/manage.md](docs/playbooks/manage.md)
- System model: [docs/reference/system-model.md](docs/reference/system-model.md)
- Operator readiness: [docs/reference/operator-readiness.md](docs/reference/operator-readiness.md)
- Governance and decisions: [decisions/index.md](decisions/index.md)
