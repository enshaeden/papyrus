# Operator Readiness

This document records the operator-readiness hardening pass that moved Papyrus from a well-structured prototype to an operator-facing local-first system with explicit workflow outcomes, calibrated trust signals, parity checks, and a realistic demo/runtime path.

## Purpose And Scope

- Harden operator workflows without rewriting the object model or adding AI-specific features.
- Keep all read, write, and manage behavior anchored in the shared application layer.
- Provide one clear local happy path and one clear demo/review path.
- Make trust degradation explicit, inspectable, and useful in real operator hands.

## Technical Approach

- Added a shared posture model in `src/papyrus/application/posture.py` so CLI, API, and web surfaces expose the same trust and approval reasoning.
- Extended manage/operator workflows with governed web and API actions for:
  - superseding an object
  - marking an object suspect with explicit rationale
  - recording a validation run
- Added a thin parity CLI in `scripts/operator_view.py` for queue, dashboard, object detail, review detail, manage queue, and validation-run inspection.
- Added `scripts/demo_runtime.py` plus `src/papyrus/application/demo_flow.py` to build a realistic local demo/runtime with:
  - a healthy service and trusted runbook
  - a degraded service
  - a stale runbook
  - a weak-evidence known error
  - an in-review revision
  - a change-triggered suspect object
- Kept static export secondary and untouched as the approved-content surface.

## Operator-Ready V1

Papyrus operator-ready v1 is the smallest release that lets a local operator read, write, and govern knowledge safely without needing direct SQLite inspection or undocumented internal workflow knowledge.

Included in v1:

- a polished read surface across queue, object, service, dashboard, impact, and revision-history views
- a structured write surface for object and revision creation plus review submission
- a functioning manage surface for reviewer assignment, approval, rejection, supersession, suspect marking, validation-run recording, and audit inspection
- reliable workflow transitions with explicit success and failure outcomes
- calibrated trust posture with visible reasons instead of generic status language
- a realistic sample/demo runtime with healthy, stale, weak-evidence, in-review, and change-triggered suspect content
- role-based operability checks for read, write, and manage tasks
- parity across CLI, web, and API for core operational truth
- one clear local startup path and one clear demo/review path

Explicitly deferred from v1:

- enterprise authentication and RBAC
- collaborative multi-user editing
- notifications and subscriptions
- real-time updates
- advanced diff tooling
- heavy external integrations not required for local operator readiness

## Dependencies Introduced Or Modified

- No new third-party dependencies were introduced.
- Runtime behavior continues to rely on the standard-library WSGI stack, SQLite, and existing repository taxonomies/schemas.

## Security, Observability, And Performance Review

- Security:
  Governed API actions now require an explicit actor, internal error responses are sanitized, and operator-facing errors avoid leaking stack traces or raw exception internals.
- Observability:
  Governance actions surface as audit events with details, object detail pages expose recent audit metadata, and validation-run history remains inspectable through web, API, and CLI surfaces.
- Performance:
  This pass kept the existing SQLite projection model and reused shared query helpers rather than adding new infrastructure. Ranking work stays in SQL plus lightweight Python ordering over bounded result sets.

## Demo Scenario Coverage

- Healthy service: `kb-demo-remote-access-service-record`
- Healthy runbook: `kb-demo-vpn-recovery-runbook`
- Degraded service: `kb-demo-identity-service-record`
- Stale runbook: `kb-demo-identity-fallback-runbook`
- Weak evidence: `kb-demo-evidence-gap-known-error`
- Change-triggered suspect object: `kb-demo-identity-token-known-error`
- Pending review: `kb-demo-password-reset-runbook`

Build and review it with:

```bash
python3 scripts/demo_runtime.py
python3 scripts/serve_web.py --db build/demo-knowledge.db
python3 scripts/serve_api.py --db build/demo-knowledge.db
python3 scripts/operator_view.py queue --db build/demo-knowledge.db
```

## Failure Modes And Rollback

- Runtime unavailable:
  Run `python3 scripts/build_index.py` or rebuild the demo DB with `python3 scripts/demo_runtime.py`.
- Invalid governed action:
  Fix the request payload or workflow state; Papyrus now returns explicit 400 responses and web error pages.
- Demo/runtime rollback:
  Stop pointing the web/API/CLI at `build/demo-knowledge.db` and return to `build/knowledge.db`.
- Code rollback:
  Revert this pass and rebuild the runtime. The changes are additive and do not require irreversible source migrations.

## Known Limitations And Tradeoffs

- The write/manage UI still governs runtime state rather than writing canonical Markdown source directly.
- The CLI is an inspection/parity surface, not a full authoring surface.
- Authentication, RBAC, notifications, realtime updates, and collaborative multi-user editing remain deferred.
- Static export remains approval-gated and secondary; it is intentionally not a live governance surface.

## Structured Findings

----------------------------------------
TYPE: Workflow gap
SEVERITY: High

DESCRIPTION:
Supersession, suspect marking, and validation-run recording existed below the application layer but were not exposed as complete operator workflows in the web or API surfaces.

IMPACT:
Operators could not complete critical governance actions end-to-end without dropping into code or ad-hoc database workflows.

