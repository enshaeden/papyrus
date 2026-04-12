# Route Separation and Experience Boundaries

Status: Approved
Owner: Architecture
Scope: Web app route structure, layout ownership, role isolation

## Core rule
Reader, Operator, and Admin are separate experience route groups.
They are not tabs within one dashboard and not modes of one shared page.

## Route groups

### Shared
- `/search`
- `/account`
- `/system-menu` (if route-based)
- shared utility routes only if they remain role-safe

### Reader
- `/reader`
- `/reader/browse`
- `/reader/tree/:nodeId`
- `/reader/object/:objectId`
- `/reader/object/:objectId/flag`

### Operator
- `/operator`
- `/operator/read`
- `/operator/read/tree/:nodeId`
- `/operator/read/object/:objectId`
- `/operator/write`
- `/operator/write/drafts`
- `/operator/write/new`
- `/operator/write/object/:objectId`
- `/operator/write/object/:objectId/validate`
- `/operator/write/object/:objectId/preview`
- `/operator/review`
- `/operator/review/flags`
- `/operator/review/flags/:flagId`
- `/operator/review/assignments`
- `/operator/review/object/:objectId`

### Admin
- `/admin`
- `/admin/overview`
- `/admin/users`
- `/admin/roles`
- `/admin/spaces`
- `/admin/access`
- `/admin/templates`
- `/admin/schemas`
- `/admin/governance`
- `/admin/publishing`
- `/admin/audit`
- `/admin/settings`

## Route rules
- Route guards must enforce role access before render.
- Navigation generation must derive from role-scoped route definitions, not from one global list with runtime filtering.
- Deep links must still respect role access and fail closed.
- Search results must link only to routes the current role can access.
- Production must not expose a route or client control for manual role switching.

## Layout ownership
- `/reader/*` uses Reader shell
- `/operator/*` uses Operator shell
- `/admin/*` uses Admin shell
- Shared primitives may be reused, but shell composition remains separate.

## URL and naming rules
- Route names must make role ownership obvious.
- Layout files, shell files, test files, and route definitions should mirror the same structure.