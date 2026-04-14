---
id: kb-assets-acquisition-windows-device-lifecycle
title: Windows Device Lifecycle
canonical_path: knowledge/assets/acquisition/windows-device-lifecycle.md
summary: "This document outlines the complete workflow for managing Windows devices at <COMPANY_NAME>\u2014\
  from the moment a device arrives from the vendor, through onboarding and reassignment, to eventual decommissioning.\
  \ This ensures..."
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Windows Device Lifecycle
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- windows
created: '2025-11-26'
updated: '2025-12-01'
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
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

This document outlines the complete workflow for managing **Windows devices** at <COMPANY_NAME>—from the moment a device arrives from the vendor, through onboarding and reassignment, to eventual decommissioning. This ensures consistent handling, security compliance, and accurate asset tracking across all systems.

---

## **1. Device Arrival From Vendor**

When a new Windows device arrives at the office:

[Receiving a new Windows device Receiving a new Windows device](receiving-a-new-windows-device.md)

---

## **2. Importing Device Into <ENDPOINT_MANAGEMENT_PLATFORM> (device enrollment Enrollment)**

device enrollment - Windows Device Enrollment - Admin Guide device enrollment - Windows Device Enrollment - Admin Guide

---

## **3. Device Setup for a New Hire or Existing User**

- Configure and stage the device according to device provisioning standards.
- Confirm required apps and configuration profiles are assigned.
- Update <ASSET_MANAGEMENT_SYSTEM>:
  - Change status to **Assigned**
    - Add user’s name
- Add device details to the user’s <TICKETING_SYSTEM> onboarding ticket.

---

## **4. Moving Device Between Users**

When a Windows device is being reassigned:

- Perform an **device enrollment Reset or Wipe** to clear user data and restore a fresh, compliant configuration.
- Reassign the device to the new user.
- Update <ASSET_MANAGEMENT_SYSTEM>:
  - Change assigned user
    - Add the date of the transfer
    - Add comments regarding wipe/reset
- Ensure new device enrollment assignment is correct before handing out the device.

---

## **5. Decommissioning a Windows Device**

[Windows Device Decommissioning Standard Operating Procedure (SOP) Windows Device Decommissioning Standard Operating Procedure (SOP)](../decommissioning/windows-device-decommissioning-standard-operating-procedure-sop.md)

---

## **6. Summary of Required Updates Across Systems**

| Step | <ASSET_MANAGEMENT_SYSTEM> | <ENDPOINT_MANAGEMENT_PLATFORM> Device List | device enrollment | Corporate Identifier |
| --- | --- | --- | --- | --- |
| New device arrives | Add device | — | — | Add serial number |
| Before onboarding | Update status, assign user | Device appears after enrollment | Import via SOP | Already added |
| Device reassignment | Update user + notes | Reset/Wipe | Confirm group | No change |
| Decommission | Mark as retired | Remove device | Remove record | Remove serial number |
