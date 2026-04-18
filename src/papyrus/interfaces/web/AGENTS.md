# AGENTS.md

## Purpose

This subtree contains the Papyrus web application.

Optimise for premium governed product quality, clear information hierarchy, context-aware workflows, readable knowledge surfaces, operator efficiency, and consistency with the Papyrus content model.

This is not a generic dashboard.
This is not a generic CMS.
This is not a generic text editor.

The UI must reflect the system’s actual structure:
- knowledge objects
- entries within those objects
- lifecycle and governance state
- ingestion and transformation workflows
- reader-facing versus operator-facing views

## Web Priorities

When making trade-offs, prioritise in this order:

1. governance clarity and route/access correctness
2. information hierarchy
3. workflow clarity
4. readability of content surfaces
5. quality of shared shell and shared primitives
6. accessibility and responsive behaviour
7. visual polish

Do not preserve a visually attractive UI if it still communicates the wrong structure.

## Papyrus UX Rules

- Context switching must materially change the view, available actions, visible metadata, and navigation relevance. It must not merely reshuffle navigation chrome.
- Reader mode must read like authored content. Remove governance-heavy framing from reader-facing article views unless required for comprehension.
- Operator views may expose governance metadata, lifecycle controls, provenance, and structural details, but must remain legible and prioritised.
- Papyrus is premium governed knowledge platform. Shell quality is trust signal, not cosmetic garnish.
- Shared primitives must feel intentional and durable. Premium visual treatment is allowed when route/access discipline, governance clarity, and usability remain intact.
- Do not present static placeholder cards, fake counts, fake recents, fake activity, or demo-state blocks in production-facing routes unless they are explicitly marked as fixtures or development-only states.
- Avoid dashboard sprawl. Every surface must answer a clear user need.
- Prefer focused views with strong hierarchy over dense screens with many competing panels.
- Avoid mixing unrelated concerns on the same page when those concerns belong to different workflows.

## Shared-Route Web Architecture

- When changing layouts, routes, or object pages, follow:
  - `decisions/role-scoped-experience-architecture.md`
  - `decisions/runtime-role-context-and-access-resolution.md`
  - `decisions/layout-contracts.md`
  - `decisions/knowledge-workflows-and-lifecycle.md`
  - `decisions/web-ui-component-contracts.md`
- Maintain one shared production shell and one canonical shared route space with explicit role-conditioned visibility rules.
- Request-scoped role and access context must come from runtime or authenticated identity, not URL namespaces.
- Route guards, deep links, navigation, search, and related discovery must enforce that context fail closed.
- Left navigation must be generated from the canonical shared route set plus resolved visibility.
- Reader object views must remain content-first.
- Operator surfaces must remain task-first.
- Admin surfaces must remain control-plane-first.

## Forbidden Web Patterns

Reject changes that:
- add role authority through path prefixes, query parameters, or template-local branching
- expose unauthorised actions as disabled instead of absent
- preserve duplicate route trees for the same canonical work
- imply separate production shells for permanent role experiences
- add page-local policy logic that should live in backend contracts
- reintroduce dashboard-style mixed panels into Reader surfaces
- add placeholder production content to fill empty states

## Required Architecture Evidence

For any route, shell, navigation, or role-related UI change, report:
- canonical route family touched
- shell owner
- role visibility impact
- navigation source of truth
- whether any shared component contract changed

## Navigation Rules

- Remove duplicated navigation, duplicated filters, duplicated action bars, and duplicated status summaries at the generating component or layout boundary defined in `decisions/web-ui-component-contracts.md`.
- Navigation must reflect user intent and current context.
- Global navigation should be stable.
- Local navigation should narrow to the current object, workflow, and resolved access context.
- Do not expose every possible control in every context.
- Use progressive disclosure when a full control set would overload the user.

## Layout and Component Rules

- Fix shared layout primitives before patching page-level symptoms.
- Fix shared components before patching route-local copies.
- Do not solve hierarchy problems by shrinking text, compressing spacing, or adding more panels.
- Preserve the canonical shared shell and route/access architecture when redesigning.
- Premium visual redesign is allowed. Keep Papyrus hero colour as sole legacy brand anchor when redesign scope calls for palette replacement.
- Do not remove colour tokens, semantic states, or spacing rules without replacing them with a coherent alternative in the same change.
- Prefer one strong primary action per area over many equal-weight actions.
- Cards, tables, panels, and metadata blocks must have a clear reason to exist. Remove decorative or redundant containers.
- Landing surfaces, section headers, navigation chrome, mode cards, context cards, dashboard blocks, empty states, and similar top-level UI containers must not include explanatory paragraph copy beneath headings by default.
- Supporting prose is allowed only when it is task-critical, state-critical, safety-critical, or necessary to prevent user error.
- Prefer terse headings plus actionable controls over descriptive blurbs.
- If a visible paragraph can be removed without loss of task comprehension, it should not exist.
- Do not stack a kicker, eyebrow, or overline above a heading when both labels resolve to the same visible text. Collapse the duplicate label at the owning component or presenter boundary.
- Long-form content views must use readable line length, consistent heading rhythm, and visual separation between content and metadata.
- Premium dark surfaces, elevated rails, and glass-like shell treatments are acceptable when content remains dominant and decorative noise stays low.

