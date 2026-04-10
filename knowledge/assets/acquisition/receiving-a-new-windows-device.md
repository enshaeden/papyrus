---
id: kb-assets-acquisition-receiving-a-new-windows-device
title: Receiving a new Windows device
canonical_path: knowledge/assets/acquisition/receiving-a-new-windows-device.md
summary: "For details on how to import Windows devices into <ENDPOINT_MANAGEMENT_PLATFORM> using device\
  \ enrollment , please refer to the admin guide here: device enrollment \u2013 Windows Device Enrollment\
  \ \u2013 Admin Guide device enrollment Windows Device Enrollment Admin Guide..."
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Receiving a new Windows device
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- windows
created: '2025-11-26'
updated: '2025-11-26'
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
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-assets-acquisition-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-acquisition-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Add the Device to <ASSET_MANAGEMENT_SYSTEM> Inventory**

1. Log the new Windows device in **<ASSET_MANAGEMENT_SYSTEM>** under the hardware inventory using [Add New Asset Form](<INTERNAL_URL>) .
2. Include all required details such as model, serial number, status, and assigned user (if applicable).

# **Add the Serial Number in <ENDPOINT_MANAGEMENT_PLATFORM>**

1. In <ENDPOINT_MANAGEMENT_PLATFORM>, go to: **Devices → Enrollment → Corporate Device Identifiers**
  - Add the device **serial number** under the *Corporate Identifier* section so it is recognized as a corporate-owned device.

For details on **how to import Windows devices into <ENDPOINT_MANAGEMENT_PLATFORM> using device enrollment** , please refer to the admin guide here: **device enrollment – Windows Device Enrollment – Admin Guide** device enrollment - Windows Device Enrollment - Admin Guide device enrollment - Windows Device Enrollment - Admin Guide
