# Knowledge Workflows and Lifecycle

Status: Approved
Owner: Product / Operations / Architecture
Scope: Knowledge-object lifecycle, revision review workflow, draft progress, and flag handling

## Purpose

This record defines the lifecycle vocabulary Papyrus uses across code, docs, and operator workflows.

Do not collapse these concerns into one mixed status list.

- Object lifecycle describes the canonical object.
- Revision review describes the current revision under governance.
- Draft progress describes whether a draft is ready to hand off.
- Flag handling is a separate workflow attached to an object or revision.

This record does not claim that every possible route or role-specific screen is already shipped.

## Canonical State Machines

### `object_lifecycle_state`

This state belongs to the knowledge object.

- `draft`
- `active`
- `deprecated`
- `archived`

Rules:

- `draft` means the object shell exists but has not yet become active guidance.
- `active` means the object may be surfaced as current guidance when its current revision is also reader-safe.
- `deprecated` means the object remains readable for context but should be replaced over time.
- `archived` means the object is retired from normal active guidance flows and preserved for traceability.

`in_review`, `published`, and `flagged` are not object lifecycle states.

### `revision_review_state`

This state belongs to a specific revision.

- `draft`
- `in_review`
- `approved`
- `rejected`
- `superseded`

Rules:

- `draft` means the revision is still being authored or reworked.
- `in_review` means the revision is waiting on explicit governance action.
- `approved` means the revision cleared review and may become the current approved revision.
- `rejected` means the revision did not clear review and must be revised before resubmission.
- `superseded` means a later approved revision replaced it.

`published` is not a separate revision-review state.
Papyrus reaches a published/current outcome when an approved revision becomes the current approved revision for an active object.

### `draft_progress_state`

This state belongs to draft progress evaluation.

- `blocked`
- `in_progress`
- `ready_for_review`

Rules:

- `blocked` means required structure or validation is missing.
- `in_progress` means the draft can continue but is not yet ready for review.
- `ready_for_review` means the draft cleared required authoring gates and may be submitted.

`draft_progress_state` does not replace `revision_review_state`.
A draft can be `ready_for_review` before the revision enters `in_review`.

## Workflow Boundaries

### Authoring

- Create a new object shell or open an existing object through an explicit authoring entrypoint.
- Apply the blueprint structure.
- Save draft section content.
- Validate required structure and taxonomy rules.
- Submit only when `draft_progress_state = ready_for_review`.

Authoring does not overwrite current approved content directly.
Each substantive change produces or updates a governed revision.

### Review

- Review begins when a revision enters `revision_review_state = in_review`.
- Review outcomes are `approved` or `rejected`.
- Review may also trigger reassignment, evidence follow-up, or downstream impact inspection.

Review is queue-based governance work.
It is not an object lifecycle state.

### Publish / Current Guidance Outcome

Papyrus does not use a standalone `published` lifecycle state.

The effective publish/current-guidance condition is:

- `object_lifecycle_state = active`
- current revision exists
- current revision is approved and surfaced according to role visibility rules

### Archive / Deprecate

- `deprecated` keeps the object readable with replacement or caution context.
- `archived` retires the object from active guidance flows while preserving history and traceability.

## Flag Workflow

Flagging is a separate governance workflow.
Do not encode it as `object_lifecycle_state = flagged`.

Current rule:

- a flag is attached to an object or revision
- a flag may trigger review, evidence follow-up, or no content change

This decision intentionally does not assign canonical flag-state names until the flag record schema and storage contract are formalized.

## Role Expectations

- Reader surfaces consume only reader-safe guidance and do not expose review or authoring controls.
- Operator surfaces handle normal read, write, import, review, and follow-up workflows.
- Admin surfaces handle oversight, governance pressure, audit, and intervention workflows without blending in operator authoring routes.

Role visibility is governed separately by:

- `docs/decisions/role-experience-visibility-matrix.md`
- `docs/decisions/route-separation-and-experience-boundaries.md`

## Non-Goals

This record does not define:

- a separate generic `published` status
- actor-shaped shell behavior
- presentation-layer layout decisions
- future flag-state taxonomy that has not yet been implemented
