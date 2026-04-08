# Control-Plane Architecture

Papyrus is being refactored from an article-centric Markdown repository into a governed operational knowledge control plane.

## Scope Of This Phase

Phase 1 and Phase 2 establish the architectural spine only.

- Canonical authored source remains Markdown with YAML front matter under `knowledge/` and `archive/knowledge/`.
- Core runtime logic moves into `src/papyrus/`.
- Existing CLI entrypoints remain in place, but become wrappers over application services.
- The current flat article schema and SQLite projection remain compatibility structures until later phases replace them.

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

## Lifecycle Model

Papyrus separates:

- knowledge object lifecycle
- revision review lifecycle
- trust posture

During the transition, source files still carry the legacy status field required by the current validation flow. Later phases will add explicit review assignment, approval, rejection, supersession, and suspect-state handling in the runtime model.

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

[Unverified] Later phases will replace the current flat SQLite projection with a relational runtime model that preserves object identity separately from revision identity.

## Layered Runtime Design

The target runtime is organized under `src/papyrus/`:

- `domain/`: entities, value objects, and policy-level rules
- `application/`: commands, queries, review, validation, impact, and sync flows
- `infrastructure/`: markdown parsing, repositories, database support, search internals, and migrations
- `interfaces/`: CLI, API, and web surfaces
- `jobs/`: scheduled or operator-invoked scans

This separation exists to keep validation, search, reporting, and future governance workflows reusable across multiple interfaces.

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
