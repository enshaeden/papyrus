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
  - a single role-prioritized sidebar navigation section
  - role switch target path
- The shared shell supports three variants:
  - `normal` for navigation-first work with optional rails
  - `focus` for active drafting with no shell rails
  - `minimal` for one-step decision screens and explicit system/error pages
- Page chrome is explicit, not implied:
  - routes pass a `page_header` object when they need headline, kicker, intro, context, detail, actions, or actor context
  - pages that do not ask for a header render no ceremonial header block
- Active actor state is available in two shell layers:
  - topbar selector for role switching
  - optional compact actor banner when the surface explicitly asks for actor context
- Actor quick links are derived from actor shell configuration so the visible action set changes with role context.
- Surface actions now favor outcome-based labels rather than route names:
  - examples include `Read guidance`, `Review queue`, `Update guidance`, `Review service impact`, and `Create draft`
  - primary actions should describe the user result, not the destination URL
- Dense data views now use decision-oriented cells instead of raw export-style rows:
  - the shared presenter layer provides decision cells with a primary fact, status badges, compact supporting text, and optional progressive disclosure
  - read, review, health, services, activity, and revision-history tables now keep the next action and risk posture in the first scan line
  - long secondary metadata remains available through disclosure instead of occupying primary columns
- The shared shell now treats the right rail as conditional layout, not permanent chrome:
  - pages that pass actionable contextual content still render the right rail
  - pages that do not pass meaningful aside content render as a two-column shell with no empty rail
- Templates live under `src/papyrus/interfaces/web/templates/` and are organized into:
  - shared shell layout
  - reusable partial components
  - page templates
- CSS is split into tokens, layout, components, and page-level rules under `src/papyrus/interfaces/web/static/css/`.
- The operator UI color system is governed through semantic tokens rather than component-level hex values:
  - `7659 C` (`--color-brand-hero`) carries identity and intent. It drives the top bar, primary actions, active navigation, object identity, focus rings, command highlights, and key count chips.
  - `7658 C` (`--color-brand-depth`) is reserved for authority and depth. It is used for stronger hover and pressed states, denser emphasis surfaces, and stronger labels inside governance-heavy panels.
  - `7660 C` (`--color-brand-context`) carries context and grouping. It is used through contextual tint tokens for selected fills, grouped secondary controls, governance and citation panels, filter chips, and timeline rails.
  - Status colors remain separate from the brand family so success, warning, error, and informational states do not read as product-brand signals.
  - Typical screen balance should remain mostly neutral:
    - `80-88%` neutral surfaces
    - `8-14%` contextual tinting
    - `3-7%` hero usage
    - `1-3%` depth usage
- Component mapping follows the semantic layer:
  - the top bar, primary buttons, active sidebar navigation, object identity strips, revision and review actions, and key count chips use hero tokens
  - hero hover and pressed states, dense admin headers, and governance-heavy labels use depth tokens
  - secondary buttons, selected rows, filter pills, metadata and citation panels, grouped picker states, and timeline rails use contextual tokens while keeping most surfaces neutral
  - secondary and grouped controls should not promote contextual tones into CTA treatment
- Minimal progressive enhancement lives in `src/papyrus/interfaces/web/static/js/` for search filtering, disclosure hooks, and path/id suggestions in forms.

## Shell Rules

- The shell must default to the widest useful working area for the current surface.
- Shell variants are explicit:
  - use `normal` for navigation and browsing surfaces
  - use `focus` for active write work
  - use `minimal` for decision forms and system/error pages
- The right rail is opt-in:
  - render it only when the surface has actionable contextual support
  - do not reserve space for empty or instructional-only sidebars
- The left rail provides one ordered navigation model per actor.
- Duplicate navigation groups are not allowed.
- Page headers are optional.
- When a page renders a header, it must only include the elements the route explicitly asked for.
- Actor summary text is opt-in, not default.

## Action Hierarchy Rules

- Every surface needs one obvious primary action.
- Primary actions must describe the outcome, not the route name.
- Use labels such as `Start drafting`, `Create draft`, `Send for review`, and `Review import`.
- Tertiary actions belong in disclosures, table row menus, or supporting panels rather than competing with the main task.

## Sidebar Usage Rules

- Sidebars exist to support action, not to explain the product.
- A sidebar is valid only when it adds one of:
  - governed status or contract needed for the current decision
  - an immediate supporting action
  - compact contextual metadata that would otherwise interrupt the main flow
