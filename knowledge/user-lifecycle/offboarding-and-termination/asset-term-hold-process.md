---
id: kb-user-lifecycle-offboarding-and-termination-asset-term-hold-process
title: Asset Term Hold Process
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/asset-term-hold-process.md
summary: 'Key aspects of a termination hold for asset management include and aren''t limited to: asset retrieval, data security, inventory update, inspection and assessment, compliance and record keeping.'
type: offboarding
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Asset Term Hold Process
team: Identity and Access
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <HR_SYSTEM>
services:
- Endpoint Provisioning
- Offboarding
tags:
- endpoint
- offboarding
created: '2025-11-26'
updated: '2026-02-17'
last_reviewed: '2026-04-07'
review_cadence: quarterly
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
- kb-user-lifecycle-offboarding-and-termination-index
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

Key aspects of a termination hold for asset management include and aren't limited to: asset retrieval, data security, inventory update, inspection and assessment, compliance and record keeping.

At <COMPANY_NAME> a Term Hold starts once IT **receives** an asset from an offboarded user.

**All** assets from offboarded users will be placed on term hold. The term hold period varies from 2-4 weeks to a maximum of “indefinite”, depending on either the employee rank or Legal Hold request. The default term hold periods are:

- **Legal Hold Request** : Indefinite (Don’t remove under any circumstances)
- **VPs:** 4 weeks
- **Directors:** 3 weeks
- **All other standard term holds (including contractors):** 2 weeks

Policy Exception: If IT is short on stock for new hires, we may request approval to wipe a machine sooner than the Term Hold period by emailing the <PERSON_NAME> of the legal team at: <EMAIL_ADDRESS> , Security team at: <EMAIL_ADDRESS> , HR and the previous manager. Please make a note of such interactions within the asset's <ASSET_MANAGEMENT_SYSTEM> record and create a ticket documenting the request and permission.
