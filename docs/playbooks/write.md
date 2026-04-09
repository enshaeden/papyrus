# Write Playbook

Use this playbook when you are creating or revising canonical knowledge and need to move it cleanly through the lifecycle from draft to review.

## Start With The Guided Authoring Flow

The primary web path is now:

1. create object shell
2. draft or revise the structured guidance
3. validate and submit for review

Use the write surface when you want Papyrus to show progress, required versus optional work, evidence gaps, and what will happen if the revision is approved.

## Create A Canonical Source Object

Start with the approved scaffold:

```bash
python3 scripts/new_article.py --type runbook --title "Example Procedure"
```

List valid taxonomy values before you choose metadata:

```bash
python3 scripts/new_article.py --list-taxonomy knowledge_object_types
python3 scripts/new_article.py --list-taxonomy services
python3 scripts/new_article.py --list-taxonomy systems
python3 scripts/new_article.py --list-taxonomy tags
```

Outcome:
- A new canonical Markdown source file is created under `knowledge/`.
- In the guided web flow, the shell becomes step 1 of 3 and Papyrus sends you directly into revision drafting.

Failure signals:
- The type or taxonomy value is not approved.
- Required fields remain placeholder text.

## Revise An Existing Object

1. Keep the existing object identity and canonical path stable unless a governed structural change requires otherwise.
2. Update the body, metadata, and change log together.
3. Use the runtime-backed revision flow when you want lifecycle progress, citation cues, and reviewer handoff context.

Do not create a parallel source file when the work is a revision of an existing object.

## Attach Citations Correctly

For each material claim:

- add a citation with a resolvable target
- include capture metadata when available
- keep the citation specific enough that another operator can re-check it
- prefer direct evidence over inherited provenance notes

Current web authoring boundary:

- citations that point to existing governed local Papyrus content are treated as internal references
- external, migration, or other manual evidence remains weak until follow-up records when the evidence was captured and attaches an integrity-backed snapshot
- the web write form does not currently attach evidence snapshots directly; use the manage-side evidence follow-up path after the revision exists

Failure signals:

- the cited local target does not exist
- the citation has no usable capture metadata
- the citation is too vague to support the claim it is attached to

## Validate Before Submission

Run:

```bash
python3 scripts/validate.py
python3 scripts/build_index.py
```

Then review health signals that commonly catch authoring problems:

```bash
python3 scripts/report_content_health.py --section duplicates
python3 scripts/report_content_health.py --section broken-links
python3 scripts/report_content_health.py --section citation-health
```

Outcome:
- Source passes repository policy checks.
- Runtime search and trust views reflect the revision.
- The guided submit step shows validation blockers, warnings, and whether the revision is ready for review.

Failure signals:
- validation errors on metadata, taxonomy, links, citations, or canonical paths
- duplicate-title or isolated-object warnings that indicate poor discoverability

## Submit For Review

Submission starts after the source is valid and the runtime reflects the new revision.

At minimum, hand off:

- the canonical file path
- the change summary
- the validation result
- any citation or trust caveats the reviewer should inspect

Reviewer-facing decision support now includes:

- what changed
- what evidence supports it
- what remains unresolved
- what the canonical writeback would change if approved

Use the runtime-backed queue and revision history surfaces during review so the revision is judged as a tracked object revision, not as a detached Markdown diff.

Current repository boundary:

- inspection happens through the runtime-backed queue, revision, CLI parity, and object detail views
- approval-state changes are tracked in the governance workflow layer rather than through ad-hoc file or database edits
- approved revisions become canonical guidance through explicit writeback preview and approval flow, not through hidden source mutation

## Handle Rejection Or Follow-Up Revision

If review rejects or questions the revision:

1. update the same canonical object rather than forking it
2. resolve citation, ownership, or scope issues directly in source
3. rerun validation and rebuild the runtime
4. resubmit with a clear change summary

Do not bypass review by patching generated output or by copying the content into `docs/`.

## Inspect Or Recover Source Writeback

Use the governed source-sync commands when you need to inspect or recover canonical writeback:

```bash
python3 scripts/source_sync.py preview --object <object_id>
python3 scripts/source_sync.py writeback --object <object_id>
python3 scripts/source_sync.py restore-last --object <object_id>
```

- `preview` shows the changed fields, changed sections, and whether the canonical source has drifted unexpectedly.
- `restore-last` restores the most recent backed-up canonical state and records the recovery in the audit trail.
