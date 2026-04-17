# Experience Conformance Checklist

Use this checklist for manual browser validation after route, shell, navigation, visibility, or workflow changes.

Treat this file as runtime validation procedure.
Authoritative constraints still live in:

- `decisions/role-scoped-experience-architecture.md`
- `decisions/layout-contracts.md`
- `decisions/runtime-role-context-and-access-resolution.md`
- `decisions/knowledge-workflows-and-lifecycle.md`
- `decisions/web-ui-component-contracts.md`

## Global checks

Run these checks on every route listed below:

- Landing target matches canonical role home.
- Left navigation shows only role-permitted destinations.
- Top-bar actions show only role-permitted actions.
- Hidden controls are absent, not disabled, unless a decision record explicitly says otherwise.
- Direct URL access fails closed for disallowed routes and actions.
- Shared routes keep one canonical surface and expand composition by role instead of splitting paths.
- Search, related links, and recommendation surfaces expose only destinations the role can open.
- Object detail density matches role purpose.
- Write, review, governance, and admin actions stay inside workflow boundaries.

## Reader checklist

### `/`

- Redirects to `/read`.
- Does not redirect to `/review` or `/admin/overview`.

### `/read`

- Primary surface remains content-first.
- Left navigation excludes `/write`, `/import`, `/review`, `/governance`, and all `/admin/*`.
- Search results exclude non-reader-visible objects and non-reader-visible routes.
- Queue or landing modules do not expose review, governance, or admin actions.

### `/read/object/{reader-visible-object}`

- Primary content dominates.
- Context rail does not become governance-heavy.
- Review controls, ingest controls, governance controls, and admin controls are absent.
- Related links include only reader-visible objects.
- Search entrypoints and inline discovery stay reader-safe.

### Reader fail-closed probes

- `/write` fails closed.
- `/write/new` fails closed.
- `/write/object/{object_id}` fails closed.
- `/write/object/{object_id}/submit` fails closed.
- `/write/citations/search` fails closed.
- `/write/objects/search` fails closed.
- `/import` fails closed.
- `/import/{ingestion_id}` fails closed.
- `/import/{ingestion_id}/review` fails closed.
- `/review` fails closed.
- `/review/activity` fails closed.
- `/review/object/{object_id}/{revision_id}` fails closed.
- `/review/object/{object_id}/{revision_id}/assign` fails closed.
- `/review/object/{object_id}/archive` fails closed.
- `/review/object/{object_id}/suspect` fails closed.
- `/review/object/{object_id}/supersede` fails closed.
- `/review/object/{object_id}/evidence/revalidate` fails closed.
- `/review/impact/object/{object_id}` fails closed.
- `/review/impact/service/{service_id}` fails closed.
- `/review/validation-runs` fails closed.
- `/review/validation-runs/new` fails closed.
- `/governance` fails closed.
- `/governance/services` fails closed.
- `/governance/services/{service_id}` fails closed.
- `/admin` fails closed.
- `/admin/overview` fails closed.
- `/admin/users` fails closed.
- `/admin/access` fails closed.
- `/admin/spaces` fails closed.
- `/admin/templates` fails closed.
- `/admin/schemas` fails closed.
- `/admin/settings` fails closed.
- `/admin/audit` fails closed.

## Operator checklist

### `/`

- Redirects to `/review`.

### `/read`

- Shared read route stays readable.
- Operator-visible metadata may expand context, but route still reads as knowledge surface.
- Navigation still highlights Reader destination correctly.

### `/read/object/{active-object}`

- Object detail includes operator-appropriate metadata density.
- Related links include operator-visible governed objects.
- Review state, trust state, provenance, and workflow context appear where contracts expect them.
- Admin-only controls remain absent.

### `/write`

- Redirect or landing behavior points into primary write route without exposing retired advanced route copies.

### `/write/new`

- Primary authoring route opens.
- Object-type picker excludes deferred advanced blueprint types unless new scope decision changes that.
- Hidden controls are absent.

### `/write/object/{object_id}`

- Draft editing route opens.
- Workflow panels show write-specific guidance.
- Review and admin actions do not overtake authoring surface.
- Related object and citation search helpers return only operator-visible results.

### `/write/object/{object_id}/submit`

- Submit flow opens for eligible drafts.
- Review submission controls appear only when workflow permits them.

### `/write/citations/search`

