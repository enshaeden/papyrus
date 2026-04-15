# Remove Non-Essential Explanatory UI Copy

Status: Approved
Owner: Front-end Architecture
Scope: Visible supporting prose on Papyrus web surfaces

## Problem

Explanatory paragraph chrome has been spreading across landing surfaces, section headers, navigation chrome, mode cards, context cards, dashboard blocks, and empty states.

These blurbs weaken hierarchy, slow scanability, and make task surfaces feel more like narrated dashboards than operational views.

## Decision

Remove non-essential supporting prose from visible UI containers by default.

On Papyrus web surfaces:

- do not place explanatory paragraph copy beneath headings by default
- do not add helper blurbs under mode cards, context cards, navigation blocks, dashboard blocks, or empty states unless omission would create user error
- prefer terse headings, explicit state, and actionable controls over descriptive supporting prose
- preserve supporting prose only when it is task-critical, state-critical, safety-critical, compliance-critical, or necessary to prevent user error
- remove the copy at the owning presenter, component, template, shell, or shared renderer boundary instead of hiding it downstream

If a visible paragraph can be removed without reducing task comprehension, it does not meet the bar and must not ship.

## Consequences

- stronger scanability across Reader, Operator, and Admin surfaces
- less dashboard clutter and less descriptive chrome competing with task state
- a stricter copy bar for shared components and presenter contracts
- explicit exception review for retained warnings, trust-state messaging, destructive-action warnings, and workflow-blocking instructions
