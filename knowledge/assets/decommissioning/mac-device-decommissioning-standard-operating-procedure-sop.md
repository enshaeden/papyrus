---
id: kb-assets-decommissioning-mac-device-decommissioning-standard-operating-procedure-sop
title: Mac Device Decommissioning Standard Operating Procedure (SOP)
canonical_path: knowledge/assets/decommissioning/mac-device-decommissioning-standard-operating-procedure-sop.md
summary: This document defines the standard process for securely decommissioning Mac devices managed through
  <ENDPOINT_MANAGEMENT_PLATFORM> and <ENDPOINT_ENROLLMENT_PORTAL>. It ensures all company data is removed,
  devices are deregistered from management...
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Mac Device Decommissioning Standard Operating Procedure (SOP)
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- macos
created: '2025-12-16'
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

### **Purpose**

This document defines the standard process for **securely decommissioning Mac devices** managed through <ENDPOINT_MANAGEMENT_PLATFORM> and <ENDPOINT_ENROLLMENT_PORTAL>. It ensures all company data is removed, devices are deregistered from management systems, and inventory remains accurate.

**Decommissioning should only be done within 14 days of the device physically leaving our possession.**

This prevents us from decommissioning a device too soon if the device is needed elsewhere.

**Under no circumstances** can a device be removed from <ENDPOINT_MANAGEMENT_PLATFORM> while it is **Deployed,** under **Legal Hold** or under any **Term Hold** status. Removing a device from <ENDPOINT_MANAGEMENT_PLATFORM> under these statuses is a severe breach of policy.

If all <ENDPOINT_MANAGEMENT_PLATFORM> licenses are used up and more are needed, **discuss with leadership first** . Then ensure that only devices that are marked as **Decommissioned** or **Recycled** are removed from <ENDPOINT_MANAGEMENT_PLATFORM> to free up licenses.

---

### **Scope**

This procedure applies to all **corporate-owned Mac devices** managed by <ENDPOINT_MANAGEMENT_PLATFORM> and enrolled via **<ENDPOINT_ENROLLMENT_PORTAL>** , which are to be:

- Retired due to end-of-life (EOL)
- Replaced by new hardware
- Donated, resold, or permanently removed from service

---

### **Owner & Access Requirements**

- **Owner:** Single operator (Service Desk) performs all steps in this SOP.
- **Permissions:** **<ENDPOINT_MANAGEMENT_PLATFORM>** Administrator (or custom role with Wipe/Delete) and permission to Release devices in **<ENDPOINT_ENROLLMENT_PORTAL>**
- **Systems Used:** <ENDPOINT_MANAGEMENT_PLATFORM>, <ENDPOINT_ENROLLMENT_PORTAL>, and <ASSET_MANAGEMENT_SYSTEM> (or your asset system).
- **Escalation (Only if needed):** If device is on legal hold/investigation or a wipe fails twice; otherwise proceed without additional approvals.

---

### **Prerequisites**

Before beginning:

- Ensure the device is **not assigned to an active user** and has been determined that <COMPANY_NAME> has no use for it.
- Have **<ENDPOINT_MANAGEMENT_PLATFORM> Admin (delete)** or **<ENDPOINT_ENROLLMENT_PORTAL> (device enrollment manager)** permissions.

---

### **Step-by-Step Procedure**

Recommended to follow steps completely for a single device and then start over to ensure no step is missed.

#### **Step 1: Record Info for Decom Process**

- In **<ENDPOINT_MANAGEMENT_PLATFORM>** , search for serial number to open device record
- Record the following details:
  - **Lock Code**
    - **Encryption Key**
- Best to record this info in the sheet that will be provided to vendor
- Critical to record this info before deleting device from <ENDPOINT_MANAGEMENT_PLATFORM> or <ENDPOINT_ENROLLMENT_PORTAL>

#### **Step 2: Perform a Wipe (Factory Reset)**

- Boot device and enter unique lock code retrieved from <ENDPOINT_MANAGEMENT_PLATFORM>
  - Devices returned from term will have a lock code on them that needs to be entered to access anything
    - Non-term devices would not have a lock code and you can proceed