- Returns operator-visible citation candidates only.
- Returned items do not leak reader-hidden or admin-only destinations.

### `/write/objects/search`

- Returns operator-visible related-object candidates only.
- Returned items do not leak reader-hidden or admin-only destinations.

### `/import`

- Upload workbench opens.
- Browser upload and local-path affordances match runtime configuration.
- Reader-only shell copy does not appear.

### `/import/{ingestion_id}`

- Extraction and mapping detail open.
- Ingest surface shows provenance, warnings, and next action.
- Route does not expose admin-only control-plane actions.

### `/import/{ingestion_id}/review`

- Mapping review opens.
- Canonical field name `object_lifecycle_state` appears.
- Legacy field name `status` does not render.
- Convert action remains workflow-gated.

### `/review`

- Review queue opens.
- Queue ranking, counts, and next actions match operator workflow.
- Admin-only control-plane destinations remain absent.

### `/review/activity`

- Shared activity surface opens.
- Operator shell treats route as activity, not admin control plane.
- Only operator-allowed audit context renders.

### `/review/object/{object_id}/{revision_id}`

- Review detail opens.
- Decision controls appear only when revision state allows them.
- Archive, suspect, supersede, and revalidate actions align with workflow policy.

### `/review/object/{object_id}/{revision_id}/assign`

- Assignment route opens.
- Available assignee and assignment actions remain workflow-valid.

### `/review/object/{object_id}/archive`

- Archive flow opens only for valid objects.
- Required acknowledgements render when policy requires them.

### `/review/object/{object_id}/suspect`

- Suspect flow opens only for valid objects.
- Policy and impact context stay visible.

### `/review/object/{object_id}/supersede`

- Supersede flow opens only for valid objects.
- Replacement search and linkage stay operator-visible only.

### `/review/object/{object_id}/evidence/revalidate`

- Revalidation flow opens only for valid objects.
- Evidence state and next action stay explicit.

### `/review/impact/object/{object_id}`

- Object impact route opens.
- Related services and impacted objects respect operator visibility.

### `/review/impact/service/{service_id}`

- Service impact route opens.
- Impact composition stays review-centric.

### `/review/validation-runs`

- Validation run history opens.
- Route stays shared review surface, not admin-only page.

### `/review/validation-runs/new`

- New validation run flow opens.
- Trigger controls remain operator-valid.

### `/governance`

- Governance landing opens.
- Surface stays control-and-oversight-focused.
- Admin-only settings links remain absent.

### `/governance/services`

- Service catalog opens.
- Service visibility and related links stay role-safe.

### `/governance/services/{service_id}`

- Service detail opens.
- Related knowledge, impact, and lifecycle context remain operator-visible only.

## Admin checklist

### `/`

- Redirects to `/admin/overview`.

### `/admin`

- Redirects to `/admin/overview`.

### `/admin/overview`

- Admin landing opens.
- Shell reads as control plane, not operator workflow clone.

### `/admin/users`

- Users surface opens.
- Admin-only actions remain absent from non-admin roles.

### `/admin/access`

- Access surface opens.
- Shared-route links do not leak control-plane ownership.

### `/admin/spaces`

- Spaces surface opens.

### `/admin/templates`

- Templates surface opens.

### `/admin/schemas`

- Schemas surface opens.

### `/admin/settings`

- Settings surface opens.

### `/admin/audit`

- Redirects to `/review/activity`.
- Admin navigation still highlights Audit entry after redirect.

### Admin inheritance checks on shared routes

Validate all Operator-shared routes under Admin role:

- `/read`
- `/read/object/{active-object}`
- `/write`
- `/write/new`
- `/write/object/{object_id}`
- `/write/object/{object_id}/submit`
- `/write/citations/search`
- `/write/objects/search`
- `/import`
- `/import/{ingestion_id}`
- `/import/{ingestion_id}/review`
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

For each shared route above:

- Route opens without exact-role failure.
- Higher privilege adds allowed context and controls without splitting route identity.
- Admin-only control-plane links remain available from shared shell where intended.
- Operator-only omissions do not accidentally hide Admin inheritance paths.

## Route retirement probes

Confirm these retired paths fail closed:

- `/operator/read`
- `/reader/object/{object_id}`
- `/admin/inspect`
- `/dashboard/oversight`
- `/review/queue`
- `/operator/import`
- `/operator/write/new`
- `/write/advanced`
