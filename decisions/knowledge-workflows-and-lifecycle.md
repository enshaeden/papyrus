# Knowledge Workflows and Lifecycle

Scope: knowledge-object lifecycle, revision review workflow, draft progress, and flag handling.

## Purpose

This record defines the lifecycle vocabulary Papyrus uses across code, documentation, and operator workflows.

These concerns MUST remain distinct and MUST NOT be collapsed into a single mixed status list.

- Object lifecycle describes the canonical state of the knowledge object.
- Revision review describes the governance state of a specific revision.
- Draft progress describes whether a draft is structurally ready to hand off for review.
- Flag handling is a separate workflow attached to an object or revision.

This record does not claim that every possible route, transition path, or role-specific screen is already shipped.

## Canonical State Machines

A knowledge object MUST store `object_lifecycle_state`, `revision_review_state`, and `draft_progress_state` as distinct canonical state machines.

The system MAY derive a combined presentation label in the form `object_lifecycle_state : qualifier` for display and workflow use. Labels such as `draft: in_progress`, `draft: ready_for_review`, and `active: published` are derived projections and MUST NOT be treated as authoritative stored states.

At the model level, canonical workflow state is represented by:

- `object_lifecycle_state`
- `revision_review_state`
- `draft_progress_state`

At the presentation level, state MAY be projected as:

`document_state = object_lifecycle_state : qualifier`

Where `qualifier` is derived from the applicable subordinate state machine or publication condition.

Examples:

- `draft: in_progress`
- `draft: ready_for_review`
- `draft: in_review`
- `active: published`
- `deprecated: published`
- `archived: superseded`

### `object_lifecycle_state`

This state belongs to the knowledge object.

Allowed values:

- `draft`
- `active`
- `deprecated`
- `archived`

Rules:

- `draft` means the object shell exists but has not yet become active guidance.
- `active` means the object may be surfaced as current guidance when an eligible revision is approved and reader-safe.
- `deprecated` means the object remains readable for context but should be replaced over time.
- `archived` means the object is retired from normal guidance flows and preserved for traceability.

The following are not object lifecycle states:

- `in_progress`
- `in_review`
- `approved`
- `rejected`
- `superseded`
- `blocked`
- `ready_for_review`
- `published`

### `revision_review_state`

This state belongs to a specific revision.

Allowed values:

- `in_progress`
- `in_review`
- `approved`
- `rejected`
- `superseded`

Rules:

- `in_progress` means the revision is still being authored or reworked.
- `in_review` means the revision is awaiting explicit governance action.
- `approved` means the revision cleared review.
- `rejected` means the revision did not clear review and must be revised before resubmission.
- `superseded` means a later approved revision replaced it.

`published` is not a canonical revision review state.

### `draft_progress_state`

This state belongs to draft progress evaluation.

`draft_progress_state` is optional until evaluated. Absence means no draft-progress determination has yet been recorded.

Allowed values:

- `blocked`
- `ready_for_review`

Rules:

- `blocked` means required structure or validation is missing.
- `ready_for_review` means required authoring gates have cleared and the revision may be submitted for review.

`draft_progress_state` does not replace `revision_review_state`.

A draft may be `ready_for_review` before its revision enters `in_review`.

### Projection Rules

The system MAY derive a combined `document_state` for display, filtering, or workflow cues.

#### Draft projections

When `object_lifecycle_state = draft`, the qualifier may be derived from either:

- `revision_review_state`, or
- `draft_progress_state`

Valid examples include:

- `draft: in_progress`
- `draft: in_review`
- `draft: rejected`
- `draft: ready_for_review`
- `draft: blocked`

These qualifiers do not change the underlying object lifecycle state. They describe the current revision state or draft-readiness condition within the draft lifecycle.

#### Published projections

When `object_lifecycle_state = active` or `deprecated`, the qualifier may be `published` if all of the following are true:

- the current revision is `approved`
- the revision is currently designated for surfacing
- the revision is eligible for reader presentation

Accordingly:

- `active: published` means the object is live guidance backed by an approved surfaced revision
- `deprecated: published` means the object is still surfaced for readers, but as guidance intended for replacement

`published` is a derived publication condition, not a canonical stored state.

`published` MUST NOT be projected when `object_lifecycle_state = archived`.

#### Superseded projections

When a revision has been replaced by a later approved revision, the qualifier may be projected as `superseded` where useful for traceability, historical views, or operator workflows.

Example:

- `archived: superseded`

### Constraints

- Canonical storage must keep lifecycle, review, and draft-progress states distinct.
- Projection must not collapse the underlying state machines into a single stored state field.
- `approved` and `published` are not interchangeable.
- `approved` is canonical; `published` is derived.

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
- a revision is currently designated for surfacing
- that revision is `approved`
- that revision is surfaced according to role visibility rules

Approval of a revision does not by itself require promotion of the object to `active`.

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

## Experience Boundary Reference

Reader, Operator, and Admin experience boundaries, visibility rules, and route groups are governed by `role-scoped-experience-architecture.md`.

This record does not redefine role-specific UI or shell policy.

## Non-Goals

This record does not define:

- a separate generic `published` status
- actor-shaped shell behavior
- presentation-layer layout decisions
- future flag-state taxonomy that has not yet been implemented