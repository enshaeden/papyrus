# Role-Scoped Experience Architecture

Scope: Production role model, visibility, shared route space, shell ownership, actor transition, and tonal guidance

## Purpose

This record is the canonical authority for Papyrus role-scoped experience architecture.

Use it when changing:

- production role boundaries
- route visibility and route guards
- shell ownership
- search visibility
- role-conditioned navigation
- actor-to-role transition rules

Concrete shell composition rules live in `layout-contracts.md`.
Knowledge lifecycle and workflow state machines live in `knowledge-workflows-and-lifecycle.md`.

Papyrus uses one root interface, one production shell, and one shared route space.
It does not create separate route trees or separate shells by role.

Roles determine which routes, navigation items, actions, panels, and search results are present for the current user within that shared interface.

## Core rules

- There is one root interface.
- There is one production shell.
- There is one shared route space.
- There are three canonical production roles: `Reader`, `Operator`, and `Admin`.
- Roles are hierarchical for access:
  - `Operator` includes Reader-visible access.
  - `Admin` includes Operator-visible and Reader-visible access.
- Reader is for consumption.
  - Readers can access only Reader-visible content and actions.
  - Operator and Admin routes, navigation items, controls, and search results are absent.
- Operator is for work.
  - Operators can access Reader content.
  - Operators can also access writing, review, governance, and management surfaces intended for operational work.
  - Admin-only routes, navigation items, controls, and search results are absent.
- Admin is for control.
  - Admins can access Reader and Operator content.
  - Admins can also access control surfaces that fundamentally change the Read and Operate experience for others.
  - No routes, navigation items, controls, or search results are hidden from an Admin.
- Hidden means absent, not merely disabled, for the current user.
- Route visibility, navigation visibility, control visibility, related-link visibility, panel visibility, and search visibility MUST match.
- Search visibility must match route visibility.
- Global search is shell-owned and remains centered in the top bar.
- Production role switching is forbidden.
- Granting a user a different production role is the sole discretion of an Admin.

## Architectural stance

Papyrus does not use role-owned route namespaces such as Reader routes, Operator routes, and Admin routes for the same underlying work.

Papyrus uses canonical shared routes.
Role changes what a user can see and do on those routes.
Where a surface is not visible for a role, it is absent and direct access must fail closed.

Admin is broader access over the same product, not a separate product mode.

## Role model and actor transition

The role model is the authority for production experience architecture.
The actor model is a transitional development and testing mechanism.

Actors may shape local defaults such as landing path, emphasis, density, and workflow priority in development.
Actors must not be treated as authority for permanent route structure, navigation architecture, shell structure, or production visibility boundaries.

## Canonical request identity

Papyrus must resolve the current request role from canonical request identity, not from URL shape.

The local runtime uses runtime configuration to set a default actor for incoming requests.
The current role is then derived from that actor mapping for route guards, navigation, and layout composition.

Rules:

- URL path prefixes are not role authority.
- Query parameters and cookies are not role authority unless a later decision explicitly defines them.
- Each request must carry canonical `actor_id` and `role_id` before route dispatch.
- Route visibility, action visibility, navigation visibility, search visibility, and layout composition must all consume that same request-scoped identity.
- `/` may resolve to a role-appropriate landing path after the request role is known.
- Local runtime defaults are:
  - Reader -> `/read`
  - Operator -> `/review`
  - Admin -> `/admin/overview`

### Current mapping

- `local.reader` maps to Reader.
- `local.operator` maps to Operator.
- `local.reviewer` maps to Operator with review-heavy development defaults.
- `local.manager` maps to Admin-oriented development defaults. It does not establish a fourth production role.

### Transition rules

- Do not treat `local.reviewer` as a separate permanent product experience unless a later decision creates one.
- Do not treat `local.manager` as proof that Papyrus needs a fourth permanent experience.
- Do not justify route duplication, shell duplication, or alternate production navigation architecture by pointing to actor-shaped development behaviour.
- Production architecture must converge on one shared interface with role-conditioned visibility, not actor-shaped permutations.

## Visibility and experience matrix

| Surface / Capability | Reader | Operator | Admin | Notes |
|---|---:|---:|---:|---|
| Global search bar | Yes | Yes | Yes | Results filtered by role visibility |
| Account/system menu | Yes | Yes | Yes | Menu entries may differ by role |
| Dev-only role switcher | Dev only | Dev only | Dev only | Never in production |
| Reader browse / content / object detail | Yes | Yes | Yes | Shared read surface |
| Flag submission | Yes | Yes | Yes | Reader sees submission only |
| Full flag details and resolution | No | Yes if authorised | Yes | Policy-controlled |
| Writing workspace | No | Yes | Yes | Shared surface; hidden from Reader |
| Review queues and assignments | No | Yes | Yes | Shared surface; hidden from Reader |
| Governance workspace | No | Yes if allowed | Yes | Shared surface with stronger admin controls |
| Templates | No | Use only if allowed | Yes | Template administration is Admin-owned by default |
| Schemas | No | No or limited inspect | Yes | Strong admin boundary |
| Users, roles, spaces, access, settings | No | No | Yes | Admin-only |
| Audit log | No | Limited object history | Yes | Distinguish object history from full system audit |