AFFECTED COMPONENTS:
Web manage surface, JSON API, audit visibility

ROOT CAUSE:
The first read/write/manage pass exposed only the most common review actions.

RECOMMENDED RESOLUTION:
Expose the missing governed actions through thin web/API layers with rationale capture, redirect-after-post handling, and audit evidence.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Trust calibration issue
SEVERITY: High

DESCRIPTION:
Ownership placeholders dominated the trust state and made nearly the entire runtime look uniformly suspect, which hid the more important freshness and evidence signals.

IMPACT:
Operators could not quickly separate healthy, weak-evidence, stale, and change-triggered suspect content.

AFFECTED COMPONENTS:
Trust model, queue ordering, dashboard visibility, object detail views

ROOT CAUSE:
Ownership ambiguity was treated as a primary trust-state downgrade rather than a secondary operational warning.

RECOMMENDED RESOLUTION:
Keep ownership ambiguity visible, but let freshness, evidence quality, and explicit suspect events drive the primary trust posture.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Search/retrieval weakness
SEVERITY: High

DESCRIPTION:
Search and queue ordering did not reliably put the most trustworthy operational answer first, and service linkage was not visible in result lists.

IMPACT:
Support operators had to click through multiple results before judging whether a result was safe and relevant.

AFFECTED COMPONENTS:
Queue query, search query, queue presenter, dashboard presenter

ROOT CAUSE:
Ranking leaned toward coarse runtime posture without explicit operator-answer prioritization or cross-navigation signals.

RECOMMENDED RESOLUTION:
Promote approved, trustworthy, service-linked, and connected content first; demote weak/stale/isolated content while keeping the reason visible in-line.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Bug
SEVERITY: High

DESCRIPTION:
FTS-backed search could miss runtime-created or newly governed objects until the runtime projection was rebuilt, even though queue/detail surfaces already reflected the updated state.

IMPACT:
Operators could complete a workflow and still fail to retrieve the new or updated object through direct search, which undermined trust in the system during active governance work.

AFFECTED COMPONENTS:
Search query path, CLI/API/web retrieval parity

ROOT CAUSE:
The search path preferred the `knowledge_search` FTS index when present, but runtime workflow mutations updated `search_documents` more immediately than the FTS table.

RECOMMENDED RESOLUTION:
Supplement FTS matches with live `search_documents` retrieval and deduplicate results so runtime-governed objects remain searchable without forcing an immediate rebuild.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Demo/sample-data gap
SEVERITY: High

DESCRIPTION:
Source-sync data alone did not demonstrate pending review, change-triggered suspect posture, or realistic governance tension.

IMPACT:
Papyrus could look well-architected but still fail to prove real operator workflows under stress.

AFFECTED COMPONENTS:
Demo path, trust dashboard, queue, service detail, revision history

ROOT CAUSE:
Canonical repository source naturally syncs into mostly approved runtime state and does not on its own create review-queue tension.

RECOMMENDED RESOLUTION:
Build a deterministic local demo/runtime that layers governed scenario objects and audit activity on top of the synced source.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Degraded-mode design issue
SEVERITY: Medium

DESCRIPTION:
Runtime-unavailable, bad-request, and internal-error responses were too generic and exposed raw exception details in some surfaces.

IMPACT:
Operators could not reliably tell whether the next step was rebuilding the runtime, fixing a request, or asking for deeper admin help.

AFFECTED COMPONENTS:
WSGI web app, JSON API

ROOT CAUSE:
Earlier error handling focused on correctness rather than operator actionability and information hygiene.

RECOMMENDED RESOLUTION:
Return categorized, actionable error responses and sanitize internal failures.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Workflow inefficiency
SEVERITY: Medium

DESCRIPTION:
There was no parity CLI for queue, dashboard, or detail inspection.

IMPACT:
Surface parity checks depended on HTML scraping or direct SQLite inspection.

AFFECTED COMPONENTS:
CLI/operator tooling, parity regression testing

ROOT CAUSE:
The original CLI focused on validation/search utilities rather than operator-state inspection.

RECOMMENDED RESOLUTION:
Add a thin shared-query CLI surface for queue, dashboard, object, review, manage queue, and validation history.

STATUS:
RESOLVED
----------------------------------------

----------------------------------------
TYPE: Deferred capability
SEVERITY: Low

DESCRIPTION:
Papyrus still lacks enterprise auth/RBAC, notifications, realtime updates, collaborative editing, and advanced diff tooling.

IMPACT:
Papyrus is operator-ready for local-first governed use, but not enterprise-complete.

AFFECTED COMPONENTS:
Deployment framing, future roadmap

ROOT CAUSE:
These capabilities are intentionally outside the operator-ready v1 cut line.

RECOMMENDED RESOLUTION:
Treat them as explicit post-v1 roadmap items rather than leaking them into the current pass.

STATUS:
UNRESOLVED

IF UNRESOLVED:
- Reason it was not fixed:
  Out of scope for operator-ready v1 and would expand the pass into auth, collaboration, and notification infrastructure.
- What is required to resolve later:
  Separate roadmap and ADRs for auth boundaries, multi-user coordination, and realtime/eventing.
----------------------------------------
