---
id: kb-assets-decommissioning-windows-lost-or-stolen-procedures
title: Windows Lost or Stolen Procedures
canonical_path: knowledge/assets/decommissioning/windows-lost-or-stolen-procedures.md
summary: Canonical article for Windows Lost or Stolen Procedures imported from <KNOWLEDGE_PORTAL>.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Windows Lost or Stolen Procedures
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- windows
created: '2025-12-10'
updated: '2025-12-10'
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
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

1. Launch [<ENDPOINT_MANAGEMENT_PLATFORM> admin](<INTERNAL_URL>) navigate to the [devices section](<INTERNAL_URL>) and the “All Devices” section . Find the stolen laptop per serial number that should be referenced within <ASSET_MANAGEMENT_SYSTEM>.
2. After locating the asset and communicating data loss, then proceed with the “wipe Computer” option within the Management tab.
3. Just for information purposes you will see the remote lock and reset passcode icons greyed out. This is due to the fact that this option is not available for windows devices
4. Launch the [Asset <ASSET_MANAGEMENT_SYSTEM> tracker](<INTERNAL_URL>) and search for the stolen asset by S/N
5. Mark the stolen asset as stolen within the Status field and un-assign it from the <COMPANY_NAME> employee user
  1. Place a comment within the comment section within the <ASSET_MANAGEMENT_SYSTEM> Asset Record. “This device was stolen from “Employee Name” on X date” or “This device was lost when assigned to “Employee Name” on X date”
6. Return to [Lost and Stolen devices Lost and Stolen devices](lost-and-stolen-devices.md) and complete the next steps
