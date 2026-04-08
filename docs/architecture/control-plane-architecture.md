# Control-Plane Architecture

Papyrus is being refactored from an article-centric Markdown repository into a governed operational knowledge control plane.

## Current State

Phase 1 through Phase 8 establish the current control-plane spine.

- Canonical authored source remains Markdown with YAML front matter under `knowledge/` and `archive/knowledge/`.
- Core runtime logic moves into `src/papyrus/`.
- Existing CLI entrypoints remain in place, but become wrappers over application services.
- Typed source schemas now live under `schemas/knowledge_objects/`.
- The local SQLite runtime now models knowledge objects, revisions, citations, services, relationships, validation runs, review assignments, and audit events.
- Deterministic governance workflows now create objects, create revisions, submit revisions for review, assign reviewers, approve or reject revisions, supersede objects, record validation runs, and mark objects suspect due to change.
- Citation scans now resolve runtime evidence posture from canonical source plus local runtime context instead of treating front matter references as passively trusted.
- Search and reporting now read from the relational runtime for freshness, approval state, citation health, ownership clarity, and suspect-object views.
- Thin JSON and server-rendered web interfaces now consume the same application query layer instead of re-implementing runtime logic in routes.
- The flat article schema remains only as a migration compatibility structure.

## Domain Focus

Papyrus is moving away from treating `article` as the primary noun. The target first-class entities are:

- `knowledge_objects`
- `knowledge_revisions`
- `citations`
- `services`
- `relationships`
- `review_assignments`
- `validation_runs`
- `audit_events`

Initial supported knowledge object types for the refactor target are:

- `runbook`
- `known_error`
- `service_record`

## Trust Model

Papyrus must answer not only what is documented, but why it should be trusted.

Trust posture is determined by signals such as:

- whether the current revision was reviewed and approved
- whether ownership is explicit
- whether citations are present and still valid
- whether review cadence is current
- whether upstream changes, service changes, or related-object changes may have invalidated the object

Trust posture is separate from lifecycle state. An active object may still be suspect or stale.

### Evidence Posture

Citation records are first-class runtime rows, not just front matter blobs. Each citation can carry:

- `source_type`
- `source_ref`
- `source_title`
- `claim_anchor`
- `note` or `excerpt`
- `captured_at`
- `validity_status`
- `integrity_hash`

Papyrus resolves runtime citation posture conservatively:

- missing local targets become broken evidence
- migration-era provenance without capture metadata remains unverified evidence
- cited knowledge objects that change after the current object was reviewed can degrade trust
- missing integrity data remains visible as weak evidence instead of being silently treated as verified

## Lifecycle Model

Papyrus separates:

- knowledge object lifecycle
- revision review lifecycle
- trust posture

During the transition, source files still carry compatibility fields such as `services`, `related_articles`, and `references` so legacy tooling can be bridged safely. Current workflow state lives in the runtime database and is preserved across source sync runs. Later phases will add broader operator surfaces on top of the same workflow services.

## Sync Model

Papyrus runs as a local-first system with two cooperating layers:

1. Canonical authored source
   Markdown plus YAML front matter under `knowledge/` and `archive/knowledge/`.
2. Runtime projection
   A rebuildable local application state used for validation, search, reporting, and governance workflows.

The sync boundary is one-way with respect to authority:

- authored source is authoritative
- runtime state is derived and rebuildable
- exports are derived from source plus runtime logic

The current sync flow ingests canonical Markdown source into a relational runtime that preserves object identity separately from revision identity and does not wipe workflow state on rebuild.
It also re-runs citation health and refreshes runtime search/reporting projections after sync so weak evidence is reflected immediately.

## Layered Runtime Design

The target runtime is organized under `src/papyrus/`:

- `domain/`: entities, value objects, and policy-level rules
- `application/`: commands, queries, review, validation, impact, and sync flows
- `infrastructure/`: markdown parsing, repositories, database support, search internals, and migrations
- `interfaces/`: CLI, API, and web surfaces
- `jobs/`: scheduled or operator-invoked scans

This separation exists to keep validation, search, reporting, and future governance workflows reusable across multiple interfaces.

The current operator surfaces are intentionally thin:

- CLI remains the local-first operator entrypoint for validation, build, search, and report commands
- the JSON API exposes the runtime queue, object detail, revision history, service detail, trust dashboard, and impact queries
- the server-rendered web interface renders those same queries without adding duplicate business logic

## Reporting And Search

Search is now application-backed over relational runtime tables instead of a flattened article projection. Ranking considers:

- lifecycle status
- freshness
- approval state
- citation health
- ownership clarity

Health reporting uses runtime-backed views where the runtime is now the right operating model, while source-oriented checks such as broken Markdown links and orphaned generated files still evaluate the source tree directly.

## Role Of Derived Artifacts

Derived artifacts are useful but secondary:

- `generated/` can continue to hold export inputs
- `site/` can continue to hold rendered static output
- `build/` can continue to hold local runtime artifacts

None of those areas are authoritative. The control plane must function even if static-site navigation is absent.

## Migration Boundary

This refactor keeps the strong parts of the existing repository:

- local-first authored source
- rebuildable derived artifacts
- strict validation
- taxonomy enforcement
- duplicate detection
- broken-link detection
- stale reporting

What changes is the operating focus:

- from article-centric to knowledge-object centric
- from script-centric to application-package centric
- from static-site-led browsing to governance-aware runtime services
