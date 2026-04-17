# Web UI Component Contracts

Scope: Visible component ownership, page assembly, presentation shaping, local deletion, traceability, de-duplication, and UI refactor reporting

## Purpose

This record is the canonical authority for structuring visible Papyrus web surfaces.

Use it when:

- adding or refactoring visible UI
- changing presenter or template boundaries
- changing read-model inputs for visible surfaces
- changing role-conditioned controls, panels, or visible composition on shared surfaces
- removing duplicated navigation, controls, or status treatments
- removing visible UI safely

This record governs visible component ownership within the shared Papyrus shell and shared route model.
It does not create separate component architecture by role.

## Core rules

- Each major visible UI surface must have one obvious owner.
- Page files are assemblers only.
- Read models provide coarse data, visibility-relevant facts, and ordering. They do not encode local UI structure.
- Remove duplicated navigation, controls, and status treatments at the source boundary that generates them.
- Shared abstractions may not hide ownership or make removal harder.
- Role-conditioned visibility does not justify splitting one canonical surface into unclear or overlapping owners.

## One visible component = one owner

Every major visible UI surface must have a single obvious owner file.

That owner is responsible for:

- render logic for the surface
- field contract for the surface
- optional local substructure required to present the surface
- role-conditioned rendering within that surface when applicable
- a unique and stable `data-component`
- traceable style ownership
- focused test coverage

A developer inspecting a visible surface in the browser must be able to search its `data-component` and land directly in the owner file without ambiguity.

Reviews must reject changes where visible ownership is unclear.

## Page files are assemblers only

Page-level presenter and template files may:

- decide which components appear
- decide in what order they appear
- decide which role-visible components, panels, and action zones are present on a shared route
- pass coarse-grained data required for composition

Page-level files must not:

- define detailed internal markup for component substructure
- render nested lists, rows, badges, buttons, or internal scaffolding that belongs to a component
- carry copy for sub-elements that belong to a component
- take over local shaping merely because a route serves multiple roles

Page assembly answers: what appears here, and in what sequence.
Component shaping answers: how this surface expresses its content.

## Read models do not shape UI structure

Read models may decide which components appear and what data they need.

Read models must not:

- define UI-specific structures such as cards, rows, tiles, lists, or launch items
- construct nested UI objects whose only purpose is presentation
- carry copy tied only to a local visual treatment
- become catch-all transformation layers for component-specific display policy
- pre-bake separate Reader, Operator, or Admin UI structures for the same canonical surface

If removing a paragraph, badge, list, button, or role-conditioned control cluster requires editing a broad read model, the architecture is wrong unless that content is true domain data.

## Component-local rendering and traceability

All markup for a component must live in its owner.

If a component contains headers, summaries, item rows, badges, buttons, supporting metadata, or role-conditioned controls, that structure must be rendered inside the owner component instead of being split across page files, helper utilities, shared layout wrappers, or generic rendering maps.

Styles must remain traceable by component.
Tests must mirror component ownership closely enough that a developer can identify impacted coverage immediately.

The system must be built so a developer can remove a visible UI element by editing its owner and its directly associated styles and tests.

## Remove duplicated navigation and controls at the source

Remove duplicated navigation, duplicated filters, duplicated action bars, duplicated contextual actions, duplicated status summaries, and duplicated kicker-plus-heading label stacks at the shell, shared route, surface, or layout boundary that generates them.

Page-level hiding or cosmetic patching is not a valid fix when duplication originates from shared structure.

Any deliberate duplicate affordance requires explicit justification and a clear explanation of how confusion is prevented.

## Avoid abstraction that hides ownership

Do not introduce broader generic UI layers merely to reduce repetition.

Do not solve ownership problems with:

- generic card frameworks
- centralised UI schema registries
- shared render helpers that obscure ownership
- reusable dashboard abstractions that make deletion harder
- role-specific wrapper layers that duplicate canonical surface ownership without a materially different surface purpose

Clarity, traceability, and safe removal take priority over abstraction density.

## Shared surfaces and role-conditioned composition

When the same canonical route or surface is visible to multiple roles, prefer one canonical component owner with role-conditioned composition inside that surface.

Create separate component owners only when the visible surface is materially different in purpose, not merely because a more privileged role can see more controls, metadata, or panels.

Hidden controls and hidden sub-surfaces must be absent at the owning boundary, not cosmetically suppressed downstream.

## Supporting explanatory copy is exceptional

Do not add explanatory paragraph copy to visible UI containers by default.

On Papyrus web surfaces:

- do not place explanatory paragraph copy beneath headings by default
- do not add helper blurbs under mode cards, context cards, navigation blocks, dashboard blocks, or empty states unless omission would create user error
- prefer terse headings, explicit state, and actionable controls over descriptive supporting prose
- preserve supporting prose only when it is task-critical, state-critical, safety-critical, compliance-critical, or necessary to prevent user error
- remove explanatory copy at the owning presenter, component, template, shell, shared surface, or shared renderer boundary instead of hiding it downstream

If a visible paragraph can be removed without reducing task comprehension, it does not meet the bar and must not ship.

## Required reporting for UI refactors

For each new or materially refactored visible component, report:

- component name
- `data-component`
- owner file
- upstream data source
- CSS location
- test location

If the component includes role-conditioned composition, also report:

- minimum visible role for the route or surface
- any role-conditioned child controls, panels, or sections owned by that component

If this ownership map is unclear, the refactor is incomplete.