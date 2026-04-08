# Write Playbook

Use this playbook when you are creating or revising canonical knowledge.

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

Failure signals:
- The type or taxonomy value is not approved.
- Required fields remain placeholder text.

## Revise An Existing Object

1. Edit the canonical file under `knowledge/` or `archive/knowledge/`.
2. Update the body, metadata, and change log together.
3. Keep the existing object identity and canonical path stable unless a governed structural change requires otherwise.

Do not create a parallel source file when the work is a revision of an existing object.

## Attach Citations Correctly

For each material claim:

- add a citation with a resolvable target
- include capture metadata when available
- keep the citation specific enough that another operator can re-check it
- prefer direct evidence over inherited provenance notes

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

Use the runtime-backed queue and revision history surfaces during review so the revision is judged as a tracked object revision, not as a detached Markdown diff.

Current repository boundary:

- inspection happens through the runtime-backed queue, revision, CLI parity, and object detail views
- approval-state changes are tracked in the governance workflow layer rather than through ad-hoc file or database edits

## Handle Rejection Or Follow-Up Revision

If review rejects or questions the revision:

1. update the same canonical object rather than forking it
2. resolve citation, ownership, or scope issues directly in source
3. rerun validation and rebuild the runtime
4. resubmit with a clear change summary

Do not bypass review by patching generated output or by copying the content into `docs/`.
