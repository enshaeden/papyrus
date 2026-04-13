# Write Playbook

Use this playbook when you are creating, importing, or revising canonical knowledge and need to move it cleanly through the lifecycle from draft to review.

Write is still governed, but the surrounding UX now assumes `Read` is article-first and operator-centered while broader role separation remains transitional. Authoring should improve the operator article surface, not add governance-first chrome.

## Start With The Guided Blueprint Flow

The primary web path is now:

1. create object shell
2. choose or confirm the blueprint
3. complete the guided section flow
4. validate and submit for review

Use the write surface when you want Papyrus to show progress, required versus optional work, evidence posture, and what will happen if the revision is approved.

When revising an existing object, optimize for the eventual article flow:

- summary should explain what the guidance is for
- purpose and scope should make `when to use` obvious
- procedure should be operator-readable without opening raw Markdown
- verification, rollback, and escalation should be explicit because they now sit in fixed article positions

Current primary authoring rules:

- Papyrus does not use a generic rich-text editor as the primary authoring surface.
- Papyrus stores structured section data and derives the Markdown body from that structure.
- Blueprints define required sections, ordering, validation, evidence expectations, and lifecycle defaults.
- The visible next action should always be the next required section or the submit step.
- Guided section editing is the primary web authoring path.
- Guided section editing now includes citation lookup and searchable multi-select controls for related guidance, services, and controlled tags.
- Presenter or template code must not regex-assemble article structure from Markdown headings when structured section content already exists.

Current first-class blueprints:

- `runbook`
- `known_error`
- `service_record`
- `policy`
- `system_design`

## Understand Blueprints Versus Templates

Blueprints are the authoritative runtime structure for authoring and ingestion. They define:

- which sections exist
- which sections are required
- how completion is measured
- what evidence is required before review
- what lifecycle defaults a new draft starts with

Approved Markdown templates still exist for repository-side source scaffolding and controlled file generation. They are not the primary authoring experience. If Papyrus is guiding a draft in the web UI, CLI, or API, the blueprint is the source of structure and validation.

## Create A Canonical Source Object

For the guided CLI path, start with a blueprint-backed draft:

```bash
python3 scripts/operator_view.py create-draft \
  --type runbook \
  --object-id kb-example-runbook \
  --title "Example Runbook" \
  --summary "Example guided draft." \
  --owner it_operations \
  --team "IT Operations" \
  --canonical-path knowledge/examples/example-runbook.md
```

Then fill sections incrementally:

```bash
python3 scripts/operator_view.py edit-section \
  --object kb-example-runbook \
  --revision <revision_id> \
  --section purpose \
  --field use_when="Use this when the governed workflow applies."

python3 scripts/operator_view.py show-progress \
  --object kb-example-runbook \
  --revision <revision_id>
```

The repository scaffold path still exists when you explicitly need a canonical file created up front:

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
- In the guided web flow, the shell becomes step 1 and Papyrus sends you directly into blueprint-driven drafting.

Failure signals:
- The type or taxonomy value is not approved.
- Required fields remain placeholder text.

## Import External Documents Through The Workbench

Use the import workbench when the source starts as Markdown, DOCX, or a text-based PDF and must be normalized before it becomes Papyrus knowledge.

Web path:

1. open `/operator/import`
2. upload the file, or provide a local host path only on a trusted local operator web surface with explicit opt-in
3. inspect parse output, parser warnings, and extraction quality
4. review the blueprint mapping, including conflicts, low-confidence matches, and unmapped content
5. confirm conversion to a governed draft
6. continue editing in the normal write flow

CLI path:

```bash
python3 scripts/ingest.py path/to/source.docx
python3 scripts/operator_view.py list-ingestions
python3 scripts/operator_view.py review-ingestion <ingestion_id>
python3 scripts/operator_view.py convert-ingestion <ingestion_id> \
  --object-id kb-imported-example \
  --title "Imported Example" \
  --canonical-path knowledge/imported/imported-example.md \
  --owner it_operations \
  --team "IT Operations"
```

Guardrails:

- browser upload is the standard web ingest path
- browser-submitted local file paths are disabled unless the local operator explicitly enables `--allow-web-ingest-local-paths`; when enabled, the path must be absolute and is read from the machine running Papyrus
- Markdown and DOCX ingest locally; PDF import is limited to text-based PDFs, and scanned, image-only, encrypted, or heavily font-encoded PDFs require external OCR or preprocessing
- import does not create canonical knowledge automatically
- import does not bypass review
- parser warnings and degraded extraction must stay visible before conversion
- mapping gaps, conflicts, low-confidence matches, and unmapped content must stay visible before conversion
- converted content becomes the same structured draft model used by native authoring

## Revise An Existing Object

1. Keep the existing object identity and canonical path stable unless a governed structural change requires otherwise.
2. Update the blueprint sections rather than treating the revision as a freeform blob.
3. Use the runtime-backed revision flow when you want lifecycle progress, citation cues, and reviewer handoff context.

Do not create a parallel source file when the work is a revision of an existing object.

## Attach Citations Correctly

For each material claim:

- add a citation with a resolvable target
- include capture metadata when available
- keep the citation specific enough that another operator can re-check it
- prefer direct evidence over inherited provenance notes

Current web authoring boundary:

- guided section editing at `/operator/write/object/{object_id}?revision_id=...` is the primary web path after a draft already exists
- web draft creation or reuse starts through object setup or the explicit `POST /operator/write/object/{object_id}/start` action; the guided GET route itself is load-only
- the guided path owns citation lookup and searchable multi-select controls
- write and submit screens render backend workflow projections, action descriptors, operator messages, and acknowledgement requirements instead of deriving review or publication meaning in the route
- citations that point to existing governed local Papyrus content are lightweight internal references for traceability and review context
- external, migration, or other manual evidence entered through the write form remains weak until follow-up records when the evidence was captured, stores an integrity hash, and attaches any required snapshot
- the web write form can record source title, source reference, source type, and note only
- the web write form does not currently record `captured_at`, `integrity_hash`, expiry metadata, or evidence snapshots directly; use the manage-side evidence follow-up path after the revision exists
- retained technical debt: evidence capture metadata still requires the manage-side follow-up path rather than the primary write form

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
- The guided submit step shows validation blockers, warnings, progress, and whether the revision is ready for review.

Failure signals:
- validation errors on metadata, taxonomy, links, citations, or canonical paths
- required blueprint sections remain incomplete
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
- what evidence posture supports it
- what remains unresolved
- what the canonical writeback would change if approved

Use the runtime-backed queue and revision history surfaces during review so the revision is judged as a tracked object revision, not as a detached Markdown diff.

Current repository boundary:

- inspection happens through the runtime-backed queue, revision, CLI parity, and object detail views
- approval-state changes are tracked through explicit `revision_review_state`, `object_lifecycle_state`, `draft_progress_state`, and `source_sync_state` transitions rather than through ad-hoc file or database edits
- approved revisions become canonical guidance through explicit source-sync preview and approval flow, not through hidden source mutation
- imported drafts and native drafts enter the same review path after conversion

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
- `preview` also reports the proposed `source_sync_state`, required acknowledgements, and which prior assumptions stop being safe after apply.
- startup and governed writeback entry points run pending mutation recovery before preview, apply, or restore proceed
- `restore-last` restores the most recent backed-up canonical state, records the recovery in the audit trail, and leaves the object in explicit `restored` source-sync state.
