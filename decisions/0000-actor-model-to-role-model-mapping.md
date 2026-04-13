# 0000 — Actor Model to Role Model Mapping

Status: Approved  
Owner: Product / Architecture  
Scope: Web UI, CLI, API, routing, navigation, workflow surfaces, and experience boundaries  

---

## Context

Papyrus currently uses an **actor-based model** in development and runtime surfaces.

Actors (e.g. `local.operator`, `local.reviewer`, `local.manager`) define:
- landing paths
- navigation ordering
- page emphasis
- density and layout variants
- workflow prioritisation

This actor system behaves similarly to a **presentation-layer persona system**, not a true product access model.

Separately, Papyrus is introducing **role-scoped product experiences**:

- Reader
- Operator
- Admin

These roles define:
- what a user is allowed to see
- what actions are available
- what workflows are accessible
- which routes exist at all

These two models currently overlap but are not equivalent.

---

## Problem

Without an explicit mapping:

- Actors risk becoming the de facto product architecture
- Roles risk becoming a theoretical layer not enforced in code
- Navigation, routing, and UI structure can drift into a blended system
- Contributors may justify poor boundaries using existing actor behaviour

This creates long-term structural instability.

---

## Decision

Papyrus adopts the following authority model:

### 1. Role model is authoritative

The **role model defines product architecture**.

Roles determine:
- route visibility
- navigation structure
- action availability
- workflow access
- UI surface existence

If a role does not allow something, it must not exist in the UI.

---

### 2. Actor model is transitional

The actor model is a transitional runtime mechanism used to shape UI behaviour in development and operator workflows.

It must not be treated as the authority for long-term experience architecture, which is defined by role-scoped experiences.

Actors may:
- influence defaults (landing page, emphasis, density)
- shape how a role experience feels during development
- support demo scenarios and operator workflows

Actors must not:
- define permanent route structure
- define long-term navigation architecture
- justify cross-role UI blending
- override role visibility rules

---

### 3. Mapping between current actors and roles

Current system mapping:

| Actor            | Role      | Notes |
|------------------|-----------|------|
| local.operator   | Operator  | Primary working persona |
| local.reviewer   | Operator  | Same role, review-heavy defaults |
| local.manager    | Admin-adjacent (transitional) | Not a permanent role |

Clarifications:

- `local.reviewer` is **not a separate product role**
- `local.manager` does **not justify a fourth experience**
- All three map into **existing or future role-scoped experiences**

---

### 4. Experience architecture must converge on roles

Future Papyrus UI architecture must follow:

- `/reader/*` → Reader experience
- `/operator/*` → Operator experience
- `/admin/*` → Admin experience

Actor-based variations must not:
- introduce alternate route trees
- fragment navigation ownership
- create parallel experience definitions

---

### 5. Transitional allowance

During transition:

- existing actor-shaped routes and shells may remain
- actor-based landing pages may persist
- actor-based nav ordering may continue

However:

- all new work must move toward role-scoped separation
- no new features may deepen actor-driven architecture
- no new UI should rely on actor identity for access control

---

### 6. Enforcement rules

Reject any change that:

- uses actor identity to gate access instead of role
- exposes cross-role functionality through shared shells
- preserves one global navigation model filtered at runtime
- treats actor-specific layouts as permanent product structure
- introduces new actor-specific routes instead of role-scoped routes

---

## Consequences

### Positive

- Clear separation of product architecture from development tooling
- Stronger enforcement of role-scoped UX
- Reduced long-term UI drift
- Easier reasoning about access and visibility
- Enables clean Reader / Operator / Admin separation

### Trade-offs

- Temporary duplication between actor-based and role-based structures
- Additional migration work required for routes and shells
- Need for explicit mapping during transition

---

## Implementation Notes

- Role-based routing and layout ownership must be introduced incrementally
- Actor-based shell logic may remain as a thin adaptation layer
- Eventually:
  - actor switching should be removed from production surfaces
  - role should be determined by identity and access control
- Development may continue to use actor switching for testing only

---

## Supersession

This decision supersedes any prior implicit assumption that:

- actors define product architecture
- actor-specific navigation is a valid long-term pattern
- reviewer and manager personas represent distinct product experiences

All experience architecture must now align with role-scoped separation decisions.

---

## Related Decisions

- `docs/decisions/experience-principles.md`
- `docs/decisions/role-experience-visibility-matrix.md`
- `docs/decisions/route-separation-and-experience-boundaries.md`
- `docs/decisions/knowledge-workflows-and-lifecycle.md`