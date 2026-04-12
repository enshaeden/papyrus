---
id: kb-assets-decommissioning-windows-device-decommissioning-standard-operating-procedure-sop
title: Windows Device Decommissioning Standard Operating Procedure (SOP)
canonical_path: knowledge/assets/decommissioning/windows-device-decommissioning-standard-operating-procedure-sop.md
summary: This document defines the standard process for securely decommissioning Windows device enrollment
  devices managed through <PRODUCTIVITY_PLATFORM> <ENDPOINT_MANAGEMENT_PLATFORM>. It ensures all company
  data is removed, devices are deregistered from management...
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Windows Device Decommissioning Standard Operating Procedure (SOP)
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- windows
created: '2025-10-31'
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

This document defines the standard process for **securely decommissioning Windows device enrollment devices** managed through <PRODUCTIVITY_PLATFORM> <ENDPOINT_MANAGEMENT_PLATFORM>. It ensures all company data is removed, devices are deregistered from management systems, and inventory remains accurate.

---

### **Scope**

This procedure applies to all **corporate-owned Windows devices** managed by <ENDPOINT_MANAGEMENT_PLATFORM> and enrolled via **Windows device enrollment** , which are being:

- Retired due to end-of-life (EOL)
- Replaced by new hardware
- Donated, resold, or permanently removed from service

---

### **Owner & Access Requirements**

- **Owner:** Single operator (Service Desk) performs all steps in this SOP.
- **Permissions:** <ENDPOINT_MANAGEMENT_PLATFORM> Administrator (or custom role with Wipe/Delete), ability to delete device objects in **<DIRECTORY_SERVICE>,** and permission to delete **Windows device enrollment** device entries.
- **Systems Used:** <ENDPOINT_MANAGEMENT_PLATFORM> admin portal, <DIRECTORY_SERVICE> admin portal, and <ASSET_MANAGEMENT_SYSTEM> (or your asset system).
- **Escalation (Only if needed):** If device is on legal hold/investigation or a wipe fails twice; otherwise proceed without additional approvals.

---

### **Prerequisites**

Before beginning:

- Confirm the device is **powered on** and connected to the Internet (if wiping remotely).
- Ensure the device is **not assigned to an active user** .
- Have **<ENDPOINT_MANAGEMENT_PLATFORM> Administrator** or **Endpoint Security Administrator** permissions.

---

### **Step-by-Step Procedure**

#### **Step 1: Perform a Wipe (Factory Reset)**

- In the **<ENDPOINT_MANAGEMENT_PLATFORM> admin portal** , navigate to:
  - **Devices → All Devices → [Select Device] → Wipe**
- Configure the following options:
  - **Do not retain enrollment state or user data.**
    - **Remove device from <ENDPOINT_MANAGEMENT_PLATFORM> after wipe** (if available).
- Confirm the action.

> ⚠️ *This permanently deletes all corporate and user data from the device and returns it to Out-of-Box Experience (OOBE).*

Wait for the wipe to complete. The status will change to *Retired* or *Removed* in <ENDPOINT_MANAGEMENT_PLATFORM>.

---

#### **Step 2: Delete Device Record from <ENDPOINT_MANAGEMENT_PLATFORM>**

After the wipe is completed, navigate to **Devices → All Devices** .

- Select the same device.
- Click **Delete** to remove its <ENDPOINT_MANAGEMENT_PLATFORM> management record.

> 💡 *This ensures <ENDPOINT_MANAGEMENT_PLATFORM> does not retain stale management objects for decommissioned hardware.*

---

#### **Step 3: Remove Device from <DIRECTORY_SERVICE>**

Open the **<DIRECTORY_SERVICE> admin portal** .

- Go to **Devices → All Devices** .
- Locate the same device name or serial number.
- Select **Delete** .

> 🧠 *Removing the device from Entra ID prevents identity duplication and future unintended re-enrollment.*

---

