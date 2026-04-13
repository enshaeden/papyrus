# Layout Contracts by Role

Owner: UX / Front-end Architecture
Scope: Shell composition, panel rules, action zones, content hierarchy

## Global shell contract

### Top bar
Present on all experiences:
- global search
- account/system menu trigger
- page or object title
- only role-appropriate primary actions
- global search remains centered in the shell; identity and shell controls must yield around it instead of moving it

Top bar must not become a dumping ground for cross-role actions.

### Left navigation
- collapsible
- role-scoped
- generated from that role’s route model
- must never include hidden or disabled entries for unauthorised surfaces

### Main content area
- primary task surface for the active role
- must visually dominate the experience
- must not be crowded out by governance chrome

### Right panel
- contextual only
- collapsible by default unless workflow requires persistent validation
- contents differ by role and page type

## Reader layout contract

### Top bar
- search
- account/system menu
- object title when in object view

Allowed actions:
- flag for review
- maybe bookmark/share if supported

Forbidden actions:
- edit
- review queue access
- publish
- template/schema access

### Left nav
- hierarchical knowledge tree
- spaces / collections / folders / object groups
- no task queues
- no admin destinations

### Main area
- formatted document view
- content-first hierarchy
- object title, document body, embedded sections, attachments, related links
- design must feel like reading a document, not operating a system

### Right panel
Collapsed by default.
Allowed content:
- owner
- status
- last reviewed
- scope
- related objects
- flag entry point

Forbidden content:
- full review queue
- draft state machine
- workflow controls
- admin metadata blocks

### Action zones
- primary reader action sits near title or right panel entry
- action density must remain low
- Reader page must remain quiet

## Operator layout contract

### Top bar
- search
- account/system menu
- page title
- task-relevant primary actions

Allowed actions vary by mode:
- Read: open in Write, view flags
- Write: save draft, validate, preview, submit for review
- Review: resolve, reassign, escalate, request changes

### Left nav
Task-oriented.
Sections:
- Read
- Write
- Review

Read may include tree navigation.
Write may include drafts and authoring entry points.
Review may include queues and assignments.

### Main area
Determined by active mode.

#### Read
- same content-first document presentation as Reader
- includes operational affordances without degrading readability

#### Write
- structured authoring workspace
- template/schema-driven sections
- progress visibility
- draft and validation state visible

#### Review
- queue and work-item led
- fast scanning, filtering, opening, actioning

### Right panel
#### Read
- expanded governance context
- flags, history summary, status, ownership

#### Write
- validation issues
- schema guidance
- completion state
- preview controls or reference links

#### Review
- work item detail
- comments
- review history
- escalation or assignment controls

### Action zones
- actions must cluster around the active workflow
- do not mix write and review actions on the same surface unless explicitly required
- avoid permanent clutter in Read

## Admin layout contract

### Top bar
- search
- account/system menu
- admin page title
- admin-relevant actions only

### Left nav
Control-plane navigation:
- overview
- users and roles
- spaces and access
- templates
- schemas
- governance
- publishing
- audit
- settings

### Main area
- configuration and oversight first
- tables, forms, settings panes, audit views
- object read preview available when needed, but not the default admin framing

### Right panel
Optional, page-dependent.
Used for:
- help text
- change impact
- dependency warnings
- audit or preview context

### Action zones
- explicit, high-consequence actions clearly separated
- destructive actions require confirmation
- admin actions must feel deliberate, not ambient

## Layout invariants
- Reader is library-like.
- Operator is workshop-like.
- Admin is control-room-like.
- No experience may inherit another’s clutter.

## Tonal balance
- Neutral surfaces dominate every role experience.
- Pantone 7659 C (`#5D3754`) carries identity and intent for primary actions and orientation.
- Pantone 7658 C (`#6A3460`) is reserved for shell depth, stronger emphasis, and pressed or hover states of hero controls.
- Pantone 7660 C (`#9991A4`) appears as contextual tinting for grouping, selection, and support surfaces.
- Role shells and panels should not combine all three tones at equal weight. One dominant purple-family tone per component is the contract.
