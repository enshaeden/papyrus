---
id: kb-assets-loaners-loaner-laptop-policy
title: Loaner Laptop Policy
canonical_path: knowledge/assets/loaners/loaner-laptop-policy.md
summary: The purpose of this policy is to establish a standardized procedure for providing temporary loaner laptops to employees whose primary work devices are experiencing hardware related issues. This ensures business...
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Loaner Laptop Policy
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
services:
- Endpoint Provisioning
tags:
- endpoint
created: '2025-12-11'
updated: '2025-12-11'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
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
related_articles:
- kb-assets-loaners-index
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

# **1. Purpose**

The purpose of this policy is to establish a standardized procedure for providing temporary loaner laptops to employees whose primary work devices are experiencing hardware-related issues. This ensures business continuity and minimizes downtime.

# **2. Objective**

The primary objective is to make a loaner laptop available and have the affected employee "up and running" with their work within **30 minutes** of confirming a hardware issue, provided the employee is physically present in the office.

# **3. Scope**

This policy applies to all full-time employees and contractors who are assigned a company-owned laptop for their work duties. It is strictly limited to instances of confirmed hardware failure or critical hardware maintenance.

# **4. Loaner Laptop Provision Procedure**

If, during the course of normal troubleshooting, it becomes apparent that the user will need a replacement device and one is not immediately available:

1. **Create a linked ticket:** Create a ticket, linked to the original, to track the loan out of the device. Set the due date as the expected date of return (based on receipt of their replacement device)
2. **Assign the Loaner** : Using the <ASSET_MANAGEMENT_SYSTEM> for Loaner devices, allocate the device in the system. Note, it is a best practice to confirm you physically have the device before making allocations.
  1. Set to “Reserved for Loan” if the user will not be picking the device up immediately.
    2. Set to “Deployed” if the user will take it right away
3. **Provide Loaner Laptop:** Keep the laptop in a secure location until the user is able to retrieve the device. Ensure the user is able to log in before they leave.

# Locations and Access procedures

## <REGION_A>

[<REGION_A> Loaner Location and Access for Remote Support <REGION_A> Loaner Location and Access for Remote Support](region-a-loaner-location-and-access-for-remote-support.md)

## **4.2. Loaner Laptop Tracking and Inventory**

Track issued loaners in <ASSET_MANAGEMENT_SYSTEM> using the standard inventory workflow.

The following steps should be moved to the above linked page when available:

The IT Team is responsible for diligently tracking the loaner laptop inventory:

| **Step** | **Action** | **Tool/System** |
| --- | --- | --- |
| 1 | Update Laptop Status | <ASSET_MANAGEMENT_SYSTEM> |
| 2 | Record User and Issue | <ASSET_MANAGEMENT_SYSTEM> |
| 3 | Note Loan-out Date | <ASSET_MANAGEMENT_SYSTEM> |
| 4 | Note Expected Return Date | <ASSET_MANAGEMENT_SYSTEM> |

# Device allocations
