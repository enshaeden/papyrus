# Papyrus

Papyrus is a local-first knowledge management database for IT support and systems operations. The canonical source of truth is portable Markdown with YAML front matter under `knowledge/`. Validation, indexing, search, stale reporting, and site generation are all derived from those source files and run locally.

## Goals

- Keep operational knowledge in human-readable files.
- Keep the content model independent of any single renderer.
- Rebuild the SQLite index and site layer from source at any time.
- Keep dependencies minimal and avoid SaaS or cloud runtime requirements.
- Prevent documentation sprawl and source-of-truth drift through policy and validation.

## Repository Layout

- `knowledge/`: active canonical Markdown knowledge articles with YAML front matter
- `archive/knowledge/`: archived canonical knowledge articles with preserved metadata
- `taxonomies/`: controlled vocabularies used by validation and reporting
- `schemas/`: field definitions and repository policy
- `templates/`: approved content templates only
- `docs/`: explanatory repository documentation only
- `decisions/`: ADR-style structural decisions
- `scripts/`: bootstrap, validation, indexing, search, reporting, and site helpers
- `generated/`: derived site-input pages generated from source
- `build/`: generated SQLite database and other local build artifacts
- `site/`: MkDocs output when a static site build is run
- `tests/`: lightweight local regression checks using `unittest`

## Content Model

Each article is a Markdown file with YAML front matter. Front matter holds the structured fields that drive validation, indexing, search, and stale reporting. Freeform Markdown body content remains portable and does not rely on MkDocs-specific extensions.

Required metadata is defined in [schemas/article.yml](schemas/article.yml) and includes:

- `id`
- `title`
- `canonical_path`
- `summary`
- `type`
- `status`
- `owner`
- `source_type`
- `team`
- `systems`
- `services`
- `tags`
- `created`
- `updated`
- `last_reviewed`
- `review_cadence`
- `audience`
- `prerequisites`
- `steps`
- `verification`
- `rollback`
- `related_articles`
- `replaced_by`
- `retirement_reason`
- `references`
- `change_log`

Repository governance and directory policy are defined in [AGENTS.md](AGENTS.md), [schemas/repository_policy.yml](schemas/repository_policy.yml), and the architecture docs under [docs/architecture/](docs/architecture).

## Quick Start

Bootstrap a fresh clone into a local virtual environment:

```bash
./scripts/bootstrap.sh
```

Run validation:

```bash
python3 scripts/validate.py
```

Build the generated site inputs, validate, rebuild the SQLite index, and render the static site when MkDocs is installed:

```bash
./scripts/build.sh
```

Search the local index:

```bash
python3 scripts/search.py vpn
```

Report content due for review:

```bash
python3 scripts/report_stale.py
```

Report duplicate, orphaned, broken-link, and isolated-content signals:

```bash
python3 scripts/report_content_health.py
```

Create a new article scaffold from the approved template set:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

Serve the site locally:

```bash
./scripts/serve.sh
```

## Contributor Workflow

1. Create or update canonical content under `knowledge/`.
2. Move retired content to `archive/knowledge/` instead of overwriting it.
3. Reuse the approved templates under `templates/`.
4. Keep taxonomy values aligned with `taxonomies/*.yml`.
5. Record structural changes in `decisions/`.
6. Run `python3 scripts/report_content_health.py`.
7. Run `python3 scripts/report_stale.py`.
8. Run `python3 -m unittest discover -s tests -v` before committing changes.

Derived site inputs under `generated/site_docs/`, the SQLite index under `build/`, and the rendered site under `site/` are never authoritative. Rebuild them from source instead of editing them.

## Governance

- Repository rules: [AGENTS.md](AGENTS.md)
- Governance policy: [docs/architecture/governance.md](docs/architecture/governance.md)
- Lifecycle policy: [docs/architecture/content-lifecycle.md](docs/architecture/content-lifecycle.md)
- Directory contract and IA: [docs/architecture/information-architecture.md](docs/architecture/information-architecture.md)
- Contributor workflow: [docs/contributor-workflow.md](docs/contributor-workflow.md)
- Decisions: [decisions/index.md](decisions/index.md)
