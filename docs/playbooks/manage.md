# Manage Playbook

Use this playbook when you review revisions, make lifecycle decisions, monitor knowledge health, or inspect the consequence trail behind a change.

## Refresh The Runtime Before Review

```bash
python3 scripts/build_index.py
```

Outcome:
- Queue ordering, trust state, citations, and impact views reflect current source and runtime state.

Failure signals:
- runtime build errors
- stale queue or trust data after source changes

## Start With Review Or Knowledge Health

Open the runtime-backed queue:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
python3 scripts/operator_view.py manage-queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db
```

- Web review route: `/review`
- Web knowledge health route: `/health`
- Web activity route: `/activity`

Use these surfaces by purpose:

- `Review / Approvals`: ready for review, needs decision, drafts and rework
- `Knowledge Health`: stale guidance, weak evidence, suspect objects, superseded but still relied-on guidance
- `Activity / History`: recent consequences, validation outcomes, and writeback/audit recovery context

## Approve Or Reject Revisions

Review in this order:

1. open object detail
2. inspect what changed
3. verify evidence, owner, and review cadence
4. inspect writeback preview and downstream impact when related objects or services may be affected

Useful routes:

- `/objects/{object_id}`
- `/objects/{object_id}/revisions`
- `/impact/object/{object_id}`
- `/services/{service_id}`

Approval should mean the current revision is operationally usable and adequately supported. Reject when the object is materially wrong, weakly evidenced, poorly scoped, or missing governance metadata.

Current repository boundary:

- the repository exposes governed operator actions through the shared application layer and thin CLI, API, and web surfaces
- reviewer assignment, approval, rejection, supersession, suspect marking, and validation-run recording all leave audit evidence

## Inspect Activity, Audit, And Revision History

Use object detail, activity history, and revision history to answer:

- what changed
- who submitted or reviewed it
- whether prior approved revisions were superseded
- whether the current trust posture was degraded by later change
- what should be revalidated or reviewed next

If the trail is unclear, do not approve the revision until the author updates the source and change summary.

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

Use knowledge health for trend and stewardship visibility:

- Web knowledge health route: `/health`
- API trust dashboard route: `/dashboard/trust`
- CLI knowledge health: `python3 scripts/operator_view.py health --db build/knowledge.db`

Additional governed manage routes:

- `/manage/objects/{object_id}/suspect`
- `/manage/objects/{object_id}/supersede`
- `/manage/validation-runs/new`

## Recover Or Inspect Canonical Writeback

If a reviewer needs to understand or recover canonical source state:

```bash
python3 scripts/source_sync.py preview --object <object_id>
python3 scripts/source_sync.py restore-last --object <object_id>
```

Use these commands when the writeback needs explicit inspection or rollback. Do not recover by manually editing generated output.

## Use Papyrus As A Stewardship Surface

Papyrus is the place to judge whether guidance is current, owned, reviewed, supported by evidence, and still safe after change. Use canonical Markdown for authored content, and use review, knowledge health, activity, service, and impact views to shepherd that content through its lifecycle.
