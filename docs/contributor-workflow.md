# Contributor Workflow

## Placement Rubric

- `knowledge/` = how to do the work
- `docs/` = how the knowledge system, repository, schema, taxonomy, generator, and workflow design work
- `decisions/` = why structural choices were made

Use this decision tree before creating or moving content:

- Operator-facing procedure, reference, troubleshooting guide, runbook, or SOP -> `knowledge/`
- Repository architecture, schema behavior, generator design, taxonomy design, or workflow design -> `docs/`
- Durable decision record with rationale and tradeoffs -> `decisions/`

Placement rules:

- Do not move canonical operational content into `docs/`.
- Do not duplicate article content between `knowledge/` and `docs/`.
- Prefer cross-links and `references` over copying content across areas.
- If a `docs/` page starts reading like a procedure, move the operational steps into `knowledge/` and leave only the explanatory system context in `docs/`.

## Add A New Article

Create a scaffold from the approved template set:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

To prefill discovery metadata and inspect valid taxonomy values first:

```bash
python3 scripts/new_article.py --list-taxonomy article_types
python3 scripts/new_article.py --list-taxonomy services
python3 scripts/new_article.py --list-taxonomy systems
python3 scripts/new_article.py --list-taxonomy tags
python3 scripts/new_article.py --type SOP --title "Example Procedure" \
  --team "Service Desk" --audience service_desk \
  --service "Remote Access" --system "<VPN_SERVICE>" --tag vpn
```

`new_article.py` now emits scaffold-time warnings when discovery metadata is still empty and emits [Inference] candidate related articles based on title and metadata overlap.

Edit the new file under `knowledge/` and replace all placeholders before treating it as ready.

## Discovery-Focused Authoring Checks

Before merging a new or substantially revised article:

- confirm `type`, `audience`, `team`, `services`, `systems`, and `tags` are populated with valid taxonomy values
- add `related_articles` for prerequisite, follow-on, escalation, or sibling procedures where they exist
- prefer local `references` or canonical article links instead of copying article content into `docs/`
- review the generated `knowledge/explorer.md`, `knowledge/content-health.md`, and `knowledge/authors.md` surfaces after rebuilding the site

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

Additional sections now include:

- `missing-services`
- `missing-systems`
- `missing-tags`
- `isolated-articles`
- `knowledge-like-docs`

`knowledge-like-docs` is a warning-oriented section. It flags files under `docs/` that may contain operational-knowledge signals such as article-style front matter, procedural headings, or strongly operator-oriented language. Treat it as a placement review queue first, not an automatic failure.

## Serve The Local Site

Run:

```bash
./scripts/serve.sh
```

`serve.sh` refreshes generated site sources, runs validation, rebuilds the local index, and starts the local site server.

Generated discovery and audit views now include:

- `knowledge/explorer.md`
- `knowledge/support.md`
- `knowledge/authors.md`
- `knowledge/managers.md`
- `knowledge/content-health.md`
- `knowledge/coverage-matrix.md`
- `knowledge/tree.md`
