# Read Playbook

Use this playbook when you need dependable content, need to know whether it is safe to rely on, and need a clear next step if it is not.

## Build Or Refresh The Runtime

```bash
python3 scripts/build_index.py --source-root /path/to/workspace
```

Outcome:

- Search, queue, trust, service, and impact views reflect the current runtime DB plus the explicit source workspace that produced it.

Failure signals:

- The command cannot rebuild `build/knowledge.db`.
- The web or API surfaces return runtime-unavailable errors.

## Search And Discover

Terminal:

```bash
python3 scripts/search.py vpn
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
```

Browser or API:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
```

- Shared entrypoint: `/`
- Reader landing: `/read`
- Operator landing: `/review`
- Admin landing: `/admin/overview`
- API queue route: `/queue`

Use search when you know the topic. Use the read workspace when you need to browse current guidance. Use governance or service views when service context or operational posture matters.

The JSON API remains operator-oriented. It is not part of the role-scoped web route contract.

## Use The Two-Step Content Flow

1. Use `/read` as the selection workspace.
2. Open the object detail page to read the content in operational order.

What the content surface prioritizes:

- title and short summary
- when to use it
- prerequisites and scope
- steps or guidance
- verification
- rollback and recovery
- escalation and boundaries

Governance, evidence posture, and raw revision source stay secondary so the reading surface stays dependable first.

## Check Trust Posture Before Acting

Treat these as the minimum checks:

- Approval state: prefer approved current revisions.
- Trust state: investigate `suspect`, `stale`, or `weak_evidence` signals before use.
- Review cadence: compare `last_reviewed` with the stated cadence.
- Ownership: confirm the object has a clear owner or responsible team.

Useful checks:

```bash
python3 scripts/report_stale.py
python3 scripts/report_content_health.py --section citation-health --section suspect-objects
```

## Use The Object, Then The Supporting Context

From the runtime-backed surfaces, inspect:

- object detail for current guidance first, then safe-to-use posture, last review, service fit, and what changed recently
- revision history for what changed and who approved it
- supporting evidence for the claims behind the guidance
- related objects, service detail, activity history, and impact views for dependencies and follow-on work

Useful routes:

- Web object detail: `/read/object/{object_id}`
- Web revision history: `/read/object/{object_id}/revisions`
- Web governance services: `/governance/services/{service_id}`
- Web activity history: `/review/activity`
- Web impact view: `/review/impact/object/{object_id}`
- The JSON API remains operator-oriented and uses its own non-role-prefixed operator routes such as `/queue`, `/objects/{object_id}`, `/services/{service_id}`, and `/impact/object/{object_id}`.

## Flag Stale Or Suspect Knowledge

Escalate or avoid reliance when:

- the object is overdue for review
- the trust state is not `trusted`
- citations are broken, missing, or obviously inherited from weak provenance
- related objects or services show recent change that may invalidate the current guidance

Use the review and governance playbook when you need to inspect queue posture, audit why an object is suspect, or intervene on service-linked guidance.
