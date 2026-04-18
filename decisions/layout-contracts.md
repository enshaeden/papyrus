# Layout Contracts

Scope: Shared shell composition, panel rules, action zones, and page composition across canonical surfaces

## Purpose

This record defines the concrete layout contract for the shared Papyrus shell and its canonical surfaces.

Experience principles, visibility rules, route model, actor transition, and tonal guidance are governed by `role-scoped-experience-architecture.md`.

Papyrus uses one production shell and one shared route space.
This record does not define separate shells by role.
Instead, it defines a shared shell and role-conditioned composition rules within shared surfaces.

Canonical request-scoped role context is resolved before render.
Layouts, panels, and navigation must compose from that request identity rather than infer role from path structure or template-local namespace checks.

## Global shell contract

### Top bar

Present across the product:

- global search
- account or system entry points
- page, object, or workflow title
- only context-appropriate primary actions visible to the current user

Rules:

- global search remains shell-owned and centered in the top bar
- the top bar must not become a dumping ground for unrelated cross-workflow actions
- controls that are not visible for the current role must be absent
- admin-only controls must not appear outside Admin-visible surfaces unless intentionally embedded in a shared surface with Admin-only visibility

### Left navigation

- collapsible
- generated from the shared route model plus visibility contracts
- grouped by canonical surface, not by separate role-owned route trees
- never includes hidden or disabled entries for unauthorised surfaces

Rules:

- navigation visibility must match route visibility
- navigation should orient the user to the current surface and adjacent allowed surfaces
- navigation should not expose speculative future destinations, empty placeholders, or hidden controls
- navigation must consume the canonical request role context already resolved by the runtime

### Main content area

- primary task surface for the active route
- visually dominant in the page hierarchy
- not crowded out by contextual chrome or oversight detail

Rules:

- the main area should preserve the canonical purpose of the route
- additional metadata, validation, governance, or admin context must not overwhelm the primary task
- higher-privilege users may see more controls or panels, but the route's main purpose must remain stable

### Right panel

- contextual only
- collapsible by default unless the workflow requires persistent support context
- content varies by surface and by visible role

Rules:

- the right panel supplements the main task and does not replace it
- hidden content must be absent, not disabled
- role-conditioned panel content must match the route's visibility and purpose

## Shared surface contracts

## Read surface contract

Applies to routes such as:

- `/read`
- `/read/object/{object_id}`
- `/read/object/{object_id}/revisions`

### Top bar

- object, service, or page title when applicable
- low to moderate action density
- only actions appropriate to the current role on the current read surface

Typical actions by visibility:

- Reader-visible:
  - flag for review
  - bookmark or share, if supported
- Operator-visible:
  - open writing workflow when allowed
  - inspect flags or history when allowed
- Admin-visible:
  - inspect governance or control affordances when intentionally present on the route

Forbidden for Reader visibility:

- edit
- review queue access
- publish
- template access
- schema access
- user or system administration

### Left navigation

May include:

- hierarchical knowledge tree
- spaces, collections, folders, object groups, or service groupings
- adjacent shared read destinations visible to the current user

Must not include:

- hidden workflow queues
- hidden admin destinations
- entries for routes not visible to the current role

### Main area

- content-first document or object presentation
- title, body, structured sections, attachments, and related links
- readability remains primary even when more privileged roles have additional affordances

### Right panel

Collapsed by default unless the route explicitly requires it.

May include, depending on role visibility:

- owner
- status
- last reviewed
- scope
- related objects
- flag entry point
- history summary
- limited governance context
- limited admin context when intentionally embedded in a shared route

Must not include for Reader visibility:

- review queues
- draft state machine detail
- workflow control clusters
- schema administration
- user or system administration blocks

### Action zones

- primary reading action sits near the title or panel entry point
- action density remains low for Reader visibility
- higher-privilege actions must remain grouped and secondary to content readability

## Write surface contract

Applies to routes such as:

- `/write`
- `/write/new`
- `/write/object/{object_id}/start`
- `/write/object/{object_id}`
- `/write/object/{object_id}/submit`
- `/write/citations/search`
- `/write/objects/search`
- `/import`
- `/import/{ingestion_id}`
- `/import/{ingestion_id}/review`

