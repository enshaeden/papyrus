# Contributor Workflow

## Placement Rubric

- `knowledge/` and `archive/knowledge/` = canonical authored knowledge source
- `docs/` = control-plane architecture, workflow, and governance documentation
- `decisions/` = structural rationale and tradeoffs
- `src/papyrus/` = reusable runtime logic

Use this decision tree before creating or moving content:

- Operator-facing procedure, troubleshooting path, runbook, or support reference -> `knowledge/`
- Architecture, governance, runtime, schema, taxonomy, or workflow documentation -> `docs/`
- Durable structural choice with rationale and tradeoffs -> `decisions/`
- Reusable validation, search, sync, or reporting logic -> `src/papyrus/`

## Transition Note

Papyrus is in a controlled refactor from an article-centric repository to a knowledge-object control plane.

- Canonical source is still Markdown under `knowledge/` and `archive/knowledge/`.
- Existing scaffold tooling still uses `scripts/new_article.py` as a compatibility entrypoint.
- Typed source schemas under `schemas/knowledge_objects/` are now the primary source model for `runbook`, `known_error`, and `service_record`.
- `schemas/article.yml` remains only as a legacy compatibility fallback for migration-era content handling.

Do not create parallel schemas or ad hoc runtime helpers while the refactor is in progress.

## Add A New Canonical Source File

Use the current compatibility scaffold:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

To inspect valid taxonomy values first:

```bash
python3 scripts/new_article.py --list-taxonomy knowledge_object_types
python3 scripts/new_article.py --list-taxonomy services
python3 scripts/new_article.py --list-taxonomy systems
python3 scripts/new_article.py --list-taxonomy tags
```

Edit the new file under `knowledge/` and replace placeholders before treating it as ready.

## Validate Source And Repository Policy

Run:

```bash
python3 scripts/validate.py
```

Validation remains the completion gate and currently checks:

- required fields and data types
- controlled taxonomy values
- canonical path correctness
- lifecycle metadata requirements
- related-object and replacement references
- duplicate-title signals
- directory contract
- broken local Markdown links
- sanitization rules

## Build The Current Local Projection

Run:

```bash
python3 scripts/build_index.py
```

This rebuilds the local relational SQLite runtime used by search and reporting. The runtime is derived and rebuildable; the Markdown source remains authoritative.

## Search Locally

Run:

```bash
python3 scripts/search.py vpn
```

## Review Stale Source

Run:

```bash
python3 scripts/report_stale.py
```

Use `--as-of YYYY-MM-DD` for a fixed reporting date.

## Review Health Signals

Run:

```bash
python3 scripts/report_content_health.py
```

To focus on one section:

```bash
python3 scripts/report_content_health.py --section duplicates
```

## Static Export

Run:

```bash
./scripts/serve.sh
```

The static export remains useful for publishing and browseability, but it is not the primary operating model of Papyrus.
