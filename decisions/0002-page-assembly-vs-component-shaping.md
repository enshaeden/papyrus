# Separation of Page Assembly and Component Shaping

Status: Accepted

## Context

Papyrus page files had begun to perform too many responsibilities at once. They were deciding which components appeared, in what order they appeared, and also shaping component-specific content structures, labels, display fields, and conditional presentation details. This created broad page-level files that were difficult to reason about and easy to destabilise.

The result was a system where component behaviour was hidden inside page read models and assembly logic rather than owned close to the component itself. This weakened reuse, increased coupling, and made UI behaviour difficult to inspect or change without touching unrelated page logic.

Papyrus requires a cleaner separation between page composition and component-level presentation shaping.

## Options Considered

- Keep page read models responsible for both ordering and detailed display shaping
- Move all shaping into shared global view-model helpers
- Separate page assembly from component-specific shaping responsibilities
- Let each team or feature choose its own shaping boundary case by case

## Decision

Page-level code may decide which components appear and in what order. It may also provide coarse-grained data required for composition. Component-specific copy, item structures, display fields, and presentation shaping must be owned in component-local code or in narrowly scoped component-specific view models.

Page assembly answers: what appears here, and in what sequence.  
Component shaping answers: how this surface expresses its content.

Broad page read models must not bury component-specific display logic.

## Consequences

### This enables

- Thinner page files with clearer orchestration responsibilities
- Stronger local reasoning within component boundaries
- Easier refactoring of one surface without destabilising page composition
- Better alignment between data contract and rendered output
- Reduced leakage of UX decisions into broad page models

### This restricts

- Page read models cannot become catch-all transformation layers
- Component-specific content structures cannot be buried in generic page helpers
- Presentation details cannot be silently shaped far from the rendering surface
- Shared read-model utilities cannot become undocumented UI policy engines

### This now requires

- Page files to remain thin and composition-focused
- Component-specific view models to be introduced where shaping is non-trivial
- Existing page-level shaping logic to be extracted into local component boundaries
- Reviews to distinguish clearly between orchestration logic and presentation logic
- New components to define their own field contracts close to where they render