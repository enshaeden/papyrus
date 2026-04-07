---
id: kb-applications-business-apps-password-manager-vault-access-in-password-manager
title: Vault access in <PASSWORD_MANAGER>
canonical_path: knowledge/applications/business-apps/password-manager/vault-access-in-password-manager.md
summary: This SOP outlines the steps IT should follow when someone requests any vault access in <PASSWORD_MANAGER>
type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Vault access in <PASSWORD_MANAGER>
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
services:
- Identity
- Access Management
tags:
- account
- authentication
- access
created: '2025-12-02'
updated: '2026-03-05'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
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
related_articles:
- kb-applications-business-apps-password-manager-index
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

This SOP outlines the steps IT should follow when someone requests any vault access in <PASSWORD_MANAGER>

1. Before giving vault access, check the business intent of the user and get the approval from the vault owner.
2. You can follow the steps on [how to check vault owner in <PASSWORD_MANAGER>](<INTERNAL_URL>)
3. Once you got approval, login to [<PASSWORD_MANAGER>](<INTERNAL_URL>) and click on 'Vaults'
4. Search for vault name and click on it.
5. Then click on ‘Share vault' and enter user’s email address and select it to add the user to that vault.
