# Operator Web UI

This reference records the stable server-rendered UI contract for Papyrus. It is for maintainers working on the web surface, not for operator step-by-step execution.

## Purpose

- The web UI is a thin operator surface over shared application services.
- Route handlers read request state, call application queries or commands, and hand structured data to presenters.
- Presenters and templates own page layout, surface composition, and reusable components.
- Routes should not emit HTML fragments or re-derive governed meaning from raw state fields.

## Shared UI Contract

- The shared component canon is:
  - one shared surface partial with two roles:
    - flat `content-section` for primary reading and composition
    - bordered `context-panel` for right-rail metadata and operational context only
  - one summary strip
  - badges
  - decision cells and decision cards
  - tables
  - filter bars
  - action bars
  - empty states
  - metadata lists
  - form field controls
- Primary content should read through text, spacing, and dividers rather than stacked cards or softened panels.
- Non-critical surfaces should not carry visible containment. Backgrounds, borders, and radius are reserved for right-rail context panels, selected table rows, and explicit warning or error states.
- Governed, status, audit, citation, relationship, validation, and support surfaces should be flattened unless they are serving one of those explicitly contained roles.
- Projection-backed posture remains the source of UI meaning:
  - `ui_projection.state`
  - `ui_projection.use_guidance`
  - action descriptors
  - workflow projections
  - acknowledgement payloads
- Templates may present those contracts differently by surface, but should not recreate policy rules or fallback copy from raw lifecycle aliases.

## Stable HTML Hooks

Critical HTML must expose semantic hooks that survive copy edits and page simplification.

- `data-surface` identifies the page or panel work area.
- `data-component` identifies reusable UI primitives such as surface panels, summary strips, tables, badges, decision cards, and form fields.
- `data-action-id` identifies governed actions and other critical affordances.

Tests should assert those hooks plus structured contract payload behavior instead of exact headings, counts, or prose.

## Shell And Layout Rules

- Shell variants are explicit:
  - `normal` for navigation and browsing surfaces
  - `focus` for intentionally reduced-navigation work, not guided drafting
  - `minimal` for one-step decisions and system pages
- Guided drafting uses the `normal` shell. Sidebar navigation and topbar actor controls remain visible while the operator works through guided sections.
- The right rail is optional and should render only when the page has actionable contextual support.
- The sidebar is a flat grouped list, not a stack of card containers.
- The left rail and topbar actor controls come from actor shell configuration, not page-local duplication.
- Actor identity renders through the topbar control on normal-shell pages. There is no separate page-header actor banner contract.
- Page headers are opt-in and should include only the elements the presenter asks for.
- Page-local actor, status, and action affordances should not render as chips, pills, or soft cards; they should read as text with restrained accent cues.
- Density scales by role:
  - end-user surfaces stay lowest density
  - operator surfaces stay medium density
  - reviewer and manager governance surfaces use denser tables and selected-item context rails
- Reviewer and manager governance screens should prefer table-first layouts with deterministic URL-driven selection state in the right rail.

## Web Authoring Route Contract

- `POST /write/objects/{object_id}/revisions/start` is the explicit guided authoring start route. It may reuse a compatible draft or create a new one through application-owned policy.
- `GET /write/objects/{object_id}/revisions/new` is load-only:
  - with `revision_id`, it loads that revision context only
  - without `revision_id`, it may load only an existing compatible draft
  - if no compatible draft exists, it returns `400 Bad Request` with an operator-facing reason and does not redirect implicitly
- `/write/objects/new` creates the object shell and eagerly starts the first draft before redirecting to the guided page with a concrete `revision_id`.
- Presenters should link to an existing guided revision only when they already have a concrete `revision_id`. When a draft may need to be created or reused, presenters should use the explicit POST start route instead of GET-side effects.

## Current Boundaries

- The main remaining route-level UI outliers were moved into presenters during Phase 2, including ingest and shared error pages.
- Shared components can still emit low-level markup fragments, but page composition should stay in presenters and templates.
- No authentication or CSRF layer is introduced in this interface; the surface remains intended for local or otherwise trusted operator environments.

## Testing And Maintenance

- Prefer presenter tests and WSGI surface tests over copy-pinned HTML assertions.
- When a new top-level UI pattern is needed, extend the shared component canon instead of introducing page-local primitives.
- When a page needs different grouping or emphasis, change presenter composition first and only add a new partial when the pattern is reusable across surfaces.
