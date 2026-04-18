# Review And Governance Playbook

Use this playbook when you review revisions, make lifecycle decisions, monitor content risk, or inspect recent change and audit history.

The governed work surfaces are intentionally distinct:

- `Review` is the queue and revision-decision workbench
- `Governance` is the intervention board for services, posture, and cross-object follow-up
- `Activity` is the recent change and audit feed
- `Admin` is the control plane for users, access, templates, schemas, spaces, settings, and full audit

## Refresh The Runtime Before Review

```bash
python3 scripts/build_index.py --source-root /path/to/workspace
```

Outcome:

- Queue ordering, trust state, citations, and impact views reflect current source and runtime state.

## Start With Review Or Governance

Open the runtime-backed queue:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
python3 scripts/operator_view.py manage-queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db
```

- Web review route: `/review`
- Web governance route: `/governance`
- Web history route: `/review/activity`
- Admin landing: `/admin/overview`

Use these surfaces by purpose:

- `Review`: ready for review, needs decision, drafts and rework, with selected context only when it helps a decision
- `Governance`: service posture, weak evidence, suspect objects, ownership gaps, and cleanup debt grouped by intervention type
- `Activity`: recent changes, validation outcomes, and writeback or audit recovery context
- `Admin`: users, access, spaces, templates, schemas, settings, and full audit

Imported drafts and native drafts use the same review and approval path only after the import workbench conversion step.

## Approve Or Reject Revisions

Review in this order:

1. open object detail
2. inspect what changed
3. verify evidence, owner, and review cadence
4. inspect writeback preview and downstream impact when related objects or services may be affected

Useful routes:

- `/read/object/{object_id}`
- `/read/object/{object_id}/revisions`
- `/review/impact/object/{object_id}`
- `/governance/services/{service_id}`

Approval should mean the current revision is operationally usable and adequately supported. Reject when the object is materially wrong, weakly evidenced, poorly scoped, or missing governance metadata.

Current repository boundary:

- the repository exposes governed operator actions through shared application flows backed by the lifecycle state machines, policy authority, and transactional mutation journal
- reviewer assignment, approval, rejection, supersession, suspect marking, and validation-run recording all leave audit evidence
- CLI, API, and web render backend action descriptors, acknowledgement contracts, operator messages, and `ui_projection` guidance; they should not restate lifecycle or policy meaning locally
- if a manage screen needs governed truth that is missing, extend the backend contract or projection layer instead of adding route-local policy logic

## Inspect Activity, Audit, And Revision History

Use object detail, activity history, and revision history to answer:

- what changed
- who submitted or reviewed it
- whether prior approved revisions were superseded
- whether the current trust posture was degraded by later change
- what should be revalidated or reviewed next

## Run Stale And Content-Health Checks

Stale review posture:

```bash
python3 scripts/report_stale.py
python3 scripts/report_stale.py --include-deprecated
```

Content-health and governance posture:

```bash
python3 scripts/report_content_health.py
python3 scripts/report_content_health.py --section citation-health --section suspect-objects
python3 scripts/report_content_health.py --section missing-owners --section duplicates
```

Use these reports to find overdue review, broken evidence, suspect objects, duplicate coverage, and discoverability gaps.

## Evaluate Suspect Objects And Evidence Posture

Treat these as escalation conditions:

- `suspect` trust state after dependency or service change
- `weak_evidence` caused by missing, broken, or low-quality citations
- objects with no owner or no clear responsible team
- current guidance that is active but overdue for review

Use these routes when intervening:

- `/review/object/{object_id}/suspect`
- `/review/object/{object_id}/supersede`
- `/review/validation-runs/new`
- `/admin/audit`

The JSON API remains operator-oriented and exposes its own non-role-prefixed endpoints. Any future role-scoped API contract requires a separate decision and migration.
