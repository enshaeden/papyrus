---
id: kb-assets-audits-and-recordkeeping-laptop-hardware-audit-helpdesk-guide
title: "Laptop Hardware Audit \u2013 Helpdesk Guide"
canonical_path: knowledge/assets/audits-and-recordkeeping/laptop-hardware-audit-helpdesk-guide.md
summary: "This guide explains how to use the Laptop Hardware Audit \u2013 FY26 <ASSET_MANAGEMENT_SYSTEM>\
  \ base to:"
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: "Laptop Hardware Audit \u2013 Helpdesk Guide"
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <TICKETING_SYSTEM>
tags:
- endpoint
- service-desk
created: '2026-02-25'
updated: '2026-02-25'
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
- kb-assets-audits-and-recordkeeping-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-audits-and-recordkeeping-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Overview

This guide explains how to use the **Laptop Hardware Audit – FY26** <ASSET_MANAGEMENT_SYSTEM> base to:

Direct Link To Master View - [Laptop Hardware Audit – FY26](<INTERNAL_URL>)

- Reconcile all laptops across:
  - <ASSET_MANAGEMENT_SYSTEM> Inventory (<COMPANY_NAME> IT Base)
    - <ENDPOINT_MANAGEMENT_PLATFORM> (Mac MDM)
    - <ENDPOINT_MANAGEMENT_PLATFORM> (Windows MDM)
    - <ENDPOINT_ENROLLMENT_PORTAL> (<ENDPOINT_ENROLLMENT_PORTAL>)
- Identify discrepancies
- Log investigation and approvals
- Formally close audit findings

This audit base is designed to:

- Provide full visibility of every unique serial number
- Automatically detect inconsistencies
- Track remediation
- Maintain evidence and approval history
- Support leadership reporting and future audits

---

# Base Architecture Overview

The base is structured into three logical layers:

## Source Layer (Read-Only Data)

These tables contain raw imported or synced data. They should **not be edited directly** .

- **Source – Inventory** (Synced from <COMPANY_NAME> IT Base)
- **Source – <ENDPOINT_MANAGEMENT_PLATFORM>**
- **Source – <ENDPOINT_MANAGEMENT_PLATFORM>**
- **Source – <ENDPOINT_ENROLLMENT_PORTAL>**

These tables exist only to:

- Provide authoritative source data
- Feed the audit logic
- Allow cross-system comparison

---

## Serial Master (System Linking Layer)

The **Serial Master** table:

- Contains one record per unique serial number
- Links all matching source records together
- Detects duplicate serials in <ENDPOINT_MANAGEMENT_PLATFORM>/<ENDPOINT_MANAGEMENT_PLATFORM>
- Acts as the central reconciliation layer

Helpdesk users do **not** need to work directly in this table.

---

## Audit Devices (Primary Working Table)

This is the main operational table.

Each record represents:

> One unique laptop serial number across all systems.

All investigation, remediation, and closure happens here.

---

## Audit Log / Evidence (Proof & Approvals)

This table stores:

- <TICKETING_SYSTEM> tickets
- <MESSAGING_PLATFORM> references
- Manager approvals
- Procurement approvals
- Written-off documentation
- Serial verification notes

Each evidence record is linked to one Audit Device.

This ensures:

- Structured audit trail
- Timestamped approvals
- No reliance on free text in the device record

---

# Understanding the Audit Devices Table

Each record contains four types of information:

---

## A. Identification

These fields confirm system alignment:

- **Serial Confirmed**
- **Source Confirmed**
- **Platform Field**
- **In Inventory**
- **In <ENDPOINT_MANAGEMENT_PLATFORM>**
- **In <ENDPOINT_MANAGEMENT_PLATFORM>**
- **In <ENDPOINT_ENROLLMENT_PORTAL>**

These fields are automated and should not be manually edited.

---

## B. Discrepancy Detection

The field:

**Discrepancy Suggested**

Indicates the current issue category:

- Missing in Inventory
- Missing in <ENDPOINT_MANAGEMENT_PLATFORM>
- Missing in <ENDPOINT_MANAGEMENT_PLATFORM>
- Missing in <ENDPOINT_ENROLLMENT_PORTAL>
- Duplicate in <ENDPOINT_MANAGEMENT_PLATFORM>
- Duplicate in <ENDPOINT_MANAGEMENT_PLATFORM>
- None / OK

This drives prioritisation.

---

## C. Review Workflow Fields (Editable by Helpdesk)

These are used to process the audit:

- **Review Status**
  - Not Started
    - In Review
    - Awaiting Info
    - Confirmed – No Action Needed
    - Record Updated
    - Written Off – Pending Approval
    - Written Off – Approved
    - Closed
- **Review Owner**
- **Located** (Checkbox)
- **Record Corrected** (Checkbox)
- **Lost / Written Off** (Single Select)

These fields reflect investigation progress and outcome.

---

## D. Closure & Governance

These fields enforce compliance:

- **Evidence Records** (Linked records)
- **Manager Approval Count**
- **Procurement Approval Count**
- **Counts Reconciled**
- **Closure Blocked Reason**

A device cannot be fully reconciled if:

- Required approvals are missing
- Evidence is not logged
- Discrepancy is unresolved

---

# How to Navigate the Audit Devices Table

## Step 1: Start with the "Needs Review" View

Filter:

- Review Status = Not Started

These are your actionable items.

---

## Step 2: Open a Record

When reviewing a device:

1. Review system presence:
  - Is it in Inventory?
    - Is it in <ENDPOINT_MANAGEMENT_PLATFORM>/<ENDPOINT_MANAGEMENT_PLATFORM>?
    - Is it in <ENDPOINT_ENROLLMENT_PORTAL>?
2. Check Inventory Status
3. Compare assigned user across systems
4. Check duplicate counts (<ENDPOINT_MANAGEMENT_PLATFORM>/<ENDPOINT_MANAGEMENT_PLATFORM> Record Count)

---

## Step 3: Determine the Issue Type

### Missing in Inventory

Device exists in MDM or <ENDPOINT_ENROLLMENT_PORTAL> but not in Inventory.

Action:

- Confirm ownership
- Confirm procurement source
- Add to Inventory if valid device
- Log evidence

---

### Missing in <ENDPOINT_MANAGEMENT_PLATFORM> / <ENDPOINT_MANAGEMENT_PLATFORM>

Device expected in MDM but not present.

Action:

- Check Inventory Status
- Confirm device location
- Re-enroll if required
- Or update Inventory status if historical

---

### Missing in <ENDPOINT_ENROLLMENT_PORTAL>

Likely:

- Older purchase
- Serial typo
- Non-<ENDPOINT_ENROLLMENT_PORTAL> procurement

Action:

- Verify serial in Inventory
- Confirm purchase history
- Log evidence

---

### Duplicate in <ENDPOINT_MANAGEMENT_PLATFORM> / <ENDPOINT_MANAGEMENT_PLATFORM>

Multiple MDM records with same serial.

Action:

- Identify active record
- Remove stale MDM object
- Confirm compliance state
- Log MDM cleanup evidence

---

# Using the Audit Log / Evidence Table

All investigation proof must be logged here.

Do NOT paste approvals directly into device notes.

---

## How to Add Evidence

From an Audit Device record:

1. Click **Add Evidence**
2. Complete:
  - Evidence Type
    - Ticket Number
    - Link
    - Approval Role (if applicable)
    - Approval Status (if applicable)
    - Notes

Evidence Types include:

- <TICKETING_SYSTEM> Ticket
- Manager Approval
- Procurement Approval
- MDM Cleanup Confirmation
- Device Return Confirmation
- Serial Verification

---

## Written Off Process

When marking a device as:

**Written Off – Pending Approval**

You must:

1. Obtain Manager approval
2. Obtain Procurement approval
3. Log both approvals as separate evidence records
4. Ensure Approval Status = Approved

Once both approvals are logged:

- Update Lost / Written Off → Written Off – Approved
- System will allow reconciliation

---

# Processing the Full Audit

Follow this structured workflow:

---

## Phase 1 – Triage

1. Work from “Needs Review” view.
2. Assign yourself as Review Owner.
3. Set Review Status → In Review.
4. Investigate discrepancy.

---

## Phase 2 – Investigation

- Confirm device location.
- Validate serial.
- Cross-check user assignment.
- Confirm MDM state.
- Update Inventory if needed.

Mark:

- Located = Yes (if known)
- Record Corrected = Yes (once fixed)

Log evidence.

---

## Phase 3 – Resolution

If issue resolved:

- Ensure Discrepancy Suggested updates to None / OK
- Confirm Counts Reconciled = Yes
- Set Review Status → Closed

If written off:

- Obtain approvals
- Log evidence
- Confirm approval counts populate
- Confirm Counts Reconciled = Yes
- Close record

---

# What “Audit Complete” Means

A device is considered fully reconciled when:

- Serial Confirmed = Confirmed
- Source Confirmed = Confirmed or N/A (historical)
- Evidence Logged = Yes (if discrepancy existed)
- Counts Reconciled = Yes
- Review Status = Closed

---

# Important Rules

- Do NOT edit source tables.
- Do NOT delete records.
- Do NOT manually override formula fields.
- Always log evidence.
- Written off devices require both Manager and Procurement approval.
- If unsure, escalate before marking resolved.

---

# Leadership Reporting

[Leadership Interface](<INTERNAL_URL>)

Leadership dashboard pulls from:

- Discrepancy Suggested
- Counts Reconciled
- Approval counts
- Review Status

Do not manually adjust these for reporting purposes.

All reporting must reflect actual data state.

---

# End of Audit

When all records show:

- Discrepancy Suggested = None / OK OR
- Lost / Written Off = Written Off – Approved AND
- Counts Reconciled = Yes

The estate is considered fully audited.
