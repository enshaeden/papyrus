# Actor Model To Role Model Mapping

Status: Approved
Owner: Product / Architecture
Scope: Development personas, current actor model, future role-scoped experience architecture

## Purpose
Papyrus currently uses local actor personas in development and demo flows.
Papyrus experience architecture is moving toward role-scoped product experiences: Reader, Operator, and Admin.
This record defines the relationship between the current actor model and the future role model so the repository does not carry both as competing authorities.

## Authority
The role model is the authority for future experience architecture.
The actor model is a transitional development and testing mechanism.
Actors may shape defaults such as landing path, emphasis, density, and local workflow priority in development.
Actors must not be treated as the long-term authority for production route structure, navigation architecture, or permanent experience boundaries.

## Current mapping
- `local.operator` maps to Operator
- `local.reviewer` maps to Operator with review-heavy defaults
- `local.manager` is a transitional admin-adjacent persona for development and stewardship workflows

## Rules
- Do not treat `local.reviewer` as a separate permanent product experience unless a later decision explicitly creates one.
- Do not treat `local.manager` as proof that Papyrus should have a fourth permanent experience.
- Do not justify blended shells or shared navigation architecture by pointing to current actor-based development behaviour.
- Production architecture must converge on role-scoped experiences, not actor-shaped permutations.

## Implementation note
Current actor-shaped routes and shells may remain during transition.
That transitional state does not change the target authority defined by the role-scoped experience decisions.