#### **Step 4: Deregister from device enrollment**

In the **<ENDPOINT_MANAGEMENT_PLATFORM> admin portal** , go to: **Devices → Windows Enrollment → Devices (device enrollment)**

- Search for the device by **serial number** .
- Select the device and choose **Delete** .

> ⚠️ *This unregisters the hardware hash from your tenant, ensuring the device no longer auto-enrolls in your <ENDPOINT_MANAGEMENT_PLATFORM> environment.*

---

**Step 5: Remove Serial Number From Corporate Identifier List**

After deleting the device from the device enrollment list:

- Navigate to **Devices → Windows Enrollment → Corporate Identifiers**
- Locate the device serial number and remove it.

> This ensures the device no longer has any association with corporate enrollment records.

---

#### **Step 6: Update <ASSET_MANAGEMENT_SYSTEM> Inventory (Manual Step)**

If your organization uses **<ASSET_MANAGEMENT_SYSTEM>** for device inventory tracking:

- Open the **<ASSET_MANAGEMENT_SYSTEM> Asset Management** base.
- Locate the record for the decommissioned device using the **serial number** or **asset tag.**
- Update the **Status** field to **Decommissioned** or **Disposed** .
- Add the **decommission** **date** and **IT** **approver** **name** in the respective fields.
- If required, move the record to the **Archived Devices** view or table.

📋 This step ensures your <ASSET_MANAGEMENT_SYSTEM> inventory stays synchronized with <ENDPOINT_MANAGEMENT_PLATFORM> and Entra ID for accurate asset lifecycle reporting.

---

**Step 7: Physical or Secure Disposal**

Depending on your organization’s **IT Asset Disposal (ITAD)** policy:

- Send to a **certified e-waste disposal** or **asset recovery vendor** .
- For resale or donation, verify the device **boots to the Windows OOBE screen** with **no corporate branding or configuration** .

---

### **Verification Checklist**

Before marking the device as *Decommissioned* , confirm the following:

### **System Cleanup**

- [ ] Device has been **wiped**
- [ ] Device is **deleted from <ENDPOINT_MANAGEMENT_PLATFORM>**
- [ ] Device is **removed from Entra ID**
- [ ] Device is **removed from device enrollment**
- [ ] Serial number is **removed from Corporate Identifiers**

### **Inventory Updates**

- [ ] <ASSET_MANAGEMENT_SYSTEM> record is updated to **Decommissioned/Disposed**
- [ ] **Decommission date** and **IT approver** recorded

### **Device Check**

- [ ] Device boots to **Windows OOBE**
- [ ] No corporate or user data remains

---

### **Summary: Decommissioning Actions and Purpose**

| Column 1 | Column 2 |
| --- | --- |
| Action | Purpose |
| **Wipe (Factory Reset)** | Securely erase all corporate and user data. |
| **Delete from <ENDPOINT_MANAGEMENT_PLATFORM>** | Remove from management inventory. |
| **Delete from Entra ID** | Prevent duplicate or stale directory records. |
| **Delete from device enrollment** | Deregister hardware hash and stop auto-enrollment. |
| **Update <ASSET_MANAGEMENT_SYSTEM> Inventory** | Maintain accurate asset tracking and reporting. |
| **Physical Disposal** | Complete lifecycle removal per ITAD standards. |

---

### **Notes & Best Practices**

- Always use **Wipe** (not device enrollment Reset) for decommissioning.
- Ensure **all deletions** are done in **<ENDPOINT_MANAGEMENT_PLATFORM>, Entra ID, and device enrollment** to prevent orphaned records.
- Maintain an **IT asset disposal log** with serial number, date, and disposal confirmation.
- Update **<ASSET_MANAGEMENT_SYSTEM>** immediately after device removal to maintain accurate reporting.
- For bulk decommissioning, consider automating cleanup using **PowerShell** or **<PRODUCTIVITY_PLATFORM> Graph API** .
