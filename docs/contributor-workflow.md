# Contributor Workflow

## Add A New Article

Create a scaffold from the approved template set:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

Edit the new file under `knowledge/` and replace all placeholders before treating it as ready.

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
- duplicate article ids
- canonical path correctness
- related and replacement article references
- title similarity without explicit linkage
- lifecycle metadata requirements
- directory contract and generated artifact policy
- duplicate source content between `docs/` and `knowledge/`
- broken local Markdown links
- sanitization checks for URLs, credentials, emails, addresses, host details, and branded residue

## Rebuild The Local Index

Run:

```bash
python3 scripts/build_index.py
```

This recreates `build/knowledge.db` from source files.

## Search Locally

Run:

```bash
python3 scripts/search.py vpn
```

Archived content is excluded by default. Add `--include-archived` if needed.

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

## Serve The Local Site

Run:

```bash
./scripts/serve.sh
```

`serve.sh` refreshes generated site sources, runs validation, rebuilds the local index, and starts the local site server.
