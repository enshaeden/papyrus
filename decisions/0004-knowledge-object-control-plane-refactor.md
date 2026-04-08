# 0004 Knowledge-Object Control Plane Refactor

- Status: accepted
- Date: 2026-04-07

## Context

Papyrus has a strong phase-zero foundation:

- local-first authored source
- portable Markdown
- strict validation
- controlled vocabularies
- rebuildable derived artifacts
- duplicate, stale, and broken-link reporting

The current center of gravity is still wrong for the target problem:

- the primary schema is a flat article schema
- reusable logic is concentrated in `scripts/kb_common.py`
- the SQLite build is a flattened article table
- the generated site and documentation browse model still dominate the repository narrative

That shape is adequate for a disciplined Markdown repository, but insufficient for a governed operational knowledge control plane.

## Decision

Papyrus will be refactored from an article-centric repository into a knowledge-object-centric control plane.

The target first-class runtime entities are:

- knowledge objects
- knowledge revisions
- citations
- services
- relationships
- review assignments
- validation runs
- audit events

The runtime will move into a real application package under `src/papyrus/` with explicit layers for domain, application, infrastructure, interfaces, and jobs.

Canonical authored source remains local-first Markdown. Runtime state, reports, projections, and export surfaces remain rebuildable and non-authoritative.

MkDocs and other generated outputs are retained only as secondary export concerns. They do not define the primary application architecture.

## Consequences

### Positive

- reusable logic gains stable module boundaries
- CLI, API, and web surfaces can share the same application services
- governance workflows become modelable instead of passive metadata conventions
- runtime state can distinguish object identity from revision identity

### Costs

- the refactor introduces a new `src/` top-level directory
- compatibility shims are required during migration
- current source schemas and projections must coexist temporarily with the new package

## Migration Direction

The refactor proceeds in phases:

1. reframe repository docs and establish the application package
2. move core logic out of script-local helpers
3. replace the flat runtime projection with a relational operating model
4. replace the universal article schema with object-type-specific schemas
5. add explicit governance workflows
6. harden citations into runtime evidence with degradable trust posture
7. rebuild search and reporting over runtime governance signals

Later-phase clarification added during implementation:

- citation validity must remain conservative; missing capture metadata or integrity data cannot be treated as verified evidence
- runtime reporting should move to the relational model where that model is now the operating source for trust, approval, freshness, and evidence posture
- source-oriented checks such as broken Markdown links and orphaned generated files remain source-tree validations because the runtime does not replace the canonical filesystem

## Rejected Alternatives

### Keep Extending The Article Schema

Rejected because it preserves the wrong domain center of gravity and keeps review, evidence, and dependency state implicit.

### Keep Runtime Logic In Scripts

Rejected because it blocks reuse across interfaces and keeps the most important logic in an unstructured compatibility layer.

### Let Static Site Navigation Remain The Primary Product Surface

Rejected because export structure is not the same thing as operational runtime structure, trust posture, or governance workflow.