## Explicit role boundaries

- Reader must never see Authoring, Review, Template, Schema, Admin, Publish, or User Management controls.
- Operator must never see User Management, Access Management, Schema Administration, or System Settings unless explicitly elevated by role.
- Admin owns access, schema, template, oversight policy, publishing policy, and audit controls.
- Admin access includes Reader and Operator surfaces.
- Admin is not a catch-all for every advanced or inconvenient screen.

## Shared route model

Papyrus uses a shared route model rather than role-owned route namespaces.

Illustrative route families include:

### Shared entry and read surfaces

- `/`
- `/read`
- `/read/object/{object_id}`
- `/read/object/{object_id}/revisions`

### Operator-visible work surfaces

- `/import`
- `/import/{ingestion_id}`
- `/import/{ingestion_id}/review`
- `/write`
- `/write/new`
- `/write/object/{object_id}/start`
- `/write/object/{object_id}`
- `/write/object/{object_id}/submit`
- `/write/citations/search`
- `/write/objects/search`
- `/review`
- `/review/activity`
- `/review/object/{object_id}/{revision_id}`
- `/review/object/{object_id}/{revision_id}/assign`
- `/review/object/{object_id}/archive`
- `/review/object/{object_id}/suspect`
- `/review/object/{object_id}/supersede`
- `/review/object/{object_id}/evidence/revalidate`
- `/review/impact/object/{object_id}`
- `/review/impact/service/{service_id}`
- `/review/validation-runs`
- `/review/validation-runs/new`
- `/governance`
- `/governance/services`
- `/governance/services/{service_id}`

### Admin-only control surfaces

- `/admin`
- `/admin/overview`
- `/admin/users`
- `/admin/access`
- `/admin/spaces`
- `/admin/templates`
- `/admin/schemas`
- `/admin/settings`
- `/admin/audit`

A route's presence in the product does not imply visibility to every role.
Each route must declare its minimum visible role and must fail closed on direct access when the current user lacks permission.

## Route semantics

- A canonical route should represent a canonical surface.
- The same domain action must not be duplicated under separate role-owned namespaces merely to reflect role.
- If Reader, Operator, and Admin can all access the same underlying object or workflow surface, they should do so through the same canonical route, with role-conditioned visibility of controls and panels inside that surface.
- Separate routes are justified only when the surface itself is materially different in purpose, not merely because a more privileged role can see more within it.

## Route and shell rules

- Route guards must enforce role access before render.
- Deep links must still respect role access and fail closed.
- Navigation must derive from the shared route model plus role visibility rules, not from separate route trees per role.
- Search results must link only to routes the current role can access.
- Related links, recents, dashboards, queues, and command surfaces must include only destinations visible to the current user.
- A shared route may render different controls, side panels, metadata density, and oversight affordances by role, but the route identity remains canonical.
- Production must not expose a route or client control for manual role switching.
- Layout files, shell files, route definitions, and tests should mirror the shared route model and its visibility contracts, not role-owned namespaces.

## Entry and landing rules

- `/` is the shared application entry point.
- `/` is not a role-owned destination.
- After authentication, the application may resolve `/` to a role-appropriate default landing experience within the shared route space.
- That landing behaviour must not be treated as evidence for separate role route trees or separate production shells.

## Search rules

- Global search is shell-owned.
- Global search must remain centered in the top bar.
- Search indexing and search result projection must respect role visibility boundaries.
- A user must not receive search hits, command suggestions, object links, service links, revision links, or administrative targets for destinations they cannot access.
- Search filtering is a product rule, not merely a presentation choice.

## Implementation rules

- Each route definition MUST declare a minimum visible role.
- Each action definition MUST declare a minimum visible role.
- Each search result type MUST declare a minimum visible role.
- Shared surfaces SHOULD use role-conditioned composition rather than role-specific route duplication.
- Admin-only controls SHOULD appear as panels, sections, or actions within canonical shared surfaces when the underlying surface is the same.
- Tests MUST verify that hidden destinations are absent from navigation, search, related links, command surfaces, and direct route access for the current role.

## Tonal guidance

- Papyrus uses a governed tonal family centered on Pantone 7659 C, not a single-color theme.
- Pantone 7659 C (`#5D3754`) is identity and intent. Use it for primary actions, active navigation, object identity cues, command highlights, summary chips, and review-intent controls.
- Pantone 7658 C (`#6A3460`) is authority and depth. Use it for shell bars, pressed or hover states of hero controls, dense metadata emphasis, and other high-contrast depth cues.
- Pantone 7660 C (`#9991A4`) is context and grouping. Use it for contextual fills, selected rows, grouped secondary controls, filter states, timeline rails, and oversight or metadata panels.
- Semantic success, warning, error, and info colors remain separate from the 7658/7659/7660 family.
- Most surfaces remain neutral. The purple family is reserved for orientation, context, and high-intent actions.
- Use one dominant purple-family tone per component. Do not mix hero, depth, and context equally on the same element.
- Avoid decorative purple gradients and theme flooding. The product should feel calm, operational, governed, and precise.
