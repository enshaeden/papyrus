# Operator Governance And Decisions

## Status

Accepted

## Purpose And Scope

This document consolidates the Papyrus repository decisions into one operator-facing governance record. Use it when you need the durable rules, rationale, migration boundaries, and v1 product boundary that explain how Papyrus is meant to be operated and evolved.

This record supersedes the earlier split decision set for:

- source-of-truth and anti-drift policy
- migration workspace and sanitized provenance
- sanitized review reports and public seed artifacts
- the knowledge-object control-plane refactor
- the operator-ready v1 cut line

## Operator Summary

Papyrus is a local-first operational knowledge control plane for IT support and systems operations.

- Canonical source stays in Markdown under `knowledge/` and `archive/knowledge/`.
- Repository documentation and operator guidance stay in `docs/`.
- Structural governance decisions stay in `decisions/`.
- Runtime state, indexes, reports, and static exports are rebuildable and non-authoritative.
- Operators should use the runtime, API, web UI, CLI, and approved static export according to role, but treat canonical source as the final authority when layers disagree.
- Approved runtime revisions must write back deterministically to canonical Markdown through the governed application layer.

## Repository Boundaries

### Source Of Truth

- Canonical operational knowledge lives only in `knowledge/` and `archive/knowledge/`.
- Canonical explanatory documentation lives only in `docs/`.
- Structural governance decisions live only in `decisions/`.
- Controlled vocabularies live only in `taxonomies/`.
- Field and repository policy definitions live only in `schemas/`.
- Approved content templates live only in `templates/`.

### Derived And Non-Canonical Areas

- Generated and build outputs belong only in `generated/`, `build/`, or `site/`.
- Generated files must never be edited by hand.
- If a generated artifact is wrong, fix the source or generator and rebuild.
- `build/` is derived local state for runtime databases, ingestion workbench artifacts, and disposable demo data; it must not be treated as canonical repository source.
- A top-level `migration/` workspace is allowed for sanitized seed plans, manifests, and migration-only validation inputs.
- A top-level `reports/` workspace is allowed for sanitized review artifacts only.

### Drift Controls

- Validation must enforce lifecycle, duplicate, metadata, link, sanitization, and directory-contract rules.
- Article creation must stay within approved template families from `templates/`.
- Schema and taxonomy changes require explicit rationale.
- Contributors must update source files rather than patching derived outputs.

## Provenance, Migration, And Sanitization

Papyrus supports deterministic seeding from legacy exports without promoting raw import artifacts into long-term source of truth.

- `migration/` remains non-canonical even when it stores audited seed plans or manifests.
- Canonical articles must retain sanitized provenance through fields such as `source_system` and `source_title`.
- Migration outcomes must be preserved through sanitized manifests, not raw export paths, source ids, or branded labels.
- Reports and seed-review artifacts must avoid reversible mappings back to sensitive source material.
- Sanitized reports can be versioned for audit and handoff, but they must not become substitutes for canonical knowledge articles or decision records.

## Control-Plane Architecture

Papyrus is intentionally knowledge-object-centric rather than article-centric.

### First-Class Runtime Entities

- knowledge objects
- knowledge revisions
- citations
- events
- services
- relationships
- review assignments
- validation runs
- audit events
- actors

### Architectural Direction

- Shared runtime logic belongs in `src/papyrus/` with explicit domain, application, infrastructure, interface, and job layers.
- CLI, API, and web surfaces must share the same application services instead of duplicating workflow logic.
- Canonical authored source remains local-first Markdown.
- Approved revisions must write back to canonical Markdown through the application layer instead of manual source sync.
- Change, validation, and evidence events must be ingested explicitly and stored locally before impact propagation occurs.
- Trust degradation must remain explicit, causal, and auditable. Hidden downgrade paths are not acceptable.
- Governance actions must always carry an accountable actor.
- Runtime state, reports, search projections, and exports remain rebuildable and non-authoritative.
- MkDocs and other static export outputs are secondary publication surfaces, not the control plane.

### Migration Direction

The control-plane refactor proceeds in phases:

1. Reframe repository docs and establish the application package.
2. Move core logic out of script-local helpers.
3. Replace the flat runtime projection with a relational operating model.
4. Replace the universal article schema with object-type-specific schemas.
5. Add explicit governance workflows.
6. Harden citations into runtime evidence with degradable trust posture.
7. Rebuild search and reporting over runtime governance signals.
8. Expose thin operator web and API surfaces over the shared application layer.
9. Keep static export explicit, optional, and approval-gated.
10. Close the loop from governed runtime revision back to canonical Markdown source.
11. Ingest structured local change events and propagate visible consequence.
12. Mature evidence handling from presence checks into lifecycle state.
13. Require accountable actors across all governed actions.
14. Preserve a trivial local startup path for operator and demo modes.

