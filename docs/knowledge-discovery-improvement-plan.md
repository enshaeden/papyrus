# Knowledge Discovery Improvement Plan

## Scope

This implementation targets three repository user journeys only:

- support specialists looking for the right SOP or troubleshooting path
- technical writers adding new canonical articles
- support managers auditing the knowledge tree and article coverage

## Verified Repository Gaps

- The generated site relied primarily on static browse pages by service, system, and tag.
- Article pages exposed raw metadata but did not surface applicability, inbound links, or likely adjacent content clearly.
- The scaffold workflow validated only a subset of metadata and did not help authors prefill discovery fields or review related content candidates.
- Content-health signals existed in CLI form but had limited generated-site visibility.

## Implementation Plan

1. Extend the static site generator to add role-based landing pages and a faceted explorer driven by canonical article metadata.
2. Improve article pages with faster operational summaries, stronger connected-content navigation, and lifecycle visibility.
3. Add generated manager and audit surfaces for the knowledge tree, coverage matrix, and content-health gaps.
4. Extend `new_article.py` to expose taxonomy values, prefill discovery metadata, and warn about duplicate or isolated-article risk earlier.
5. Update approved templates and contributor documentation so discoverability and interoperability guidance is present at scaffold time.

## Non-Goals

- No external SaaS search or discovery dependency.
- No parallel source of truth outside canonical Markdown plus YAML.
- No schema expansion unless required by the existing metadata model.

## Validation Plan

- Run `python3 scripts/validate.py`.
- Run `python3 scripts/report_content_health.py`.
- Run `python3 scripts/build_site_docs.py`.
- Run `python3 scripts/build_index.py`.
- Run `python3 -m unittest discover -s tests -v`.
