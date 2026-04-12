# UI Component Ownership Model

Status: Accepted

## Context

Papyrus web surfaces had become difficult to trace and maintain. Visible UI blocks were often assembled across page files, helper utilities, shared layout wrappers, and generic presentational fragments. This made routine work unnecessarily risky: a developer could inspect a visible element in the browser and still not know which file truly owned its structure, copy, styling, or tests.

This fragmentation also degraded UX quality. Surface-level fixes were being applied in multiple places instead of at the component boundary that actually generated the visible output. As a result, hierarchy drift, duplicated patterns, and inconsistent styling accumulated across the product.

Papyrus requires a UI model where visible surfaces are locally owned, easy to trace, and safe to modify or remove.

## Options Considered

- Continue using page files and shared helpers to assemble most visible structure
- Centralise more rendering in generic reusable page sections
- Assign each major visible UI surface a dedicated owner component
- Allow mixed ownership, where some surfaces are page-owned and others component-owned

## Decision

Each major visible UI surface must have one obvious owner component file. That file owns the render logic for the surface, its field contract, and any optional local substructure required to present it. Page-level files may compose owner components, but they must not own detailed structure for those components. Shared primitives may still exist for buttons, cards, layout tokens, and repeated low-level UI patterns, but they must not obscure ownership of visible product surfaces.

A developer inspecting a visible surface in the browser should be able to trace it to one primary component owner file without ambiguity.

## Consequences

### This enables

- Fast traceability from browser-inspected UI to source file
- Safer edits and removals of visible product surfaces
- Cleaner component testing boundaries
- More stable UX refactors because ownership is explicit
- Clearer alignment between markup, styles, and test coverage

### This restricts

- Page files cannot continue to accumulate embedded view structure for major surfaces
- Generic helper layers cannot act as shadow owners of UI
- Shared abstractions cannot be introduced if they blur visible ownership
- A visible component cannot have its primary structure spread across unrelated files

### This now requires

- Each major visible Home surface and equivalent major product surface must have a dedicated component owner
- Component filenames, `data-component` attributes, related CSS sections or files, and test filenames must follow a shared naming convention
- Refactors must move page-owned detailed markup into owner components
- New UI work must identify the owner component first, then implement within that boundary
- Reviews must reject changes where visible ownership is ambiguous