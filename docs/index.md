# Papyrus

Papyrus is a standalone knowledge management database for IT support and systems operations. Markdown plus YAML front matter under `knowledge/` is the canonical source of truth. SQLite, search, stale reporting, and the MkDocs browsing layer are derived from those source files.

## What This Repository Provides

- Canonical operational content in portable Markdown files.
- Controlled vocabularies under `taxonomies/`.
- A schema-driven validator under `scripts/validate.py`.
- A reproducible SQLite index with optional FTS5 under `scripts/build_index.py`.
- A local search CLI under `scripts/search.py`.
- A stale content report under `scripts/report_stale.py`.
- A content-health report under `scripts/report_content_health.py`.
- A local documentation site that can be rebuilt without changing the canonical content model.

## Source of Truth

Edit `knowledge/`, `archive/knowledge/`, `docs/`, `decisions/`, `taxonomies/`, `schemas/`, or `templates/` as appropriate. The generated pages under `generated/site_docs/`, the SQLite index under `build/`, and the rendered site under `site/` are rebuilt from source and are never authoritative.

## Next Steps

- Review the governance notes in [architecture/governance.md](architecture/governance.md).
- Review the lifecycle policy in [architecture/content-lifecycle.md](architecture/content-lifecycle.md).
- Review the directory contract in [architecture/information-architecture.md](architecture/information-architecture.md).
- Review the workflow guide in [contributor-workflow.md](contributor-workflow.md).
- Browse the generated knowledge index after running `./scripts/build.sh`.
