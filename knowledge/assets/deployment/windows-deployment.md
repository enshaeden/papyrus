---
id: kb-assets-deployment-windows-deployment
title: Windows Deployment
canonical_path: knowledge/assets/deployment/windows-deployment.md
summary: All Windows PCs are enrolled in <ENDPOINT_MANAGEMENT_PLATFORM> during initial setup, when the
  new hire selects "Work Account" and signs in with their <COMPANY_NAME> email .
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Windows Deployment
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- windows
created: '2026-02-25'
updated: '2026-02-26'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
prerequisites:
- Confirm the device, asset record, and office or shipping context before taking action.
- Verify you have the required inventory, MDM, or ticketing access for the task.
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
- kb-assets-deployment-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-deployment-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## **Windows Setup**

All Windows PCs are enrolled in **<ENDPOINT_MANAGEMENT_PLATFORM>** during initial setup, when the new hire selects **"Work Account"** and signs in with their **<COMPANY_NAME> email** .

Steps can be found here: [Windows Device Lifecycle Windows Device Lifecycle](../acquisition/windows-device-lifecycle.md)

**Important Guidelines:**

- Users must have completed the <IDENTITY_PROVIDER> **password and MFA setup** beforehand.
- IT must assign the following licenses prior to deployment:
  - **<ENDPOINT_MANAGEMENT_PLATFORM> license**
    - **<COLLABORATION_PLATFORM> Apps for enterprise**

Without these licenses, the new hire will not be able to complete the setup process or access the device.
