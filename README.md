# Papyrus

Papyrus is a local-first governed operational knowledge control plane for IT support and systems operations.

Canonical authored knowledge remains in portable Markdown with YAML front matter under `knowledge/` and `archive/knowledge/`. Runtime state, validation, search, reporting, and future review workflows are being moved into an application package under `src/papyrus/`. Generated artifacts remain rebuildable and non-authoritative.

## What Papyrus Must Answer

- What do we know?
- Why do we believe it?
- Who reviewed or approved it?
- What changed that may invalidate it?
- What other knowledge becomes suspect when one thing changes?

## Current Refactor Boundary

Phases 1-4 are implemented.

- The repository framing is now knowledge-object centric instead of article centric.
- Canonical authored source is still Markdown under `knowledge/` and `archive/knowledge/`.
- The `src/papyrus/` package now owns reusable runtime logic instead of `scripts/kb_common.py`.
- Typed source schemas now live under `schemas/knowledge_objects/` for `runbook`, `known_error`, and `service_record`.
- `scripts/build_index.py` now rebuilds a relational SQLite runtime with first-class knowledge objects, revisions, citations, services, relationships, validation runs, review assignments, and audit events.
- CLI scripts remain first-class operator entrypoints, but they are wrappers over application services.
- MkDocs, `generated/`, and `site/` remain derived export concerns, not the primary product surface.
- The legacy universal article schema remains only as a migration compatibility shim.

## Repository Layout

- `knowledge/`: active canonical authored knowledge source files.
- `archive/knowledge/`: archived canonical authored knowledge source files.
- `docs/`: explanatory architecture, workflow, and governance documentation.
- `decisions/`: ADR-style structural decisions.
- `src/papyrus/`: application package for domain, application, infrastructure, interface, and job layers.
- `schemas/`: repository policy, typed source schemas, and legacy compatibility shims.
- `taxonomies/`: controlled vocabularies used by validation and reporting.
- `templates/`: approved source templates only.
- `scripts/`: operator-facing CLI entrypoints and compatibility shims.
- `migration/`: sanitized migration inputs and manifests; never canonical source.
- `reports/`: sanitized review and migration reports.
- `generated/`: derived export inputs.
- `build/`: derived local runtime artifacts such as SQLite projections.
- `site/`: rendered static export output.
- `tests/`: regression coverage.

## Operating Model

Papyrus distinguishes three layers:

1. Canonical authored source
   Source of truth under `knowledge/` and `archive/knowledge/`.
2. Operational runtime state
   Local, rebuildable application state used for validation, search, reporting, and later governance workflows.
3. Derived exports
   Static site output, generated pages, and other rebuildable views.

If source and a derived artifact disagree, the source wins.

## Quick Start

Bootstrap a local environment:

```bash
./scripts/bootstrap.sh
```

Validate canonical source and repository policy:

```bash
python3 scripts/validate.py
```

Build the current local runtime database:

```bash
python3 scripts/build_index.py
```

Search the local projection:

```bash
python3 scripts/search.py vpn
```

Report review due dates:

```bash
python3 scripts/report_stale.py
```

Report duplicates, link failures, isolation, and metadata gaps:

```bash
python3 scripts/report_content_health.py
```

Create a new canonical source scaffold:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

Serve the derived static export:

```bash
./scripts/serve.sh
```

## Source Of Truth Rules

- Canonical authored knowledge lives only under `knowledge/` and `archive/knowledge/`.
- Generated artifacts under `generated/`, `build/`, and `site/` are never authoritative.
- Validation is the completion gate.
- Structural changes to schemas, taxonomies, or top-level directories require a decision record.
- Static site output is secondary to the authored source and application runtime.

## Key Documents

- Control-plane architecture: [docs/architecture/control-plane-architecture.md](docs/architecture/control-plane-architecture.md)
- Governance policy: [docs/architecture/governance.md](docs/architecture/governance.md)
- Knowledge object lifecycle: [docs/architecture/content-lifecycle.md](docs/architecture/content-lifecycle.md)
- Information architecture: [docs/architecture/information-architecture.md](docs/architecture/information-architecture.md)
- Contributor workflow: [docs/contributor-workflow.md](docs/contributor-workflow.md)
- Refactor ADR: [decisions/0004-knowledge-object-control-plane-refactor.md](decisions/0004-knowledge-object-control-plane-refactor.md)
