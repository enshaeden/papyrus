# Read Playbook

Use this playbook when you need the right operational guidance and need to know whether it is safe to rely on.

## Build Or Refresh The Runtime

```bash
python3 scripts/build_index.py
```

Outcome:
- Search, queue, trust, service, and impact views reflect the current repository state.

Failure signals:
- The command cannot rebuild `build/knowledge.db`.
- The web or API surfaces return runtime-unavailable errors.

## Search And Discover

Terminal:

```bash
python3 scripts/search.py vpn
python3 scripts/search.py --limit 20 "job change"
```

Browser or API:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
```

- Web queue route: `/queue`
- Web trust dashboard route: `/dashboard/trust`
- API queue route: `/queue`

Use search when you know the topic. Use the queue, trust dashboard, or service detail views when you need to browse by operational posture.

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

Failure signals:
- Missing or weak citations.
- Overdue review dates.
- Suspect-object flags caused by upstream change.
- No clear owner for escalation.

## Read The Object, Evidence, And Related Context

From the runtime-backed surfaces, inspect:

- Object detail for summary, status, owner, and service fit.
- Revision history for what changed and who approved it.
- Citations for the evidence behind the claims.
- Related objects and impact views for dependencies and follow-on work.

Useful routes:

- Web object detail: `/objects/{object_id}`
- Web revision history: `/objects/{object_id}/revisions`
- Web service detail: `/services/{service_id}`
- Web impact view: `/impact/object/{object_id}`
- API equivalents under the same route names on the local API server

## Follow Common Navigation Paths

When starting from a service issue:

1. Open the service detail view.
2. Read the linked runbook for the operational procedure.
3. Check related known errors for symptom-specific failures.
4. Open impact views if the issue may affect dependent objects or services.

When starting from a known error:

1. Read the symptom and evidence first.
2. Follow linked runbooks for the approved operator action.
3. Check revision history if the workaround or fix looks recent or disputed.

## Flag Stale Or Suspect Knowledge

Escalate or avoid reliance when:

- the object is overdue for review
- the trust state is not `trusted`
- citations are broken, missing, or obviously inherited from weak migration provenance
- related objects or services show recent change that may invalidate the current guidance

Use the manage playbook when you need to review the queue or audit why an object is suspect.