### Rejected Alternatives

- Keep extending the flat article schema:
  Rejected because it preserves the wrong domain center of gravity and keeps review, evidence, and dependency state implicit.
- Keep runtime logic in script-local helpers:
  Rejected because it blocks reuse across interfaces and leaves core behavior in an unstable compatibility layer.
- Let static site navigation define the product:
  Rejected because export structure is not the same thing as operational runtime structure, trust posture, or governance workflow.

## Operator-Ready V1 Boundary

Papyrus v1 is defined as an operator-ready, local-first, governance-aware system. It is not defined as an enterprise-complete collaboration platform.

### Included In V1

- polished read surfaces for queue, object detail, revision history, service detail, dashboard, and impact views
- structured write flows for object creation, revision creation, validation before submission, and review handoff
- functioning manage flows for reviewer assignment, approval, rejection, supersession, suspect marking, validation-run recording, and audit inspection
- explicit workflow outcomes with visible audit evidence
- calibrated trust posture that distinguishes approval state from trust degradation
- realistic demo/runtime data that shows healthy, stale, weak-evidence, suspect, and pending-review states
- role-based operability for read, write, and manage tasks
- shared operational truth across CLI, web, and API surfaces
- a simple local startup path and a deterministic demo/review path

### Closed-Loop Control Plane Extension

- Approved revisions now write back deterministically to canonical Markdown source.
- Papyrus can ingest structured local events and propagate causal impact.
- Evidence lifecycle now includes snapshots, expiry, stale state, and revalidation requests.
- Web, API, CLI, demo, and scenario flows all require or supply an accountable actor.
- Demo and operator startup are available as one-command local entrypoints through `scripts/run.py`.

### Explicitly Deferred

- enterprise authentication and RBAC
- collaborative multi-user editing
- notifications and subscriptions
- real-time updates
- advanced diff tooling
- heavy external integrations not required for operator readiness

## Dependencies Introduced Or Modified

- No new third-party dependencies are required by this consolidated governance model.
- Papyrus continues to rely on local Markdown source, SQLite-backed runtime projections, existing schemas and taxonomies, and the current static export toolchain.
- Repository shape assumptions now include `migration/`, `reports/`, and `src/papyrus/` as intentional parts of the governed system boundary.
- The controlled-source schemas now carry evidence lifecycle fields, and the runtime schema now includes events plus weighted relationship metadata. This change is intentional so impact and writeback behavior stay local, causal, and reproducible.

## Known Limitations And Tradeoffs

- Papyrus is intentionally strict about source-of-truth boundaries, which increases validation pressure but materially reduces drift.
- Runtime governance and review state remain rebuildable and inspectable, but Papyrus still uses local operator-selected actors rather than enterprise identity.
- Static export remains secondary and approval-gated, which keeps publication safer but means it is not the live governance surface.
- Operator-ready v1 is intentionally narrower than enterprise collaboration software, so auth, notifications, real-time updates, and heavier integrations remain future work.

## Failure Modes And Recovery

- Source and derived state disagree:
  Treat canonical source as authoritative, rebuild the runtime or export, and re-run validation.
- Governed writeback fails:
  Treat the approval as incomplete, inspect the source root and audit event trail, correct the schema or path issue, and rerun the approval or explicit source sync.
- Runtime projections or search surfaces become stale:
  Rebuild with `python3 scripts/build_index.py` and re-check operator views.
- Change or evidence event causes unexpected trust degradation:
  Inspect the stored event payload, propagation path, and audit history before overriding trust posture.
- Static export becomes inconsistent with approval state:
  Rebuild approved output and do not patch generated files manually.
- Migration or review artifacts drift toward canonical behavior:
  Move authoritative content back into `knowledge/`, `archive/knowledge/`, `docs/`, or `decisions/` as appropriate and keep `migration/` and `reports/` non-canonical.

## Rollback Strategy

This consolidation is a documentation-structure change only.

- If the single-record format proves unhelpful, restore the previous split decision files from version control.
- No data migration or runtime schema rollback is required.
- Derived export content can be rebuilt after rollback without changing canonical knowledge.

## Related Operator Docs

- [Getting started](../docs/getting-started.md)
- [Read playbook](../docs/playbooks/read.md)
- [Write playbook](../docs/playbooks/write.md)
- [Manage playbook](../docs/playbooks/manage.md)
- [System model](../docs/reference/system-model.md)
- [Operator readiness](../docs/reference/operator-readiness.md)
