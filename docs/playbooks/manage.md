# Manage Playbook

Use this playbook when you review revisions, audit trust posture, or govern the knowledge corpus.

## Refresh The Runtime Before Review

```bash
python3 scripts/build_index.py
```

Outcome:
- Queue ordering, trust state, citations, and impact views reflect current source and runtime state.

Failure signals:
- runtime build errors
- stale queue or trust data after source changes

## Review The Queue

Open the runtime-backed queue:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
```

- Web queue route: `/queue`
- API queue route: `/queue`

Use the queue to prioritize items with non-approved state, weak evidence, missing ownership, or suspect trust posture.

## Approve Or Reject Revisions

Review in this order:

1. open object detail
2. inspect revision history
3. verify evidence, owner, and review cadence
4. inspect impact when related objects or services may be affected

Useful routes:

- `/objects/{object_id}`
- `/objects/{object_id}/revisions`
- `/impact/object/{object_id}`
- `/services/{service_id}`

Approval should mean the current revision is operationally usable and adequately supported. Reject when the object is materially wrong, weakly evidenced, poorly scoped, or missing governance metadata.

Current repository boundary:

- the repository exposes review inspection through the runtime-backed web and API surfaces
- approval and rejection remain governance workflow actions, not standalone top-level reviewer scripts in this repository

## Inspect Audit And Revision History

Use object detail and revision history to answer:

- what changed
- who submitted or reviewed it
- whether prior approved revisions were superseded
- whether the current trust posture was degraded by later change

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

Use the trust dashboard for trend and queue visibility:

- Web trust dashboard route: `/dashboard/trust`
- API trust dashboard route: `/dashboard/trust`

## Use Papyrus As A Governance Surface

Papyrus is the place to judge whether knowledge is current, owned, reviewed, and supported by evidence. Use canonical Markdown for authored content, and use the runtime queue, trust, revision, service, and impact views to govern that content as an operational system.
