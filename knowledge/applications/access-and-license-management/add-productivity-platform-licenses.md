---
id: kb-applications-access-and-license-management-add-productivity-platform-licenses
title: Add <PRODUCTIVITY_PLATFORM> Licenses
canonical_path: knowledge/applications/access-and-license-management/add-productivity-platform-licenses.md
summary: Canonical article for Add <PRODUCTIVITY_PLATFORM> Licenses imported from <KNOWLEDGE_PORTAL>.
type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Add <PRODUCTIVITY_PLATFORM> Licenses
team: Identity and Access
systems:
- <COLLABORATION_PLATFORM>
services:
- Access Management
tags:
- account
- access
created: '2026-03-19'
updated: '2026-03-19'
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
- kb-applications-access-and-license-management-index
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

# First-time setup

1. Go to <SUPPLIER_PORTAL_URL>
  1. Click “Sign in”
    2. Select “Need an account?” even if you already have one
2. Select **Enter my Token and Key** .
  1. Leave everything else blank, just enter the **Token** and **Key**
      1. Token and Key are saved in the [IT Vault](<INTERNAL_URL>) in <PASSWORD_MANAGER>
    2. Click **Next** .
3. Complete the registration form
4. Verify your email from the link that gets sent

# Adding new licenses

1. Sign in to [<SUPPLIER_PORTAL_URL>](<SUPPLIER_PORTAL_URL>)](<INTERNAL_URL>)
2. Select “Subscription Management” from the sidebar
3. Find the desired license in the correct approved subscription account for the requesting business unit.
  1. Note: If multiple subscription accounts exist, verify you are modifying the intended contract before changing seat counts.
4. Click on the **⚙️Seats** for the desired license
5. Enter the new value (more or less) in the “New Seat Count” field and hit **Confirm**
