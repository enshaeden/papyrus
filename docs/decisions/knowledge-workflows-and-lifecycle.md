# Knowledge Workflows and Lifecycle

Status: Approved
Owner: Product / Operations / Architecture
Scope: Flagging, authoring, review, publishing, lifecycle states

## Lifecycle states
- Draft
- In Review
- Published
- Flagged
- Archived
- Deprecated

Optional future states:
- Scheduled
- Superseded
- Emergency Update Pending

## Implementation status
This record defines the governing workflow model for Papyrus.
Current UI and route structure may still be transitional in places.
Do not treat transitional screens or interim actor-shaped flows as authority over the lifecycle and workflow boundaries defined here.

## Flag flow

### Intent
Allow Readers, Operators, and Admins to signal potential content issues without exposing every user to the full governance workflow.

### Trigger
From object view, user selects `Flag for review`.

### Submission
User enters short required explanation.
System creates flag record linked to:
- object
- object version if applicable
- submitting user
- timestamp
- reason text
- severity/category if supported

### Visibility
- Reader: can submit; cannot see full queue
- Operator: can view queue, inspect, triage, resolve/reassign/escalate if authorised
- Admin: can oversee and intervene

### Outcomes
- resolved with no content change
- sent to Write for revision
- escalated
- closed as duplicate / invalid if policy allows

## Authoring flow

### Intent
Enable structured knowledge creation and modification without devolving into a generic editor.

### Entry points
- create new object
- open object in Write
- continue draft
- revise object from review feedback

### Steps
1. Select object type or start from object context
2. Apply template and schema
3. Enter structured content
4. Save draft continuously or manually
5. Validate required fields and schema rules
6. Preview formatted output
7. Submit for review

### Operator capabilities
- create/edit draft
- compare versions
- attach references
- respond to review comments
- resubmit

### Constraints
- published content is not directly overwritten
- every substantive change produces version history
- validation must fail early and clearly

## Review flow

### Intent
Provide a queue-based operational workflow for governance and change control.

### Sources into review
- submitted draft
- governance flag
- failed validation requiring intervention
- reassigned review work

### Review actions
- inspect object
- inspect prior version
- inspect comments and flags
- request changes
- approve
- resolve flag
- reassign
- escalate to Admin

### Outcomes
- returned to Write
- approved for publish
- resolved without publish
- escalated

### Role rules
- Operator handles standard review
- Admin handles policy, access, schema, and override cases

## Publish flow

### Intent
Move reviewed content into visible reader-safe knowledge without bypassing control.

### Entry conditions
- object passes validation
- review state permits publish
- publishing user has permission

### Publish actions
- publish immediately
- schedule publish if supported
- replace current published version while preserving history
- rollback through controlled version restore if supported

### Visibility after publish
- Reader sees published content only
- Operator sees published plus operational history as permitted
- Admin sees full record and audit context

### Policy questions to lock
- can Operators publish directly after approval
- does Admin approval gate some object types
- what object types require dual approval
- whether emergency publish exists and how it is audited