## Component Ownership and Removal Rules

Follow `decisions/web-ui-component-contracts.md` for visible component ownership, page assembly boundaries, read-model limits, local deletion, and UI refactor reporting.

In this subtree:

- every major visible surface still needs a stable `data-component`
- ownership of markup, styles, and tests must stay locally traceable
- do not introduce generic render helpers or card frameworks that hide ownership


## Content Surface Rules

- Knowledge pages must clearly distinguish:
  - title and identity
  - primary content
  - supporting metadata
  - lifecycle or governance state
  - related actions
- The primary content must dominate the reading surface.
- Governance metadata must not overwhelm the content in reader-facing views.
- Do not render raw structure, internal fields, or schema-oriented terminology in end-user reading flows unless the design explicitly calls for it.
- When showing entries within a knowledge object, make the relationship clear and navigable.
- When showing partial content by role or context, ensure the view feels intentionally filtered, not arbitrarily incomplete.


## Authoring and Workflow Rules

- Papyrus authoring should feel structured and guided, not like an unbounded blank editor unless the route explicitly supports raw editing.
- Template-driven flows must feel sequential and self-explanatory.
- Ingestion, validation, transformation, and publishing flows must show progress state, error state, and next action clearly.
- Surface validation errors early, close to the problem, and in plain language.
- Do not bury failure states in console-only or toast-only feedback when the workflow itself is blocked.

## State and Data Rules

- Prefer real data paths over mocked values in production routes.
- If a route depends on data not yet implemented, show an honest, minimal empty state or pending state rather than a fabricated dashboard.
- Empty states must direct the user toward the next meaningful action.
- Loading states must preserve layout stability.
- Error states must explain what failed, what the user can do next, and whether data integrity is affected.

## Accessibility and Responsiveness

- Maintain keyboard accessibility for navigation, menus, dialogs, and content controls.
- Preserve visible focus states.
- Ensure text wraps or scales appropriately within buttons, tabs, and selectable controls.
- Do not allow truncation, clipping, or overflow to hide critical meaning.
- Verify desktop and mobile breakpoints for any shared layout or navigation change.
- Prefer responsive reflow over cramming more content into fixed containers.

## Documentation Drift Rules

When changing routes, components, UI flows, labels, or screenshots:
- update the affected docs in the same task when practical
- remove stale claims and stale screenshots
- verify route names, labels, and interaction descriptions against implementation

Do not let the docs describe a cleaner UI than the one that actually ships.

## Working Rules
* When refactoring UI, prefer component extraction over adding more helper indirection.
* When a visible element is hard to trace or hard to remove, stop and simplify ownership before changing copy or styling.
* Do not leave component internals split across page presenters, read models, and CSS blobs when they can be localised to one owner.
* For browser-visible surfaces, `data-component` names, owner files, CSS scope, and tests should align in naming where practical.

- Make the smallest correct structural change that resolves the issue at the source.
- Do not use CSS overrides as a substitute for fixing the underlying component contract.
- Do not create route-specific hacks for problems caused by shared layouts or shared components.
- When a route looks wrong, inspect the layout shell, shared navigation, shared panels, and shared typography primitives first.
- When changing visual hierarchy, verify the result against the user’s primary task on that screen.
- Do not claim a UX improvement if the page still feels cluttered, duplicative, static, or context-insensitive.

## Verification

This web surface ships through the Python application and WSGI entrypoints in `scripts/serve_web.py` and `scripts/run.py --operator`.
Use `decisions/experience-conformance-checklist.md` as a review checklist when reviewing route, shell, role-visibility, and workflow-surface changes. The authoritative constraints live under `decisions/`.

- dev: `python3 scripts/serve_web.py --db build/knowledge.db --source-root /path/to/workspace`
- format: `./scripts/format.sh`
- lint: `./scripts/lint.sh`
- typecheck: `./scripts/typecheck.sh`
- test: `python3 -m unittest tests.test_web_presenters tests.test_web_operator_ui tests.test_web_semantic_hook_contract tests.interfaces.test_web_routing tests.interfaces.test_web_import_smoke tests.test_interface_surfaces tests.test_surface_conformance tests.test_operator_readiness`
- build: `./scripts/build.sh`
- route map: `python3 scripts/build_route_map.py`

For UI work, completion requires all applicable checks plus direct verification of the affected routes and states.

Minimum bar:

* relevant tests pass
* build succeeds
* affected routes render without obvious regressions
* desktop and mobile breakpoints checked for changed views
* loading, empty, and error states checked when touched
* docs updated if labels, flows, screenshots, or route behaviour changed
* for UI architecture work, the ownership map for affected components is reported explicitly


## Reporting Format

At the end of each task, report in this order:

1. routes and flows changed
2. shared components or layout primitives changed
3. lint, typecheck, test, and build results
4. manual validation performed
5. unresolved UX debt or follow-up work

Do not state that the UI is fixed unless this evidence is present.

## Planning Trigger

Create a written plan before editing when the task:

- changes shared navigation
- changes layout shells or route wrappers
- changes design-system primitives or tokens
- changes reader mode or object-view hierarchy
- affects multiple major routes
- rewires context switching behaviour
- introduces a new workflow for ingestion, validation, publishing, or authoring
