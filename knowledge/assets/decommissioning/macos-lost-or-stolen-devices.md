---
id: kb-assets-decommissioning-macos-lost-or-stolen-devices
title: MacOS Lost or Stolen devices
canonical_path: knowledge/assets/decommissioning/macos-lost-or-stolen-devices.md
summary: Canonical article for MacOS Lost or Stolen devices imported from <KNOWLEDGE_PORTAL>.
knowledge_object_type: runbook
legacy_article_type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: MacOS Lost or Stolen devices
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- macos
created: '2025-10-03'
updated: '2026-02-17'
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
- kb-assets-decommissioning-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-decommissioning-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

1. Launch **<ENDPOINT_MANAGEMENT_PLATFORM>** and locate the stolen laptop.
  1. Use the “Lock Computer” option in the Management tab.
    2. Lock the laptop with a random 6-digit passcode.
      1. Set the Lock Message to “This asset has been reported stolen. Please contact <EMAIL_ADDRESS> .”
2. In **<ENDPOINT_MANAGEMENT_PLATFORM>** add the machine to the **Static Computer Group** : [**Stolen or Missing Laptops**](<INTERNAL_URL>)
3. In **<ENDPOINT_MANAGEMENT_PLATFORM>** change the device’s PreStage enrollments
  1. Remove the device from the [MacOS PreStage 2023](<INTERNAL_URL>)
    2. Add the device to the [Lost and Stolen PreStage](<INTERNAL_URL>)
4. Return to [Lost and Stolen devices Lost and Stolen devices](lost-and-stolen-devices.md) and complete the next steps

> INFO: The lock code generated in step 1b will be visible in the Policy History when the policy successfully runs. As a best practice, you can save a copy of the lock code in the device' <ASSET_MANAGEMENT_SYSTEM> record under “<ENDPOINT_MANAGEMENT_PLATFORM> Lock Code”
