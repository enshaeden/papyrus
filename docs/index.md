# System & Design Docs

This area explains how the Papyrus control plane works. It covers repository architecture, governance, lifecycle rules, runtime design, and contributor workflow. It is not the source of truth for operator-facing procedures.

## Use The Right Area

- For canonical operational knowledge, use `knowledge/` or `archive/knowledge/`.
- For architecture, runtime, governance, and workflow documentation, use `docs/`.
- For durable structural rationale and tradeoffs, use `decisions/`.

## What Belongs Here

- Control-plane architecture and domain model
- Canonical source versus runtime-state rules
- Repository policy, validation, and taxonomy behavior
- Contributor workflow and migration guidance
- Export and publishing design for derived artifacts

## What Does Not Belong Here

- Canonical operator procedures
- Runbook steps copied from `knowledge/`
- Static-export output treated as source of truth

## Start Here

- [Control-Plane Architecture](architecture/control-plane-architecture.md)
- [Governance Policy](architecture/governance.md)
- [Knowledge Object Lifecycle](architecture/content-lifecycle.md)
- [Information Architecture](architecture/information-architecture.md)
- [Contributor Workflow](contributor-workflow.md)
- [Refactor ADR](../decisions/0004-knowledge-object-control-plane-refactor.md)
- [Phase-Zero Discovery Plan](knowledge-discovery-improvement-plan.md)
