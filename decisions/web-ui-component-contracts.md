# Web UI Component Contracts

Status: Approved
Owner: Front-end Architecture
Scope: Visible component ownership, page assembly, presentation shaping, local deletion, traceability, de-duplication, and UI refactor reporting

## Purpose

This record is the canonical authority for structuring visible Papyrus web surfaces.

Use it when:

- adding or refactoring visible UI
- changing presenter or template boundaries
- changing read-model inputs for visible surfaces
- removing duplicated navigation, controls, or status treatments
- removing visible UI safely

## Core rules

- Each major visible UI surface must have one obvious owner.
- Page files are assemblers only.
- Read models provide coarse data and ordering. They do not encode local UI structure.
- Remove duplicated navigation, controls, and status treatments at the source boundary that generates them.
- Shared abstractions may not hide ownership or make removal harder.

## One visible component = one owner

Every major visible UI surface must have a single obvious owner file.

That owner is responsible for:

- render logic for the surface
- field contract for the surface
- optional local substructure required to present the surface
- a unique and stable `data-component`
- traceable style ownership
- focused test coverage

A developer inspecting a visible surface in the browser must be able to search its `data-component` and land directly in the owner file without ambiguity.

Reviews must reject changes where visible ownership is unclear.

## Page files are assemblers only

Page-level presenter and template files may:

- decide which components appear
- decide in what order they appear
- pass coarse-grained data required for composition

Page-level files must not:

- define detailed internal markup for component substructure
- render nested lists, rows, badges, buttons, or internal scaffolding that belongs to a component
- carry copy for sub-elements that belong to a component

Page assembly answers: what appears here, and in what sequence.
Component shaping answers: how this surface expresses its content.

## Read models do not shape UI structure

Read models may decide which components appear and what data they need.

Read models must not:

- define UI-specific structures such as cards, rows, tiles, lists, or launch items
- construct nested UI objects whose only purpose is presentation
- carry copy tied only to a local visual treatment
- become catch-all transformation layers for component-specific display policy

If removing a paragraph, badge, list, or button requires editing a broad read model, the architecture is wrong unless that content is true domain data.

## Component-local rendering and traceability

All markup for a component must live in its owner.

If a component contains headers, summaries, item rows, badges, buttons, or supporting metadata, that structure must be rendered inside the owner component instead of being split across page files, helper utilities, shared layout wrappers, or generic rendering maps.

Styles must remain traceable by component.
Tests must mirror component ownership closely enough that a developer can identify impacted coverage immediately.

The system must be built so a developer can remove a visible UI element by editing its owner and its directly associated styles and tests.

## Remove duplicated navigation and controls at the source

Remove duplicated navigation, duplicated filters, duplicated action bars, duplicated contextual actions, duplicated status summaries, and duplicated kicker-plus-heading label stacks at the source component, shell, or layout boundary that generates them.

Page-level hiding or cosmetic patching is not a valid fix when duplication originates from shared structure.

Any deliberate duplicate affordance requires explicit justification and a clear explanation of how confusion is prevented.

## Avoid abstraction that hides ownership

Do not introduce broader generic UI layers merely to reduce repetition.

Do not solve ownership problems with:

- generic card frameworks
- centralised UI schema registries
- shared render helpers that obscure ownership
- reusable dashboard abstractions that make deletion harder

Clarity, traceability, and safe removal take priority over abstraction density.

## Required reporting for UI refactors

For each new or materially refactored visible component, report:

- component name
- `data-component`
- owner file
- upstream data source
- CSS location
- test location

If this ownership map is unclear, the refactor is incomplete.
