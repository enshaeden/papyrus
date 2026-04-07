# Papyrus

Papyrus is a local-first knowledge management database for IT support and systems operations. Canonical content lives in portable Markdown with YAML front matter under `knowledge/`. Validation, indexing, reporting, and the browseable site layer are all derived from those source files and can be rebuilt locally.

## Goals

- Keep operational knowledge in human-readable source files.
- Keep the content model portable and vendor-neutral.
- Rebuild all derived artifacts from source at any time.
- Minimize drift through schema, taxonomy, and repository-policy validation.
- Keep migration inputs auditable without treating them as canonical content.

## Repository Layout

- `knowledge/`: active canonical knowledge articles.
- `archive/knowledge/`: archived canonical knowledge articles.
- `taxonomies/`: controlled vocabularies used by validation and reporting.
- `schemas/`: schema and repository-policy definitions.
- `templates/`: approved article templates only.
- `migration/`: sanitized migration inputs and manifests; never canonical article source.
- `reports/`: sanitized migration and review reports.
- `docs/`: explanatory system, design, workflow, and repository documentation.
- `decisions/`: ADR-style structural decisions.
- `scripts/`: validation, indexing, search, reporting, and site helpers.
- `generated/`: derived site-source files.
- `build/`: derived local data such as the knowledge index.
- `site/`: rendered static site output.
- `tests/`: lightweight regression tests.

## Content Model

Each article is a Markdown file with YAML front matter. Front matter stores the structured fields that drive validation, search, review reporting, and migration traceability. Required metadata is defined in [schemas/article.yml](schemas/article.yml).

Repository governance and directory policy are defined in [AGENTS.md](AGENTS.md), [schemas/repository_policy.yml](schemas/repository_policy.yml), and the architecture notes under [docs/architecture](docs/architecture/).

## Quick Start

Bootstrap a local environment:

```bash
./scripts/bootstrap.sh
```

Run validation:

```bash
python3 scripts/validate.py
```

Build derived artifacts:

```bash
./scripts/build.sh
```

Search the local index:

```bash
python3 scripts/search.py vpn
```

Report review due dates:

```bash
python3 scripts/report_stale.py
```

Report duplicate, orphaned, broken-link, and isolation signals:

```bash
python3 scripts/report_content_health.py
```

Report discovery metadata gaps:

```bash
python3 scripts/report_content_health.py --section missing-services --section missing-systems --section missing-tags
```

Create a new article scaffold:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

List valid taxonomy values before scaffolding:

```bash
python3 scripts/new_article.py --list-taxonomy services
python3 scripts/new_article.py --list-taxonomy systems
python3 scripts/new_article.py --list-taxonomy tags
```

Serve the local site:

```bash
./scripts/serve.sh
```

## Contributor Workflow

Placement rubric:

- `knowledge/` = how to do the work
- `docs/` = how the knowledge system and repository design work
- `decisions/` = why structural choices were made

1. Create or update canonical content under `knowledge/`.
2. Move retired content to `archive/knowledge/` instead of overwriting it.
3. Reuse the approved templates under `templates/`.
4. Keep taxonomy values aligned with `taxonomies/*.yml`.
5. Record structural changes in `decisions/`.
6. Run `python3 scripts/validate.py`.
7. Run `python3 scripts/report_content_health.py`.
8. Run `python3 scripts/report_stale.py`.
9. Run `python3 -m unittest discover -s tests -v` before finalizing substantial changes.

If `docs/` starts to accumulate operator-facing procedures, review:

```bash
python3 scripts/report_content_health.py --section knowledge-like-docs
```

Derived files under `generated/site_docs/`, `build/`, and `site/` are never authoritative. Rebuild them from source instead of editing them directly.

The generated site includes role-based entry points for support, authors, and managers, plus a faceted explorer, content-health view, coverage matrix, and knowledge-tree audit surface rebuilt entirely from canonical metadata.

## Governance

- Repository rules: [AGENTS.md](AGENTS.md)
- Governance policy: [docs/architecture/governance.md](docs/architecture/governance.md)
- Lifecycle policy: [docs/architecture/content-lifecycle.md](docs/architecture/content-lifecycle.md)
- Directory contract: [docs/architecture/information-architecture.md](docs/architecture/information-architecture.md)
- Contributor workflow: [docs/contributor-workflow.md](docs/contributor-workflow.md)
- Decisions: [decisions/index.md](decisions/index.md)
