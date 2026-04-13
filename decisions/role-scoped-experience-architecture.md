# Role-Scoped Experience Architecture

Status: Approved
Owner: Product / UX / Architecture
Scope: Production role model, experience separation, visibility, route groups, shell ownership, actor transition, and tonal guidance

## Purpose

This record is the canonical authority for Papyrus role-scoped experience architecture.

Use it when changing:

- production role boundaries
- route groups and route guards
- shell ownership
- search visibility
- role-specific navigation
- actor-to-role transition rules

Concrete shell composition rules live in `layout-contracts-by-role.md`.
Knowledge lifecycle and workflow state machines live in `knowledge-workflows-and-lifecycle.md`.

## Core rules

- Reader is for consumption.
- Operator is for work.
- Admin is for control.
- Hidden means absent, not merely disabled, for the current user.
- Search visibility must match route visibility.
- Global search is shell-owned and remains centered in the top bar.
- Separate route groups and shells are mandatory.
- Shared primitives are allowed. Shared blended experiences are not.
- Production role switching is forbidden.
- Context switches must materially change the information model, not only surrounding chrome.
- Transitional development personas must not define permanent production information architecture.
- The same knowledge object may reuse domain data across roles, but it must not force Reader, Operator, and Admin through one blended UI shape.

## Role model and actor transition

The role model is the authority for production experience architecture.
The actor model is a transitional development and testing mechanism.

Actors may shape local defaults such as landing path, emphasis, density, and workflow priority in development.
Actors must not be treated as authority for permanent route structure, navigation architecture, or production visibility boundaries.

### Current mapping

- `local.operator` maps to Operator.
- `local.reviewer` maps to Operator with review-heavy defaults.
- `local.manager` maps to Admin-adjacent development defaults. It does not establish a fourth production role.

### Transition rules

- Do not treat `local.reviewer` as a separate permanent product experience unless a later decision creates one.
- Do not treat `local.manager` as proof that Papyrus needs a fourth permanent experience.
- Do not justify blended shells or shared navigation architecture by pointing to actor-shaped development behaviour.
- Production architecture must converge on role-scoped experiences, not actor-shaped permutations.

## Visibility and experience matrix

| Surface / Capability | Reader | Operator | Admin | Notes |
|---|---:|---:|---:|---|
| Global search bar | Yes | Yes | Yes | Results filtered by role visibility |
| Account/system menu | Yes | Yes | Yes | Menu entries may differ by role |
| Dev-only role switcher | Dev only | Dev only | Dev only | Never in production |
| Reader browse / tree / object read | Yes | Yes in Read | Optional inspect only | Admin inspection is not the primary framing |
| Flag submission | Yes | Yes | Yes | Reader sees only the submission affordance |
| Full flag details and resolution | No | Yes if authorised | Yes | Policy-controlled |
| Operator Write workspace | No | Yes | Optional override | Admin access must be explicit |
| Review queues and assignments | No | Yes | Yes | Admin uses oversight framing, not automatic workflow inheritance |
| Templates | No | Read/use only if needed | Yes | Template administration is Admin-owned by default |
| Schemas | No | No or limited inspect | Yes | Strong admin boundary |
| Users, roles, spaces, access, settings | No | No | Yes | Admin-only |
| Audit log | No | Limited object history | Yes | Distinguish local history from full system audit |

## Explicit role boundaries

- Reader must never see Write, Review, Template, Schema, Admin, Publish, or User Management controls.
- Operator must never see User Management, Access Management, Schema Administration, or System Settings unless explicitly elevated.
- Admin owns access, schema, template, governance policy, publishing policy, and audit controls.
- Admin does not automatically inherit general writing or review workflows.
- Admin is not a catch-all for every advanced or inconvenient screen.

## Route groups

### Shared

- `/` (local entry shim redirecting to `/operator`; not a role-owned destination)

### Reader

- `/reader`
- `/reader/browse`
- `/reader/object/{object_id}`

### Operator

- `/operator`
- `/operator/read`
- `/operator/read/object/{object_id}`
- `/operator/read/object/{object_id}/revisions`
- `/operator/read/services`
- `/operator/read/services/{service_id}`
- `/operator/import`
- `/operator/import/{ingestion_id}`
- `/operator/import/{ingestion_id}/review`
- `/operator/write/new`
- `/operator/write/object/{object_id}/start`
- `/operator/write/object/{object_id}`
- `/operator/write/object/{object_id}/submit`
- `/operator/write/citations/search`
- `/operator/write/objects/search`
- `/operator/review`
- `/operator/review/governance`
- `/operator/review/activity`
- `/operator/review/impact/object/{object_id}`
- `/operator/review/impact/service/{service_id}`
- `/operator/review/object/{object_id}/{revision_id}`
- `/operator/review/object/{object_id}/{revision_id}/assign`
- `/operator/review/object/{object_id}/archive`
- `/operator/review/object/{object_id}/suspect`
- `/operator/review/object/{object_id}/supersede`
- `/operator/review/object/{object_id}/evidence/revalidate`
- `/operator/review/validation-runs`
- `/operator/review/validation-runs/new`

### Admin

- `/admin`
- `/admin/overview`
- `/admin/inspect`
- `/admin/inspect/object/{object_id}`
- `/admin/inspect/object/{object_id}/revisions`
- `/admin/services`
- `/admin/services/{service_id}`
- `/admin/governance`
- `/admin/impact/object/{object_id}`
- `/admin/impact/service/{service_id}`
- `/admin/review`
- `/admin/review/object/{object_id}/{revision_id}`
- `/admin/review/object/{object_id}/{revision_id}/assign`
- `/admin/review/object/{object_id}/archive`
- `/admin/review/object/{object_id}/suspect`
- `/admin/review/object/{object_id}/supersede`
- `/admin/review/object/{object_id}/evidence/revalidate`
- `/admin/audit`
- `/admin/validation-runs`
- `/admin/validation-runs/new`

## Route and shell rules

- Route guards must enforce role access before render.
- Navigation must derive from role-scoped route definitions, not from one global list with runtime filtering.
- Deep links must still respect role access and fail closed.
- Search results must link only to routes the current role can access.
- Production must not expose a route or client control for manual role switching.
- `/reader/*` uses the Reader shell.
- `/operator/*` uses the Operator shell.
- `/admin/*` uses the Admin shell.
- Layout files, shell files, route definitions, and tests should mirror role ownership.

## Tonal guidance

- Papyrus uses a governed tonal family centered on Pantone 7659 C, not a single-color theme.
- Pantone 7659 C (`#5D3754`) is identity and intent. Use it for primary actions, active navigation, object identity cues, command highlights, summary chips, and review-intent controls.
- Pantone 7658 C (`#6A3460`) is authority and depth. Use it for shell bars, pressed or hover states of hero controls, dense metadata emphasis, and other high-contrast depth cues.
- Pantone 7660 C (`#9991A4`) is context and grouping. Use it for contextual fills, selected rows, grouped secondary controls, filter states, timeline rails, and governance or metadata panels.
- Semantic success, warning, error, and info colors remain separate from the 7658/7659/7660 family.
- Most surfaces remain neutral. The purple family is reserved for orientation, context, and high-intent actions.
- Use one dominant purple-family tone per component. Do not mix hero, depth, and context equally on the same element.
- Avoid decorative purple gradients and theme flooding. The product should feel calm, operational, governed, and precise.
