# Papyrus

Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.

Papyrus is local-first knowledge system for IT support and systems operations. Repository contains application code, knowledge-model controls, system docs, and derived runtime artifacts. Repository does not contain committed canonical knowledge corpus.

## Run It Now

Bootstrap local environment:

```bash
./scripts/bootstrap.sh
```

Start quickest local web runtime:

```bash
./scripts/serve.sh
```

Start local web and API surfaces together:

```bash
python3 scripts/run.py --operator
```

Run engineering gate:

```bash
./scripts/check.sh
```

Run full test suite:

```bash
python3 -m unittest discover -s tests
```

## Common Workflows

Rebuild runtime from external workspace source root:

```bash
python3 scripts/build_index.py --source-root /path/to/workspace
python3 scripts/run.py --operator --source-root /path/to/workspace
```

Run read-only local runtime from retained artifacts:

```bash
python3 scripts/run.py --operator
```

Run demo runtime:

```bash
python3 scripts/run.py --demo
```

Inspect operator state from terminal:

```bash
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db --format json
```

## Repo Map

- `src/`: application code, runtime interfaces, domain, infrastructure
- `scripts/`: stable operator and engineering entrypoints
- `tests/`: unit, integration, interface, and documentation-contract coverage
- `knowledge_engine/`: canonical schemas, taxonomies, templates, repository policy
- `knowledge/`: Papyrus system knowledge and operator/developer playbooks
- `decisions/`: architecture, governance, and product-contract records
- `build/` and `generated/`: derived runtime artifacts only; never hand-edit
- `docs/`: reserved production-content structure and guidance, not committed corpus

## Source Of Truth

Authority order from root `AGENTS.md`:

1. `knowledge_engine/`
2. explicit external workspace source trees such as `knowledge/` and `archive/knowledge/` when task includes source-backed content
3. `decisions/`
4. `src/`
5. `docs/`
6. `generated/` and `build/`

Runtime boundary:

- Repository ships runtime code and retained artifacts, not canonical production corpus.
- Read-only runtime can boot from `build/knowledge.db` plus retained derived artifacts.
- Source-backed authoring, ingest conversion, writeback, and sync require explicit workspace source root.
- Request-scoped role context comes from runtime or authenticated identity, not URL prefixes.
- `scripts/serve_api.py` remains an operator-oriented local API surface.
- JSON API remains an operator-oriented local surface. It is not part of the role-scoped web experience contract, and any future role-scoped API contract requires a separate decision and migration.

## Developer Guardrails

- Do not edit files under `build/` or `generated/` by hand. Fix source or generator and rebuild.
- Do not treat `docs/` as committed production knowledge corpus in current repository state.
- Use `decisions/index.md` and linked decisions before changing shared routes, role visibility, layouts, or workflow boundaries.
- Keep top-level script behavior aligned with documentation. Update source of truth when commands or workflows change.

## Read More

- [Getting Started](knowledge/getting-started.md)
- [System Model](knowledge/system-model.md)
- Governance and decisions: [decisions/index.md](decisions/index.md)
- Role, layout, and workflow contracts: `decisions/role-scoped-experience-architecture.md`, `decisions/runtime-role-context-and-access-resolution.md`, `decisions/layout-contracts.md`, `decisions/knowledge-workflows-and-lifecycle.md`, `decisions/web-ui-component-contracts.md`
