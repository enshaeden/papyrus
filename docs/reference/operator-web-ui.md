# Operator Web UI

This document describes the current Papyrus operator web interface after the server-rendered UI refactor.

## Purpose And Scope

- Provide a stable operator shell for three modes of use: read, write, and manage.
- Keep the shell task-driven so the main work surface stays larger, secondary panels stay conditional, and the next action is clearer than the surrounding state.
- Keep actor context visible so Local Operator, Local Reviewer, and Local Manager each land on a different primary workflow and see different navigation emphasis.
- Preserve the application service layer as the source of workflow behavior.
- Keep risk, freshness, approval, and audit signals visible without letting governance chrome dominate the primary workflow.
- Support governed POST workflows for object creation, revision authoring, review submission, reviewer assignment, approval, rejection, supersession, suspect marking, and validation-run recording.

This change does not rework repository schemas, canonical source layout, or the underlying governance workflow model.

## Technical Approach

- `papyrus.interfaces.web` is now a package rather than a monolithic module.
- WSGI request parsing, route matching, template rendering, and static asset serving are separated into dedicated modules.
- Route handlers stay thin:
  - read request state
  - call application queries or commands
  - pass structured results into presenters
  - render server-side HTML
- Governed meaning is carried through backend contracts:
  - `ui_projection` for object and revision posture
  - workflow projections for draft and ingest readiness
  - action descriptors for governed actions
  - acknowledgement and operator-message payloads for governed mutations
- Templates and routes should not derive governed action availability or acknowledgement rules from raw state fields.
- The shared shell renderer now consumes actor-scoped role configuration for:
  - role landing route
  - deduplicated navigation
  - persistent actor indicator near the page title
  - role switch target path
- The shared shell supports a focus variant for active write work so authoring screens can hide both side rails by default.
- Templates live under `src/papyrus/interfaces/web/templates/` and are organized into:
  - shared shell layout
  - reusable partial components
  - page templates
- CSS is split into tokens, layout, components, and page-level rules under `src/papyrus/interfaces/web/static/css/`.
- The operator UI color system is governed through semantic tokens rather than component-level hex values:
  - `7659 C` (`--color-brand-hero`) carries identity and intent. It drives primary actions, active navigation, object identity, focus rings, and command-highlight tokens.
  - `7658 C` (`--color-brand-depth`) is reserved for authority and depth. It is used for stronger hover and pressed states, denser emphasis surfaces, and stronger labels inside governance-heavy panels.
  - `7660 C` (`--color-brand-context`) carries context and grouping. It is used through contextual tint tokens for selected fills, secondary hover states, governance panel backgrounds, filter chips, and timeline rails.
  - Status colors remain separate from the brand family so success, warning, error, and informational states do not read as product-brand signals.
- Component mapping follows the semantic layer:
  - primary buttons, active navigation, object identity strips, and key count chips use hero tokens
  - hero hover and pressed states use depth tokens
  - secondary buttons, selected rows, metadata and citation panels, and grouped picker states use contextual tokens while keeping most surfaces neutral
- Minimal progressive enhancement lives in `src/papyrus/interfaces/web/static/js/` for search filtering, disclosure hooks, and path/id suggestions in forms.

## Dependencies Introduced Or Modified

- No new third-party Python dependencies were introduced.
- The refactor continues to use the existing standard-library WSGI stack and repository taxonomies.
- The JSON API was extended to expose thin write/manage endpoints aligned to existing application commands.
- Queue, dashboard, object detail, and review detail now share backend projection-backed posture summaries so approval and trust do not blur together.
- Read and health decision surfaces now group guidance by urgency and use the same risk, freshness, and approval badge vocabulary.

## Tradeoffs And Known Limitations

- Draft objects and draft revisions remain runtime-governed records; the UI does not write canonical Markdown source files.
- Revision history is comparison-friendly, but it does not yet implement a true side-by-side diff view.
- The interface is still intended for local or otherwise trusted operator environments; it does not introduce an authentication or CSRF layer.
- Form structure is typed and guided. Guided section editing is the primary revision path.
- The separate bulk draft fallback route is retained technical debt because it still carries the search-backed citation picker and searchable multi-select helpers that have not yet moved into shared guided components.
- Weak-evidence warnings on write and submit screens now distinguish between governed local Papyrus references and external/manual evidence, and point operators to the manage-side evidence follow-up flow when capture metadata is still required.

## Operational Notes

- The old inline-rendering `src/papyrus/interfaces/web.py` implementation was removed.
- The compatibility import path remains the same: `papyrus.interfaces.web`.
- Changing the role selector in the topbar now switches immediately to the selected role's primary page instead of requiring a second submit button or keeping every role on the same queue view.
- If the current page contains unsaved governed form changes, the role switch asks for confirmation before discarding them.
- Seeded runtime content is implicit in the local runtime and does not appear as a separate selectable role in the shell.
- The shared shell keeps the underlying routes intact, but the visible navigation differs by role:
  - Local Operator: queue, services, and authoring entry points
  - Local Reviewer: review queue, trust dashboard, validation, and audit
  - Local Manager: trust dashboard, review oversight, audit, and validation
- Read surfaces preserve queue, object detail, revision history, service detail, dashboard, and impact coverage while improving decision visibility.
- Shell-only objects created through the write flow remain discoverable in `/queue` before their first revision exists. Queue hits for those shells route back into `/write/objects/{object_id}/revisions/new#revision-form`, and write screens keep the current stage visible through the progress sidebar during object creation, revision drafting, and review submission.
- Write screens use the focus shell, one active editor at a time, a single progress sidebar, and inline or end-of-step validation instead of persistent governance rails.
- Queue and health screens now replace wide status tables with grouped decision cards ordered by `Requires attention`, `Needs review`, and `Safe`.
- Object detail now uses the same risk, freshness, and approval badges as queue and health surfaces, with lifecycle state moved into reference metadata.
- The guided revision route remains the primary write path. `/write/objects/{object_id}/revisions/fallback` is a retained transitional route for citation lookup and searchable multi-select controls, not a second place to define lifecycle or acknowledgement meaning.
- Invalid object-shell creation attempts now render a warning flash and blocking validation summary at the top of the page so missing or malformed required fields are visible without hunting through the full form.
- Invalid revision saves now post back to the clean revision URL instead of preserving the original shell-created success notice, and the page renders a top-of-form blocking validation summary so operators can see why the draft was not saved.
- Write and manage flows now use redirect-after-post patterns so operator actions are explicit and inspectable.
- Governed manage routes now capture rationale for rejection, supersession, and suspect posture rather than silently mutating runtime state.
