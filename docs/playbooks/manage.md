# Oversight Playbook

Use this playbook when you review revisions, make lifecycle decisions, monitor content risk, or inspect recent change and audit history.

The oversight surfaces are intentionally distinct:

- `Review` is a dense reviewer workbench
- `Oversight` is an intervention board grouped by debt type
- `History` is a recent change and audit feed

## Refresh The Runtime Before Review

```bash
python3 scripts/build_index.py
```

Outcome:
- Queue ordering, trust state, citations, and impact views reflect current source and runtime state.

Failure signals:
- runtime build errors
- stale queue or trust data after source changes

## Start With Review Or Oversight

Open the runtime-backed queue:

```bash
python3 scripts/serve_web.py
python3 scripts/serve_api.py
python3 scripts/operator_view.py manage-queue --db build/knowledge.db
python3 scripts/operator_view.py health --db build/knowledge.db
python3 scripts/operator_view.py activity --db build/knowledge.db
```

- Web review route: `/operator/review`
- Web oversight route: `/operator/review/governance`
- Web history route: `/operator/review/activity`

Use these surfaces by purpose:

- `Review`: ready for review, needs decision, drafts and rework, with selected context only when it helps a decision
- `Oversight`: stale guidance, weak evidence, suspect objects, ownership gaps, and cleanup debt grouped by intervention type
- `History`: recent changes, validation outcomes, and writeback or audit recovery context, with raw payload detail behind disclosure

Imported drafts and native drafts use the same review and approval path only after the import workbench conversion step. Parser warnings, degraded extraction, mapping conflicts, low-confidence matches, and unmapped content stay in the import review stage and should not be hidden during draft conversion.

## Approve Or Reject Revisions

Review in this order:

1. open object detail
2. inspect what changed
3. verify evidence, owner, and review cadence
4. inspect writeback preview and downstream impact when related objects or services may be affected

Useful routes:

- `/operator/read/object/{object_id}`
- `/operator/read/object/{object_id}/revisions`
- `/operator/review/impact/object/{object_id}`
- `/operator/read/services/{service_id}`

Approval should mean the current revision is operationally usable and adequately supported. Reject when the object is materially wrong, weakly evidenced, poorly scoped, or missing governance metadata.

Evidence review boundary:

- governed Papyrus references are lightweight internal references for traceability and review context
- external or manual citations without capture time, integrity metadata, and any required snapshot remain weak evidence posture
- do not treat "citation entered" as proof that the revision is strongly evidenced

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

If the trail is unclear, do not approve the revision until the author updates the source and change summary.

Oversight view guidance:

- start from `Oversight` when you need to reduce risk across the portfolio
- start from `Services` when service criticality or ownership should drive intervention
- use `History` to understand recent changes before escalating process or staffing pressure

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

Use oversight for trend and review visibility:

- Web oversight route: `/operator/review/governance`
- API oversight dashboard route: `/dashboard/oversight`
- CLI oversight view: `python3 scripts/operator_view.py health --db build/knowledge.db`

Additional governed manage routes:

- `/operator/review/object/{object_id}/suspect`
- `/operator/review/object/{object_id}/supersede`
- `/operator/review/validation-runs/new`

## Recover Or Inspect Canonical Writeback

If a reviewer needs to understand or recover canonical source state:

```bash
python3 scripts/source_sync.py preview --object <object_id>
python3 scripts/source_sync.py restore-last --object <object_id>
```

Use these commands when source sync needs explicit inspection or rollback. Preview reports the proposed `source_sync_state`, required acknowledgements, and conflict posture before apply. Do not recover by manually editing generated output.

## Recovery And Acknowledgement Rules

- operator startup and governed mutation entry points run pending mutation recovery before they proceed
- Papyrus reclaims or rolls back stale journals and stale locks when it can do so safely
- if recovery cannot prove a safe result, Papyrus stops the operation and surfaces the blocking reason instead of ignoring the journal or lock
- archive, writeback, and restore acknowledgements come from backend contracts; operators should only confirm what the current contract requires

## Use Papyrus As An Oversight Surface

Papyrus is the place to judge whether guidance is current, owned, reviewed, supported by evidence, and still safe after change. Use canonical Markdown for authored content, and use review, oversight, history, service, and impact views to shepherd that content through its lifecycle.
