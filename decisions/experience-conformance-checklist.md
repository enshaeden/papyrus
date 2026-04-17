# Experience Conformance Checklist

Use this checklist when reviewing Papyrus UI, navigation, route, shell, and workflow changes.

Treat it as an implementation review aid.
Authoritative constraints live in `decisions/`.

## Shared route and visibility conformance

- Does the route belong to the canonical shared route model rather than a role-owned duplicate?
- Does the route declare and enforce the correct minimum visible role?
- Does the request carry canonical role context from runtime or authenticated identity rather than from path shape?
- Does the page show only actions, controls, panels, and links permitted for the current role?
- Are hidden actions, controls, panels, and destinations absent rather than disabled?
- Does search respect the same visibility rules as routes, navigation, related links, and command surfaces?
- If multiple roles can access the route, does the implementation preserve one canonical surface rather than splitting it into unnecessary role-specific copies?

## Navigation and shell conformance

- Does the left navigation show only destinations visible to the current role?
- Is navigation derived from the shared route model plus visibility contracts?
- Is role context resolved before routing and render rather than inferred from a route namespace?
- Is the shell owner clear in code, without implying separate production shells by role?
- Does the implementation avoid patching visibility downstream when the true source boundary is the shell, shared surface, or route contract?
- Are shared primitives reused without obscuring ownership or creating parallel role-specific route structures?

## Layout and surface-purpose conformance

- Does the main area preserve the canonical purpose of the route or surface?
- Does the right rail remain contextual rather than dominant?
- On read surfaces, does content remain primary?
- On write surfaces, does authoring remain primary?
- On review surfaces, does triage and decision work remain primary?
- On governance or admin surfaces, do control and oversight remain primary?
- If a surface is shared across roles, does higher privilege add controls or context without distorting the surface’s core purpose?

## Workflow integrity

- Does the page respect lifecycle and workflow boundaries?
- Are write, review, governance, and admin controls shown only where the governing workflow allows them?
- Does the implementation avoid using transitional actor-shaped behaviour as product authority?
- Where the same route is visible to multiple roles, are workflow differences handled through role-conditioned composition rather than route duplication?

## Traceability

- Is route ownership obvious?
- Is component ownership obvious for each major visible surface?
- Is visibility logic traceable?
- Is the source of navigation truth clear?
- Is the source of action visibility truth clear?
- Are any deviations documented in the relevant decision record?
