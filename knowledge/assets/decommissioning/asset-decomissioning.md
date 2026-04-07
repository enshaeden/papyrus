---
id: kb-assets-decommissioning-asset-decomissioning
title: Asset Decomissioning
canonical_path: knowledge/assets/decommissioning/asset-decomissioning.md
summary: Decommissioning assets involves securely removing outdated or end of life equipment from active use, ensuring data is wiped and components are disposed of or recycled responsibly. This process protects sensitive...
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Asset Decomissioning
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
services:
- Endpoint Provisioning
tags:
- endpoint
created: '2025-12-16'
updated: '2026-02-26'
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
- kb-assets-decommissioning-index
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

Decommissioning assets involves securely removing outdated or end-of-life equipment from active use, ensuring data is wiped and components are disposed of or recycled responsibly. This process protects sensitive information, complies with regulatory standards, and minimizes environmental impact. Proper decommissioning safeguards organizational security and supports sustainability initiatives.

# **When to decommission a machine**

An asset may be decommissioned when it reaches the end of its lifecycle (past six years from date of purchase), is no longer operationally viable, or becomes obsolete due to technological advancements. Additionally, decommissioning is appropriate if the asset poses security risks, cannot be updated to meet compliance requirements, or is no longer cost-effective to maintain.

## **Process**

1. When a device is selected to be decommissioned, the status must be changed in <ASSET_MANAGEMENT_SYSTEM> to **Pending Decom** . This designates that it will not be reissued and needs to go through the decom process.
2. Erase the device. Ensure a secure erase is performed to remove all company data.
  1. Add a comment in <ASSET_MANAGEMENT_SYSTEM> to confirm.
3. Change status in <ASSET_MANAGEMENT_SYSTEM> to **Decommissioned**
4. In [<IDENTITY_PROVIDER> Devices](<INTERNAL_URL>) , DEACTIVATE the decommissioned asset. Confirm the Serial Number first.

### Mac Device Decommission procedures

[Mac Device Decommissioning Standard Operating Procedure (SOP) Mac Device Decommissioning Standard Operating Procedure (SOP)](mac-device-decommissioning-standard-operating-procedure-sop.md)

### Windows decommissioning procedures

[Windows Device Decommissioning Standard Operating Procedure (SOP) Windows Device Decommissioning Standard Operating Procedure (SOP)](windows-device-decommissioning-standard-operating-procedure-sop.md)

# eWasting Assets

1. Book collection from eCycle company.
2. When the device is handed over for recycle and leaves the building, change the <ASSET_MANAGEMENT_SYSTEM> status to **Recycled** .
3. Email the serial number to the Fixed Assets team to ensure it is written off following procedure below.

## **Notifying Fixed Assets Team Upon Device Recycle**

When a device is identified for decommissioning, it is essential to notify the Fixed Assets team so the asset can be appropriately written off in the company’s books of account.

### **Procedure**

1. **Gather Device Details** For each device being decommissioned, collect the following information:
  - Serial number
    - Model
2. This information should be sourced directly from the Asset Management <ASSET_MANAGEMENT_SYSTEM>.
3. **Determine Submission Format**
  - **Single device** : Include the serial number and model directly in the body of the email.
    - **Multiple devices** : Export the list from <ASSET_MANAGEMENT_SYSTEM> and attach it as a spreadsheet.
4. **Notify the Fixed Assets Team** Email the collected information to both of the following recipients:
  - Hemanth Jonnalagadda
    - Mackenzie Litts
5. Ensure both are included in the email to maintain proper recordkeeping and approval workflows.

#### **Notes**

- Notification to the Fixed Assets team should occur promptly after a decommission decision is made.
