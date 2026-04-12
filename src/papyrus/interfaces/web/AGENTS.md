# AGENTS.md

## Purpose

This subtree contains the Papyrus web application.

Optimise for clear information hierarchy, context-aware workflows, readable knowledge surfaces, operator efficiency, and consistency with the Papyrus content model.

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

1. information hierarchy
2. workflow clarity
3. context-specific relevance
4. readability of content surfaces
5. consistency of shared components
6. accessibility and responsive behaviour
7. visual polish

Do not preserve a visually attractive UI if it still communicates the wrong structure.

## Papyrus UX Rules

- Context switching must materially change the view, available actions, visible metadata, and navigation relevance. It must not merely reshuffle navigation chrome.
- Reader mode must read like content. Remove governance-heavy framing from reader-facing article views unless required for comprehension.
- Operator views may expose governance metadata, lifecycle controls, provenance, and structural details, but must remain legible and prioritised.
- Do not present static placeholder cards, fake counts, fake recents, fake activity, or demo-state blocks in production-facing routes unless they are explicitly marked as fixtures or development-only states.
- Avoid dashboard sprawl. Every surface must answer a clear user need.
- Prefer focused views with strong hierarchy over dense screens with many competing panels.
- Avoid mixing unrelated concerns on the same page when those concerns belong to different workflows.

## Role-Separated Web Architecture

- Maintain separate route groups and layout ownership for Reader, Operator, and Admin.
- Do not collapse role experiences into one dashboard with conditional sections.
- Left navigation must be generated from role-scoped route definitions, not filtered from a single global nav list.
- Reader object views must remain content-first.
- Operator surfaces must remain task-first.
- Admin surfaces must remain control-plane-first.
- When changing layouts, routes, or object pages, follow:
  - `docs/decisions/route-separation-and-experience-boundaries.md`
  - `docs/guides/layout-contracts-by-role.md`
  - `docs/decisions/role-experience-visibility-matrix.md`

## Navigation Rules

- Remove duplicated navigation, duplicated filters, duplicated action bars, and duplicated status summaries at the shared-component or layout level.
- Navigation must reflect user intent and current context.
- Global navigation should be stable.
- Local navigation should narrow to the current object, workflow, or role.
- Do not expose every possible control in every context.
- Use progressive disclosure when a full control set would overload the user.

## Layout and Component Rules

- Fix shared layout primitives before patching page-level symptoms.
- Fix shared components before patching route-local copies.
- Do not solve hierarchy problems by shrinking text, compressing spacing, or adding more panels.
- Preserve the existing design system, tokens, and colour schema unless the task explicitly authorises a redesign.
- Do not remove colour tokens, semantic states, or spacing rules without replacing them with a coherent alternative in the same change.
- Prefer one strong primary action per area over many equal-weight actions.
- Cards, tables, panels, and metadata blocks must have a clear reason to exist. Remove decorative or redundant containers.
- Long-form content views must use readable line length, consistent heading rhythm, and visual separation between content and metadata.

## Component Ownership and Removal Rules

Papyrus web UI must be structured for local ownership, traceability, and safe self-service removal.

### One visible component = one owner

Every major visible UI surface must have a single obvious owner file.

A component must have:

* a dedicated presenter or component file
* a unique and stable `data-component` name
* clearly traceable CSS scope, either as a dedicated file or a clearly delimited section
* a corresponding test file or clearly scoped test coverage

A developer must be able to inspect an element in the browser, search its `data-component`, and land directly in the owning file.

If this is not possible, the implementation is incorrect.

### Page files are assemblers only

Page-level presenter and template files must compose components and pass data into them.

They must not:

* define detailed internal markup for subcomponents
* render nested lists, rows, badges, buttons, or substructure for component internals
* carry copy for sub-elements that belong to a component

If a page file owns component internals, split that component out.

### Read models do not shape UI structure

Read models may decide which components appear and what data they need.

Read models must not:

* define UI-specific structures such as cards, rows, tiles, lists, or launch items
* construct nested UI objects whose only purpose is presentation
* carry copy tied only to a local visual treatment

If removing a paragraph, badge, list, or button requires editing a read model, the architecture is wrong unless that content is truly domain data.

### Component-local rendering

All markup for a component must live in its owner.

If a component contains:

* a header
* optional summary copy
* item rows
* badges
* buttons
* supporting metadata

that structure must be rendered inside the component owner, not split between page files, shared helpers, and read models.

### Component-scoped styling

Styles must be traceable by component.

Prefer:

* dedicated component CSS files, or
* clearly delimited component sections in shared CSS

Avoid:

* large page-level CSS blobs that style many unrelated structures
* selectors whose ownership is unclear from name alone

A search for a component name must quickly reveal its styles.

### Component-scoped tests

Tests must mirror component ownership.

A developer changing or deleting a component must be able to identify the impacted tests immediately.

Do not bury component expectations inside broad, multi-surface presenter tests when focused tests are practical.

### Deletion must be local

The system must be built so a developer can remove a UI element by editing its component owner and its directly associated styles and tests.

If deletion routinely requires touching:

* page assemblers
* broad read models
* unrelated helper utilities
* generic rendering maps

then the structure is too coupled and must be simplified.

### Avoid abstraction that hides ownership

Do not introduce broader generic UI layers merely to reduce repetition.

Do not solve this with:

* generic card frameworks
* centralised UI schema registries
* shared render helpers that obscure which file owns a surface
* reusable launch/dashboard abstractions that make deletion harder

Prefer explicit component files over abstraction density.

Clarity, traceability, and removability take priority over reuse.

### Required reporting for UI refactors

For each new or refactored visible component, report:

* component name
* `data-component`
* owner file
* upstream data source
* CSS location
* test location

If this ownership map is unclear, the refactor is incomplete.


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

- dev: `python3 scripts/serve_web.py --db build/knowledge.db --source-root .`
- lint: `not separately configured; do not claim lint coverage until a dedicated lint command exists`
- typecheck: `not separately configured; do not claim typecheck coverage until a dedicated typecheck command exists`
- test: `python3 -m unittest tests.test_web_presenters tests.test_web_operator_ui tests.test_web_semantic_hook_contract tests.interfaces.test_web_routing tests.interfaces.test_web_import_smoke tests.test_interface_surfaces tests.test_surface_conformance tests.test_operator_readiness`
- build: `./scripts/build_static_export.sh`

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
