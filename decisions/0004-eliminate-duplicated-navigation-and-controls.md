# Eliminate Duplicated Navigation and Controls at the Source

Status: Accepted

## Context

Papyrus UI surfaces had accumulated repeated navigation blocks, repeated status treatments, overlapping controls, and duplicated contextual actions across pages and modes. In several places, the same choice was being represented in more than one region of the screen. This made the product feel cluttered, lowered signal-to-noise ratio, and obscured the true primary action for a given workflow.

Prior attempts to improve these surfaces often patched individual pages instead of resolving duplication at the shared primitive, layout, or ownership boundary where it originated. This produced temporary visual relief without removing the underlying cause.

Papyrus requires a discipline of removing duplicated navigation and controls at the source component or layout boundary that creates them.

## Options Considered

- Tolerate some duplication as a trade-off for discoverability
- Hide duplicated elements visually while keeping underlying structure intact
- Remove duplicated navigation and controls at the source component and layout level
- Leave existing duplication in place and focus only on styling refinements

## Decision

Duplicated navigation, repeated controls, and repeated status blocks must be removed at the source. Shared layout primitives, shell components, navigation systems, and owner components must be corrected so that each decision, control, and status expression appears once in its proper context unless there is a deliberate and justified exception.

Page-level patching is not considered a valid fix when duplication originates from shared structure. UX improvements must attack the generating source, not merely mask symptoms downstream.

## Consequences

### This enables

- Clearer information hierarchy
- Stronger emphasis on the real primary action in each workflow
- More predictable page composition
- Reduced visual noise and lower cognitive load
- More consistent behaviour across contexts and modes

### This restricts

- Teams cannot solve duplication by hiding one copy locally while leaving the source intact
- Shared shells and layout wrappers cannot accumulate overlapping controls
- A surface cannot repeat state or action affordances without explicit justification
- Styling-only fixes cannot be called UX resolution when hierarchy failure remains

### This now requires

- Audits of shared layout primitives and shell components before page-level patching
- Identification of the true source of duplicate navigation, controls, and status blocks
- Removal or consolidation at the component, shell, or layout boundary that generates duplication
- UX reviews to verify singular ownership of each major control surface
- Any justified duplicate affordance to document why duplication is necessary and how confusion is prevented