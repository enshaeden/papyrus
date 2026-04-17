# Experience Conformance Checklist

Use this checklist when reviewing Papyrus UI, navigation, route, shell, and workflow changes. Treat it as an implementation review aid; the authoritative constraints live in `decisions/`.

## Role and visibility
- Does the route belong to exactly one role-scoped experience?
- Does the page show only actions permitted for that role?
- Are unauthorised actions absent rather than disabled?
- Does search respect the same visibility rules as navigation and routes?

## Navigation and shell ownership
- Does the left navigation show only role-permitted destinations?
- Is the shell owner clear from the route group and code structure?
- Does the page avoid relying on one global nav model filtered at render time?
- Are shared primitives reused without collapsing experience boundaries?

## Layout and task fit
- Does the main area match the role’s primary task?
- Does the right rail remain contextual rather than dominant?
- Does Reader remain content-first?
- Does Operator remain work-first?
- Does Admin remain control-plane-first?

## Workflow integrity
- Does the page respect lifecycle and workflow boundaries?
- Are review, write, and publish controls shown only where the governing workflow allows them?
- Does the implementation avoid using transitional actor-shaped behaviour as product authority?

## Traceability
- Is route ownership obvious?
- Is visibility logic traceable?
- Is the source of navigation truth clear?
- Are any deviations documented in the relevant decision record?
