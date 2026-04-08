# Phase-Zero Knowledge Discovery Improvement Plan

This document records the earlier discovery and static-browse improvement plan for the phase-zero repository. It remains useful historical context, but it is no longer the primary architectural direction.

The current architectural direction is documented in [architecture/control-plane-architecture.md](architecture/control-plane-architecture.md) and [../decisions/0004-knowledge-object-control-plane-refactor.md](../decisions/0004-knowledge-object-control-plane-refactor.md).

## Historical Scope

This implementation targeted three repository user journeys only:

- support specialists looking for the right SOP or troubleshooting path
- technical writers adding new canonical articles
- support managers auditing the knowledge tree and article coverage

## Verified Repository Gaps At That Time

- The generated site relied primarily on static browse pages by service, system, and tag.
- Article pages exposed raw metadata but did not surface applicability, inbound links, or likely adjacent content clearly.
- The scaffold workflow validated only a subset of metadata and did not help authors prefill discovery fields or review related content candidates.
- Content-health signals existed in CLI form but had limited generated-site visibility.

## Historical Implementation Plan

1. Extend the static site generator to add role-based landing pages and a faceted explorer driven by canonical article metadata.
2. Improve article pages with faster operational summaries, stronger connected-content navigation, and lifecycle visibility.
3. Add generated manager and audit surfaces for the knowledge tree, coverage matrix, and content-health gaps.
4. Extend `new_article.py` to expose taxonomy values, prefill discovery metadata, and warn about duplicate or isolated-article risk earlier.
5. Update approved templates and contributor documentation so discoverability and interoperability guidance is present at scaffold time.

## Historical Non-Goals

- No external SaaS search or discovery dependency.
- No parallel source of truth outside canonical Markdown plus YAML.
- No schema expansion unless required by the existing metadata model.
