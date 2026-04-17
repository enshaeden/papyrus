# Write Playbook

Use this playbook when you are creating, importing, or revising canonical knowledge and need to move it cleanly through the lifecycle from draft to review.

## Start With The Primary Template Flow

The primary web path is:

1. open `/write` or `/write/new`
2. choose the primary template
3. complete the guided section flow
4. validate and submit for review

Use the write surface when you want Papyrus to show progress, required versus optional work, evidence posture, and what will happen if the revision is approved.

Current primary authoring rules:

- Papyrus does not use a generic rich-text editor as the primary authoring surface.
- Papyrus stores structured section data and derives rendered content from that structure.
- Blueprints define required sections, ordering, validation, evidence expectations, and lifecycle defaults.
- The visible next action should always be the next required section or the submit step.
- Guided section editing is the primary web authoring path.
- Guided section editing includes citation lookup and searchable multi-select controls for related guidance, services, and controlled tags.
- Presenter or template code must not regex-assemble content structure from Markdown headings when structured section content already exists.

Primary visible templates:

- `runbook`
- `known_error`
- `service_record`

## Understand Blueprints Versus Templates

Blueprints are the authoritative runtime structure for authoring and ingestion. They define:

- which sections exist
- which sections are required
- how completion is measured
- what evidence is required before review
- what lifecycle defaults a new draft starts with

Approved Markdown templates still exist for repository-side source scaffolding and controlled file generation. They are not the primary authoring experience. If Papyrus is guiding a draft in the web UI, CLI, or API, the blueprint is the source of structure and validation.

## Create A Governed Draft

For the guided CLI path, start with a blueprint-backed draft:

```bash
python3 scripts/operator_view.py create-draft \
  --db build/knowledge.db \
  --source-root /path/to/workspace \
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
  --db build/knowledge.db \
  --source-root /path/to/workspace \
  --object kb-example-runbook \
  --revision <revision_id> \
  --section purpose \
  --field use_when="Use this when the governed workflow applies."

python3 scripts/operator_view.py show-progress \
  --db build/knowledge.db \
  --source-root /path/to/workspace \
  --object kb-example-runbook \
  --revision <revision_id>
```

Outcome:

- A governed draft exists for the object under the explicit workspace source root.
- In the guided web flow, object setup creates the first draft before redirecting into blueprint-driven drafting.

## Import External Documents Through The Workbench

Use the import workbench when the source starts as Markdown, plain text, reStructuredText, RTF, DOCX, ODT, HTML, CSV, or a text-based PDF and must be normalized before it becomes Papyrus knowledge.

Web path:

1. open `/import`
2. upload the file, or provide a local host path only on a trusted local operator web surface with explicit opt-in
3. inspect parse output, parser warnings, and extraction quality
4. review the mapped draft target, including conflicts, low-confidence matches, and unmapped content
5. confirm conversion to a governed draft
6. continue editing in the normal write flow

CLI path:

```bash
python3 scripts/ingest.py --source-root /path/to/workspace path/to/source.docx
python3 scripts/operator_view.py list-ingestions
python3 scripts/operator_view.py review-ingestion <ingestion_id>
python3 scripts/operator_view.py convert-ingestion <ingestion_id> \
  --db build/knowledge.db \
  --source-root /path/to/workspace \
  --object-id kb-imported-example \
  --title "Imported Example" \
  --canonical-path knowledge/imported/imported-example.md \
  --owner it_operations \
  --team "IT Operations"
```

Guardrails:

- browser upload is the standard web ingest path
- browser-submitted local file paths are disabled unless the local operator explicitly enables `--allow-web-ingest-local-paths`
- import does not create canonical knowledge automatically
- import does not bypass review
- parser warnings, mapping gaps, conflicts, low-confidence matches, and unmapped content must stay visible before conversion
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

- `/write` and `/write/new` are the primary visible entrypoints for the default template set
- guided section editing at `/write/object/{object_id}?revision_id=...` is the primary web path after a draft already exists
- web draft creation or reuse starts through object setup or the explicit `POST /write/object/{object_id}/start` action; the guided GET route itself is load-only
- the guided path owns citation lookup and searchable multi-select controls
- write and submit screens render backend workflow projections, action descriptors, operator messages, and acknowledgement requirements instead of deriving review or publication meaning in the route

## Validate Before Submission

Run:

```bash
python3 scripts/validate.py
python3 scripts/build_index.py --source-root /path/to/workspace
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

## Submit For Review

Submission starts after the source is valid and the runtime reflects the new revision.

At minimum, hand off:

- the canonical file path
- the change summary
- the validation result
- any citation or trust caveats the reviewer should inspect

Reviewer-facing decision support includes:

- what changed
- what evidence posture supports it
- what remains unresolved
- what the canonical writeback would change if approved

Use the runtime-backed queue and revision history surfaces during review so the revision is judged as a tracked object revision, not as a detached Markdown diff.
