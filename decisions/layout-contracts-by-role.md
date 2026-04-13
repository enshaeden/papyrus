# Layout Contracts by Role

Status: Approved
Owner: UX / Front-end Architecture
Scope: Shell composition, panel rules, action zones, and page composition by role

## Purpose

This record defines the concrete layout contract for each role-owned shell.

Experience principles, visibility rules, route groups, shell ownership, actor transition, and tonal guidance are governed by `role-scoped-experience-architecture.md`.

## Global shell contract

### Top bar

Present on all experiences:

- global search and account/system entry points according to the experience architecture
- page or object title
- only role-appropriate primary actions

Top bar must not become a dumping ground for cross-role or cross-workflow actions.

### Left navigation

- collapsible
- role-scoped
- generated from that role's route model
- never includes hidden or disabled entries for unauthorised surfaces

### Main content area

- primary task surface for the active role
- visually dominant in the page hierarchy
- not crowded out by contextual oversight chrome

### Right panel

- contextual only
- collapsible by default unless the workflow requires persistent validation
- content varies by role and page type

## Reader layout contract

### Top bar

- object title when in object view
- low-action density

Allowed actions:

- flag for review
- bookmark or share, if supported

Forbidden actions:

- edit
- review queue access
- publish
- template or schema access

### Left navigation

- hierarchical knowledge tree
- spaces, collections, folders, or object groups
- no task queues
- no admin destinations

### Main area

- formatted document view
- content-first hierarchy
- object title, document body, embedded sections, attachments, and related links

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

- primary reader action sits near the title or right-panel entry point
- action density remains low

## Operator layout contract

### Top bar

- page title
- task-relevant primary actions

Allowed actions vary by mode:

- Content: open in Authoring, view flags
- Authoring: save draft, validate, preview, submit for review
- Review: resolve, reassign, escalate, request changes

### Left navigation

Task-oriented sections:

- Content
- Authoring
- Review

Content may include tree navigation.
Authoring may include drafts and authoring entry points.
Review may include queues and assignments.

### Main area

Determined by active mode.

#### Content

- content-first document presentation
- operational affordances without degrading readability

#### Authoring

- structured authoring workspace
- template- and schema-driven sections
- visible progress, draft, and validation state

#### Review

- queue and work-item led
- fast scanning, filtering, opening, and actioning

### Right panel

#### Content

- expanded oversight context
- flags, history summary, status, and ownership

#### Authoring

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

- actions cluster around the active workflow
- do not mix write and review actions on the same surface unless explicitly required
- avoid permanent clutter in Content

## Admin layout contract

### Top bar

- admin page title
- admin-relevant actions only

### Left navigation

Control-plane navigation:

- overview
- users and roles
- spaces and access
- templates
- schemas
- oversight
- publishing
- audit
- settings

### Main area

- configuration and oversight first
- tables, forms, settings panes, and audit views
- object read preview available when needed, but not the default framing

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
- admin actions must feel deliberate
