# Contributor Workflow

## Add a New Article

Create a new scaffold:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

Edit the new file under `knowledge/` and replace placeholders before treating it as ready for use.

The scaffold is created only from the approved templates under `templates/`.

## Validate Content

Run:

```bash
python3 scripts/validate.py
```

Validation checks:

- required fields
- field types
- controlled taxonomy values
- date format
- duplicate article IDs
- canonical path correctness
- related and replacement article references
- title similarity without explicit linkage
- lifecycle metadata requirements
- directory contract and generated artifact policy
- duplicate source content between `docs/` and `knowledge/`
- broken local Markdown links

## Rebuild the Local Index

Run:

```bash
python3 scripts/build_index.py
```

This recreates `build/knowledge.db` from source files.

## Search Locally

Run:

```bash
python3 scripts/search.py "vpn"
```

If SQLite FTS5 is available, the search uses FTS. Otherwise it falls back to substring matching against denormalized text.

Archived content is excluded by default. Add `--include-archived` if you need it.

## Review Stale Content

Run:

```bash
python3 scripts/report_stale.py
```

Use `--as-of YYYY-MM-DD` for a fixed reporting date.

## Review Drift Signals

Run:

```bash
python3 scripts/report_content_health.py
```

To focus on one section:

```bash
python3 scripts/report_content_health.py --section duplicates
```

## Serve the Local Site

Run:

```bash
./scripts/serve.sh
```

`serve.sh` refreshes the generated site sources, runs validation, rebuilds the SQLite index, and then starts MkDocs. If MkDocs is not installed, run `./scripts/bootstrap.sh` first.