- Boot into recovery mode on Mac.
  - For Intel based devices, hold Command + R when booting up
    - For ARM-based Mac hardware, when device is off, hold power button until Recovery Mode loads
- Choose Forgot All Passwords and enter Recovery Key retrieved from <ENDPOINT_MANAGEMENT_PLATFORM> in previous steps
- Continue to Disk Utility, select Drive, and Erase

---

#### **Step 3: Delete Device Record from <ENDPOINT_MANAGEMENT_PLATFORM>**

After the wipe is completed, navigate to **<ENDPOINT_MANAGEMENT_PLATFORM> → Search Inventory ->Enter serial number**

- Select the device
  - If you kept page open from retrieving the code and key, easy to return to the page.
- Click **Delete** in the bottom right to remove from <ENDPOINT_MANAGEMENT_PLATFORM>

---

#### **Step 4: Remove Device <ENDPOINT_ENROLLMENT_PORTAL>**

Open **<ENDPOINT_ENROLLMENT_PORTAL>** in a browser.

- Go to **Devices** and enter serial number for device in search box
- Click on the device then the three dots in the top right
- If you see Turn Off Activation Lock, click this option to remove before proceeding.
  - Unlikely this would be enabled but some devices do have it
- Click Release from Organization

---

#### **Step 5: Update <ASSET_MANAGEMENT_SYSTEM> Inventory (Manual Step)**

- Open the **<ASSET_MANAGEMENT_SYSTEM> Asset Management** base.
- Locate the record for the decommissioned device using the **serial number** or **asset tag.**
- Update the **Status** field to **Decommissioned** .
  - Once the device has been physically removed from our possession, update **Status** to **Recycled**
- Add the **decommission** **date** and **IT** **approver** **name** in the respective fields.
- If required, move the record to the **Archived Devices** view or table.

---

**Step 8: Physical or Secure Disposal**

Depending on your organization’s **IT Asset Disposal (ITAD)** policy:

- Send to a **certified e-waste disposal** or **asset recovery vendor** .
  - Primary vendor is HOBI

---

### **Verification Checklist**

Before marking the device as *Decommissioned* , confirm the following:

### **System Cleanup**

- [ ] Lock code and encryption key have been recorded outside of <ENDPOINT_MANAGEMENT_PLATFORM>
- [ ] Device has been **wiped**
- [ ] Device is **deleted from <ENDPOINT_MANAGEMENT_PLATFORM>**
- [ ] Device is **Removed from Org. in <ENDPOINT_ENROLLMENT_PORTAL>**

### **Inventory Updates**

- [ ] <ASSET_MANAGEMENT_SYSTEM> record is updated to **Decommissioned**
- [ ] **Decommission date** and **IT approver** recorded

### **Device Check**

- [ ] Device boots to **Welcome to your new Mac**
- [ ] No corporate or user data remains by clicking through setup past the Remote Management screen

---

### **Summary: Decommissioning Actions and Purpose**

| Column 1 | Column 2 |
| --- | --- |
| Action | Purpose |
| **Wipe (Factory Reset)** | Securely erase all corporate and user data. |
| **Delete from <ENDPOINT_MANAGEMENT_PLATFORM>** | Remove from MDM and frees license |
| **Delete from <ENDPOINT_ENROLLMENT_PORTAL>** | Release ownership of device for resale/reuse |
| **Update <ASSET_MANAGEMENT_SYSTEM> Inventory** | Maintain accurate asset tracking and reporting. |
| **Physical Disposal** | Complete lifecycle removal per ITAD standards. |

---

### **Notes & Best Practices**

- Decommissioning should only be done **within 14 days of the device physically leaving our possession.**
- Following steps for a single device completely helps keep us accurate
- Maintain an **IT asset disposal log** with serial number, date, and disposal confirmation.
- Update **<ASSET_MANAGEMENT_SYSTEM>** immediately after device removal to maintain accurate reporting.
- See nested items below.
