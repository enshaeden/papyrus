---
id: kb-applications-business-apps-collaboration-platform-deleting-archived-collaboration-platform-users-steps-and-considerations-for-restoration
title: 'Deleting Archived <COLLABORATION_PLATFORM> Users: Steps and Considerations for Restoration'
canonical_path: knowledge/applications/business-apps/collaboration-platform/deleting-archived-collaboration-platform-users-steps-and-considerations-for-restoration.md
summary: Delete archived users only after approval and after confirming the restoration and data-loss
  window.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: 'Deleting Archived <COLLABORATION_PLATFORM> Users: Steps and Considerations for Restoration'
team: Identity and Access
systems:
- <COLLABORATION_PLATFORM>
tags:
- access
created: '2026-02-25'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Access Management
prerequisites:
- Verify the request, identity details, and required approvals before changing access or account state.
- Confirm the target system and business context match the scope of this article.
steps:
- Review the imported procedure body below and confirm the documented scope matches the task at hand.
- Execute the documented steps in order and record the outcome in the relevant ticket or audit trail.
- Stop and escalate if approvals, prerequisites, or expected checkpoints do not match the live request.
verification:
- The expected outcome described in the procedure is confirmed in the target system or ticket record.
- Completion notes, exceptions, and evidence are recorded in the relevant audit or support workflow.
rollback:
- Revert any reversible change described in the procedure if verification fails.
- Pause the workflow and escalate when the documented rollback path is unclear or incomplete.
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-applications-business-apps-collaboration-platform-index
- kb-applications-business-apps-collaboration-platform-collaboration-platform-monthly-license-recovery
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-business-apps-collaboration-platform-index
- kb-applications-business-apps-collaboration-platform-collaboration-platform-monthly-license-recovery
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Deletion Preconditions

1. Obtain the required elevated approval before deleting archived users.
2. Confirm the platform retention window and restoration cutoff.
3. Confirm that deleting the user will not remove required shared content without a separate ownership-transfer step.

## Deletion Workflow

1. Open the archived user record in the collaboration admin portal.
2. Confirm the user is no longer needed for retention or restoration.
3. Execute the delete action and acknowledge the permanent-deletion warnings.
4. Record the approval source, deletion date, and restoration deadline in the ticket.

## Restoration Note

Deleted users can be restored only within the platform’s documented recovery window. After that window expires, the deletion is permanent.
