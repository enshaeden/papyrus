# 0005 Operator-Ready V1 Cut Line

- Status: Accepted
- Date: 2026-04-07

## Context

Papyrus had already established a durable local-first architecture, governance workflow primitives, and read-oriented web/API surfaces. What it lacked was an explicit operator-ready boundary: complete governed actions, calibrated trust posture, realistic workflow tension, parity checks across surfaces, and a simple path to stand the system up for review.

Without a clear v1 line, Papyrus risked expanding into adjacent but non-essential capabilities such as enterprise auth, real-time collaboration, notifications, or heavier integration work before the operator workflows were fully trustworthy.

## Decision

Papyrus v1 is defined as an operator-ready, local-first, governance-aware system for IT support and systems operations. It is not defined as an enterprise-complete collaboration platform.

Operator-ready v1 includes:

- polished read surfaces for queue, object detail, revision history, service detail, dashboard, and impact views
- structured write flows for object creation, revision creation, validation before submission, and review handoff
- functioning manage flows for reviewer assignment, approval, rejection, supersession, suspect marking, validation-run recording, and audit inspection
- explicit workflow outcomes with visible audit evidence
- calibrated trust posture that distinguishes approval state from trust degradation
- realistic demo/runtime data that shows healthy, stale, weak-evidence, suspect, and pending-review states
- role-based operability for read, write, and manage tasks
- shared core truth across CLI, web, and API surfaces
- a simple local startup path and a deterministic demo/review path

Papyrus v1 explicitly defers:

- enterprise authentication and RBAC
- collaborative multi-user editing
- notifications and subscriptions
- real-time updates
- advanced diff tooling
- heavy external integrations not required for operator readiness

## Consequences

- The repository now has a clear stop line for operator-ready work and can reject scope creep that does not improve operational trust.
- Future work can build on this baseline with separate ADRs rather than diluting the v1 goal.
- Papyrus can be presented honestly as operator-ready, local-first, and governance-aware without implying enterprise completeness.
