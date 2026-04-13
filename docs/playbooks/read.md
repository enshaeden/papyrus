# Read Playbook

Use this playbook when you need the right operational guidance, need to know whether it is safe to rely on, and need a readable article with a clear next step if it is not.

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
python3 scripts/operator_view.py queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py object kb-troubleshooting-vpn-connectivity --db build/knowledge.db
```

Browser or API:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
```

- Web operator home route: `/operator`
- Web read route: `/operator/read`
- Web knowledge health route: `/operator/review/governance`
- API queue route: `/queue`

Use search when you know the topic. Use the home page, read workspace, service map, or knowledge-health board when you need to browse by role, service context, or operational posture.

Use the operator CLI when you need parity checks without opening the browser:

- `python3 scripts/operator_view.py queue --db build/knowledge.db`
- `python3 scripts/operator_view.py health --db build/knowledge.db`
- `python3 scripts/operator_view.py object <object_id> --db build/knowledge.db`
- `python3 scripts/operator_view.py activity --db build/knowledge.db`

## Use The Two-Step Read Flow

1. Use `/operator/read` as the selection workspace.
2. Open the object detail page to read the article in operational order.

What the article surface prioritizes:

- title and short summary
- when to use it
- prerequisites and scope
- steps or guidance
- verification
- rollback and recovery
- escalation and boundaries
- linked service context

Governance, evidence posture, and raw revision source stay secondary so the article reads like an operational document first.

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

## Read The Article, Then The Supporting Context

From the runtime-backed surfaces, inspect:

- Object detail for article guidance first, then safe-to-use posture, last review, service fit, and what changed recently.
- Revision history for what changed and who approved it.
- Supporting evidence for the claims behind the guidance.
- Related objects, service detail, activity history, and impact views for dependencies and follow-on work.

Useful routes:

- Web object detail: `/operator/read/object/{object_id}`
- Web revision history: `/operator/read/object/{object_id}/revisions`
- Web service detail: `/operator/read/services/{service_id}`
- Web activity history: `/operator/review/activity`
- Web impact view: `/operator/review/impact/object/{object_id}`
- The JSON API remains operator-oriented and uses its own non-role-prefixed operator routes such as `/queue`, `/objects/{object_id}`, `/services/{service_id}`, and `/impact/object/{object_id}`.

## Follow Common Navigation Paths

When starting from a service issue:

1. Open the service detail view.
2. Read the linked runbook for the operational procedure.
3. Check related known errors for symptom-specific failures.
4. Open activity or impact views if the issue may affect dependent objects or services.

When starting from a known error:

1. Read the symptom and evidence first.
2. Follow linked runbooks for the approved operator action.
3. Check revision history if the workaround or fix looks recent or disputed.
4. If safety or freshness is degraded, move to review or knowledge health instead of relying on the guidance immediately.

## Flag Stale Or Suspect Knowledge

Escalate or avoid reliance when:

- the object is overdue for review
- the trust state is not `trusted`
- citations are broken, missing, or obviously inherited from weak migration provenance
- related objects or services show recent change that may invalidate the current guidance

Use the manage playbook when you need to review the queue or audit why an object is suspect.