- Do not use sidebars for repeated lifecycle teaching, page-definition copy, or empty placeholders.

## Copy Standards

- Use one concise, operational voice across the UI.
- Assume the user is capable and focused on getting work done.
- Prefer sequential guidance:
  - what to do now
  - what the system needs next
  - what happens after submission
- Avoid backend-facing labels in visible UI:
  - use `Reference code` instead of `Object ID`
  - use `Publishing location` instead of `Canonical path`
  - use `Related guidance` instead of `Related object IDs`
- Avoid internal implementation language such as control-plane terms, server topology, or framework boundaries unless it is truly required for a decision.
- Remove demo-looking placeholders and angle-bracket tokens from visible UI text.

## Actor-State Rules

- Actor changes must be visible without inference.
- The active actor must always be identifiable from the shared shell:
  - topbar selector
- optional compact actor banner when a surface needs page-level actor context
- The actor banner, when rendered, must show:
  - active actor name
  - role label
  - current view
  - actor-priority quick links on non-focus surfaces
- Actor-specific action emphasis must change by role through landing route, quick-link order, and dominant next actions, not only banner copy.

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
- Weak-evidence warnings on write and submit screens now distinguish between linked guidance and external/manual evidence, and point operators to the manage-side evidence follow-up flow when stronger verification details are still required.

## Operational Notes

- The old inline-rendering `src/papyrus/interfaces/web.py` implementation was removed.
- The compatibility import path remains the same: `papyrus.interfaces.web`.
- Changing the role selector in the topbar switches immediately to the selected role's landing page:
  - Local Operator: `/`
  - Local Reviewer: `/review`
  - Local Manager: `/health`
- If the current page contains unsaved governed form changes, the role switch asks for confirmation before discarding them.
- Seeded runtime content is implicit in the local runtime and does not appear as a separate selectable role in the shell.
- The shared shell keeps the underlying routes intact, but the visible navigation differs by role:
  - Local Operator: queue, services, and authoring entry points
  - Local Reviewer: review queue, trust dashboard, validation, and audit
  - Local Manager: trust dashboard, review oversight, audit, and validation
- Read surfaces preserve queue, object detail, revision history, service detail, dashboard, and impact coverage while improving decision visibility.
- Shell-only objects created through the write flow remain discoverable in `/queue` before their first revision exists. Queue hits for those shells route back into `/write/objects/{object_id}/revisions/new#revision-form`, and write screens keep the current stage visible through the progress sidebar during object creation, revision drafting, and review submission.
- Write screens use the focus shell for drafting and the minimal shell for one-step submission and decision screens.
- Queue and health screens now replace wide status tables with grouped decision cards ordered by `Requires attention`, `Needs review`, and `Safe`.
- Object detail now uses the same risk, freshness, and approval badges as queue and health surfaces, with lifecycle state moved into reference metadata.
- Actor context now propagates through the shell in two places:
  - topbar selector for changing actor
  - optional compact actor banner in pages that need page-level role context
- Duplicate left-rail navigation structures were removed. Each role now sees one ordered navigation block without a separate workflow-summary card competing for the same space.
- Home, read queue, knowledge health, and services index no longer reserve a persistent right rail for instructional filler. Those surfaces use the reclaimed width for primary work content instead.
- Repeated framing was reduced across home, read, write, import, review, health, and activity surfaces:
  - many pages now render only a title plus optional actor context rather than the old stacked header bundle
  - route-like labels such as `Open ...` were replaced with outcome language on primary actions
  - lifecycle and governance context stays visible through status panels, badges, and contracts rather than repeated explanatory prose
- Decision-heavy tables were rebalanced to improve scanability:
  - low-value metadata moved into disclosures or compact meta rows
  - risk, trust, freshness, approval, and current action now appear before archival identifiers
  - fixed table layout plus overflow handling prevents long text from collapsing action columns
- Guided revision editing now owns citation lookup and searchable multi-select controls inside the primary authoring flow.
- Invalid object-shell creation attempts now render a warning flash and blocking validation summary at the top of the page so missing or malformed required fields are visible without hunting through the full form.
- Invalid revision saves now post back to the clean revision URL instead of preserving the original shell-created success notice, and the page renders a top-of-form blocking validation summary so operators can see why the draft was not saved.
- Write and manage flows now use redirect-after-post patterns so operator actions are explicit and inspectable.
- Governed manage routes now capture rationale for rejection, supersession, and suspect posture rather than silently mutating runtime state.
