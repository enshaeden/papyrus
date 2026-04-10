---
id: kb-applications-business-apps-password-manager-account-recovery
title: Account recovery
canonical_path: knowledge/applications/business-apps/password-manager/account-recovery.md
summary: This SOP outlines actions IT performs when someone forgets their <PASSWORD_MANAGER>' password.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Account recovery
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
- access
created: '2025-12-09'
updated: '2025-12-10'
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
  source_ref: migration/import-manifest.yml
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
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

This SOP outlines actions IT performs when someone forgets their <PASSWORD_MANAGER>' password.

When someone is setting up their <PASSWORD_MANAGER> account for the first time, they receive their security key as well. In the future, if they forget their password, they can use that key to reset their <PASSWORD_MANAGER> password.

If user doesn’t have their security key, then we can follow the below steps to recover their account.

1. Login to **<PASSWORD_MANAGER>** and search for user account in **People** section.
2. Click on the user account and then click on ' **Begin Recovery** '
3. User will receive an email with a link to reset their <PASSWORD_MANAGER> password.
4. Once the reset is done from their end, then we will receive an email to complete the recovery.
5. Then return to their account and click on ' **Complete recovery** '
