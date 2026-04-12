---
id: kb-applications-business-apps-collaboration-platform-collaboration-platform-monthly-license-recovery
title: <COLLABORATION_PLATFORM> Monthly License Recovery
canonical_path: knowledge/applications/business-apps/collaboration-platform/collaboration-platform-monthly-license-recovery.md
summary: Review suspended accounts each month and archive or remove inactive accounts to recover collaboration-platform
  licenses.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <COLLABORATION_PLATFORM> Monthly License Recovery
team: Identity and Access
systems:
- <COLLABORATION_PLATFORM>
- <HR_SYSTEM>
tags:
- access
created: '2025-12-10'
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
- kb-applications-business-apps-collaboration-platform-deleting-archived-collaboration-platform-users-steps-and-considerations-for-restoration
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-business-apps-collaboration-platform-index
- kb-applications-business-apps-collaboration-platform-deleting-archived-collaboration-platform-users-steps-and-considerations-for-restoration
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Purpose

Review suspended accounts each month and recover unused `<COLLABORATION_PLATFORM>` licenses in a controlled way.

## Monthly Workflow

1. Export the list of suspended accounts from the collaboration admin portal.
2. Export the current inactive-worker report from `<HR_SYSTEM>`.
3. Compare the two lists in a working spreadsheet.
4. Confirm which suspended users are both inactive and outside the defined retention window.
5. Archive or remove those users according to the approved retention policy.

## Notes

- Archived accounts may consume a lower-cost retention license depending on the platform configuration.
- Permanent deletion should follow the separate archived-user deletion procedure and requires elevated approval.
- Keep the monthly ticket or audit record linked to the working spreadsheet and the final action list.
