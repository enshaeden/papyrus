---
id: kb-applications-business-apps-password-manager-vault-creation
title: Vault creation
canonical_path: knowledge/applications/business-apps/password-manager/vault-creation.md
summary: This SOP outlines actions IT should perform when someone requests a vault creation in <PASSWORD_MANAGER>.
knowledge_object_type: runbook
legacy_article_type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Vault creation
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
- access
created: '2025-12-09'
updated: '2026-03-05'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Identity
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
- Access Management
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

This SOP outlines actions IT should perform when someone requests a vault creation in <PASSWORD_MANAGER>.

1. First we need to check the business intent and get their manager’s approval before creating a vault.
2. Once we have the approval, login to **<PASSWORD_MANAGER>** admin portal and go to **vaults** section.
3. Click on ‘New Vault' button and give a name and description to the vault as per user’s requirement.
4. You can also set an icon for the vault if you need.
5. Then click on 'create vault' and the vault is created.
6. Then click on ‘share vault' and add the users according to the requestor. By default they will get ‘view’,’edit','share' access.
7. As you are the one who created the vault, you will have full access. But you likely should not be part of their vault, you can remove yourself from the vault once you add members.
8. Inform the requestor that vault is created and they are added to the vault. If in future they want more people added, they can raise an IT request and then we can add them after the approval.
