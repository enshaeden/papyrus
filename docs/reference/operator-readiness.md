# Operator Readiness

This reference records the current operator-ready boundary for Papyrus and the runtime behaviors maintainers should preserve.

## Supported Operator Boundary

- Papyrus is a local-first operational knowledge system with governed read, write, review, and manage surfaces.
- Canonical source remains Markdown under `knowledge/` and `archive/knowledge/`.
- Runtime projections, reports, search indexes, and static exports are rebuildable and non-authoritative.
- Read, write, review, and health surfaces rely on explicit lifecycle, review, trust, and next-action contracts rather than compatibility-era aliases.

## Supported Startup And Recovery Paths

- Build or rebuild the runtime with `python3 scripts/build_index.py`.
- Start the local operator runtime with `python3 scripts/run.py --operator`.
- Inspect or apply governed source sync with `python3 scripts/source_sync.py`.
- Startup and governed mutation entrypoints run pending mutation recovery before proceeding.
- Recovery may reclaim stale journals and stale locks only when the active mutation state can be resolved safely.
- If recovery cannot prove a safe result, Papyrus fails closed.

## UI And Backend Contract Boundary

- Governed meaning comes from shared backend contracts:
  - `ui_projection`
  - workflow projections
  - action descriptors
  - acknowledgement payloads
- The web, CLI, and API should render those contracts without reintroducing route-local policy checks.
- Presenter and template changes must preserve structured posture meaning even when page layout or copy changes.

## Operational Usefulness Signals

- Content-health reporting should prioritize cleanup signals that affect operator usefulness:
  - placeholder-heavy content
  - legacy blueprint fallback usage
  - unclear ownership
  - weak evidence
  - unresolved migration-era gaps
- Those signals are intended to drive cleanup sequencing, not tighter prose rules or extra governance ceremony.

## Explicitly Deferred

- enterprise authentication and RBAC
- realtime collaboration
- notifications and subscriptions
- advanced diff tooling
- heavy external integrations

## Remaining Technical Debt

- Guided authoring still depends on blueprint-derived section content and compatibility handling for older migrated material.
- Migration cleanup remains ongoing for legacy placeholder density, fallback structure, ownership quality, and evidence maturity.
