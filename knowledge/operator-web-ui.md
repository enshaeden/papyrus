# Operator Web UI

This reference records the stable server-rendered web UI contract for Papyrus. It is for maintainers working on the web surface, not for operator step-by-step execution.

## Purpose

- The web UI is a thin role-scoped surface over shared application services.
- Route handlers read request state, call application queries or commands, and hand structured data to presenters.
- Presenters and templates own page layout, surface composition, and reusable components.
- Routes should not emit HTML fragments or re-derive governed meaning from raw state fields.

## Shared UI Contract

- Papyrus uses one shared route space:
  - Reader reading surfaces live under `/read`
  - Operator work surfaces live under `/write`, `/import`, `/review`, and `/governance`
  - Admin control surfaces live under `/admin/overview`, `/admin/users`, `/admin/access`, `/admin/spaces`, `/admin/templates`, `/admin/schemas`, `/admin/settings`, and `/admin/audit`
- Production UI must not expose an actor switcher.
- Request-scoped role context is resolved before routing and render. It comes from runtime or authenticated identity, not from URL prefixes.
- Demo or development overlays may still map local actor IDs onto roles, but they are not part of the shipped route contract.

- The shared component canon is:
  - flat `content-section` for primary reading and composition
  - bordered `context-panel` for right-rail metadata and operational context only
  - summary strips
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
  - `focus` for intentionally reduced-navigation work
  - `minimal` for one-step decisions and system pages
- Guided drafting uses the `normal` shell.
- The global search field occupies the centered top bar slot. Identity and shell controls must not shift it off center.
- The right rail is optional and should render only when the page has actionable contextual support.
- The sidebar is a flat grouped list, not a stack of card containers.
- The left rail comes from `src/papyrus/interfaces/web/experience.py`, not page-local duplication.
- There is no production actor-selection control and no separate page-header actor banner contract.
- Page headers are opt-in and should include only the elements the presenter asks for.
- Admin control pages should prefer table-first or panel-first layouts with deterministic request-scoped role context rather than URL-driven selection state.

## Color And Tone Rules

- Papyrus uses a governed tonal family centered on Pantone 7659 C, not a single-color UI theme.
- Pantone 7659 C (`#5D3754`) is identity and intent.
- Pantone 7658 C (`#6A3460`) is authority and depth.
- Pantone 7660 C (`#9991A4`) is context and grouping.
- Semantic success, warning, error, and info colors must stay separate from the 7658/7659/7660 family.
- Neutral surfaces must dominate the screen. The purple family is reserved for orientation, context, and high-intent action.
- Avoid decorative purple gradients.

## Stable Surface Owners

- Read selection and results: `src/papyrus/interfaces/web/presenters/queue_presenter.py`
- Object detail reading surface: `src/papyrus/interfaces/web/presenters/object_presenter.py`
- Review queue and revision actions: `src/papyrus/interfaces/web/presenters/review_presenter.py`
- Activity and audit feeds: `src/papyrus/interfaces/web/presenters/activity_presenter.py`
- Import flow: `src/papyrus/interfaces/web/presenters/ingest_presenter.py`
- Admin control pages: `src/papyrus/interfaces/web/presenters/admin_presenter.py`

Every major browser-visible surface must keep a stable `data-component` owner and a local presenter or template boundary.

## Web Authoring Route Contract

- `POST /write/object/{object_id}/start` is the explicit guided authoring start route. It may reuse a compatible draft or create a new one through application-owned policy.
- `GET /write/object/{object_id}` is load-only:
  - with `revision_id`, it loads that revision context only
  - without `revision_id`, it may load only an existing compatible draft
  - if no compatible draft exists, it returns `400 Bad Request` with an operator-facing reason and does not redirect implicitly
- `/write` and `/write/new` are the canonical authoring entrypoints for the primary visible templates.
- `GET /write/citations/search` and `GET /write/objects/search` are operator-only JSON helpers for guided authoring widgets.
- Presenters should link to an existing guided revision only when they already have a concrete `revision_id`. When a draft may need to be created or reused, presenters should use the explicit POST start route instead of GET-side effects.

## Current Boundaries

- Shared routes are canonical. Role visibility changes what the current user can access on those routes.
- Reader reading surfaces stay content-first.
- Operator work surfaces stay task-first.
- Admin control surfaces stay control-plane-first.
- The JSON API remains operator-oriented and is not part of the role-scoped web route contract.
- If a screen needs governed truth that is missing, extend the backend contract or projection layer instead of adding route-local policy logic.
