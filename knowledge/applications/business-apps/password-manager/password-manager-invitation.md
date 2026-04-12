---
id: kb-applications-business-apps-password-manager-password-manager-invitation
title: <PASSWORD_MANAGER> Invitation
canonical_path: knowledge/applications/business-apps/password-manager/password-manager-invitation.md
summary: "This SOP outlines the steps IT should follow to send a <PASSWORD_MANAGER> invitation to users.\
  \ The following steps work for both FTE\u2019s and Contractors."
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <PASSWORD_MANAGER> Invitation
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
- access
created: '2025-12-02'
updated: '2026-03-05'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Identity
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
- kb-applications-business-apps-password-manager-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
related_articles:
- kb-applications-business-apps-password-manager-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

This SOP outlines the steps IT should follow to send a <PASSWORD_MANAGER> invitation to users. The following steps work for both FTE’s and Contractors.

1. Make sure to get the user’s manager approval before sending the <PASSWORD_MANAGER> invitation.
2. Once you get manager approval, login to [<PASSWORD_MANAGER>](<INTERNAL_URL>) account.
3. Click on ‘People' and then 'Invite people’
4. Enter user’s email address and make sure Invitation type is 'Team Member'.
5. Click on 'Invite' to send an invite.
6. User will receive <PASSWORD_MANAGER> invitation email to their inbox. Once they accept the invitation and create a <PASSWORD_MANAGER> account, you will receive an email to confirm their account.
7. Then go to “Dashboard“ and click on ‘People waiting to be confirmed' under 'Onboarding’ section.
8. Click on 3 dots and click 'confirm'