Minimum visible role: Operator

### Top bar

- page or object title
- task-relevant primary actions only

Typical actions:

- save draft
- validate
- preview
- submit for review
- import-related progression actions where applicable

Admin may see additional oversight or override actions only where justified by the route.

### Left navigation

May include:

- content entry points relevant to writing
- drafts
- new object entry points
- citation search
- import work
- adjacent workflow destinations visible to the current user

Rules:

- navigation should support authoring flow without turning into a generic admin control list
- admin-only destinations remain absent unless the current route itself is Admin-visible

### Main area

- structured authoring workspace
- template- and schema-driven sections where applicable
- visible progress, draft, and validation state
- import review surfaces may use staged progression layouts when needed

### Right panel

May include:

- validation issues
- schema guidance
- completion state
- preview controls
- reference links
- import diagnostics
- governance context relevant to submission

### Action zones

- actions cluster around drafting and submission flow
- do not mix review and writing actions on the same screen unless explicitly required by the workflow
- avoid unnecessary permanent clutter

## Review surface contract

Applies to routes such as:

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

Minimum visible role: Operator

### Top bar

- page or work-item title
- queue-relevant or work-item-relevant actions only

Typical actions:

- resolve
- reassign
- escalate
- request changes
- run validation
- review evidence
- perform governance actions allowed on the current route

### Left navigation

May include:

- queue entry points
- assignments
- activity
- validation runs
- impact analysis
- adjacent review surfaces visible to the current user

### Main area

- queue-led or work-item-led composition
- fast scanning, filtering, opening, and actioning
- object and revision context must remain legible within the review frame

### Right panel

May include:

- work item detail
- comments
- review history
- escalation controls
- assignment controls
- impact context
- evidence summary

### Action zones

- actions cluster around triage, decision, and reassignment
- avoid mixing unrelated authoring actions into the review frame unless explicitly required
- high-consequence review actions should be clearly grouped

## Governance surface contract

Applies to routes such as:

- `/governance`
- `/governance/services`
- `/governance/services/{service_id}`

Minimum visible role: Operator, with broader controls for Admin

### Top bar

- governance page or entity title
- governance-relevant primary actions visible to the current role

### Left navigation

May include:

- services
- governance summaries
- impact views
- adjacent governance destinations visible to the current user

### Main area

- governance and service context first
- relationships, impact, ownership, dependency, and policy-relevant metadata
- operational clarity remains primary

### Right panel

May include:

- dependency warnings
- ownership context
- review or validation summaries
- admin-only governance controls when intentionally embedded on a shared governance surface

### Action zones

- governance actions should be grouped by consequence and scope
- admin-only actions must remain visibly distinct from ordinary operator actions

## Admin surface contract

Applies to routes such as:

- `/admin`
- `/admin/overview`
- `/admin/users`
- `/admin/access`
- `/admin/spaces`
- `/admin/templates`
- `/admin/schemas`
- `/admin/settings`
- `/admin/audit`

Minimum visible role: Admin

### Top bar

- admin page title
- admin-relevant actions only

### Left navigation

Control-plane navigation may include:

- overview
- users and roles
- spaces and access
- templates
- schemas
- audit
- settings

Rules:

- only true admin destinations belong here
- this area is not a duplicate of shared work surfaces

### Main area

- configuration, oversight, and control first
- tables, forms, settings panes, policy views, and audit views
- read previews may appear when needed, but are not the default framing

### Right panel

Optional and page-dependent.

May include:

- help text
- change impact
- dependency warnings
- audit context
- preview context

### Action zones

- explicit, high-consequence actions clearly separated
- destructive actions require confirmation
- admin actions must feel deliberate

## Cross-surface rules

- The same underlying surface should not be duplicated into parallel role-owned layouts merely because a more privileged role can see more within it.
- Shared surfaces should use role-conditioned controls, panels, and metadata density instead of route duplication wherever the surface purpose is the same.
- If a route is visible to multiple roles, the layout identity of that route remains canonical even when control density changes by role.
- Navigation visibility, search visibility, related-link visibility, and action visibility must remain aligned.
- Tests must verify that hidden destinations and hidden controls are absent, not disabled, for the current role.
