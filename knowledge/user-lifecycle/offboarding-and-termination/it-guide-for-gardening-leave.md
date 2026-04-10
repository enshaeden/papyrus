---
id: kb-user-lifecycle-offboarding-and-termination-it-guide-for-gardening-leave
title: IT Guide for Gardening Leave
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/it-guide-for-gardening-leave.md
summary: 'Gardening leave is when an employee continues to receive full pay and benefits during their
  notice period but is instructed to stop performing their job responsibilities. This may occur for various
  reasons:'
knowledge_object_type: runbook
legacy_article_type: offboarding
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: IT Guide for Gardening Leave
team: Identity and Access
systems:
- <HR_SYSTEM>
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- offboarding
created: '2025-10-22'
updated: '2025-10-28'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
related_services:
- Collaboration
- Offboarding
prerequisites:
- Verify the request, identity details, and required approvals before changing access or account state.
- Confirm the target system and business context match the scope of this article.
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
- kb-user-lifecycle-offboarding-and-termination-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
- Offboarding
related_articles:
- kb-user-lifecycle-offboarding-and-termination-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## **1. What Is Gardening Leave**

Gardening leave is when an employee continues to receive full pay and benefits during their notice period but is instructed to stop performing their job responsibilities. This may occur for various reasons:

- Security or business concerns after an employee gives notice
- As a goodwill gesture during redundancy to extend benefits and pay

Employees on Gardening Leave remain on payroll and may retain some visibility (e.g., <MESSAGING_PLATFORM> presence, email forwarding) depending on HR’s request.

## **2. Types of Requirements**

Gardening Leave can be requested in various formats. IT must act based on the instructions provided by HR:

### **Scenario 1: Standard Leave with Defined Cut Date**

- HR ticket includes a specific date to cut access
- User may still occasionally need access before that date
- IT will follow standard termination procedures on the specified date

### **Scenario 2: Suspend Access with Flexibility**

- HR requests access be cut but not fully deactivated in <IDENTITY_PROVIDER>
- This allows for potential reinstatement of access if tasks arise

### **Scenario 3: Covert Leave (<MESSAGING_PLATFORM> Presence Maintained)**

- HR requests access removal without making it clear that the employee has left
- <MESSAGING_PLATFORM> presence and email should remain operational
- IT will be contacted directly by HR for this configuration

## **3. <IDENTITY_PROVIDER> & <ENDPOINT_MANAGEMENT_PLATFORM> Process**

### **Scenario 1: Standard Termination Procedure**

- On the specified date, follow the usual termination checklist

### **Scenario 2: Suspend Only**

- Clear all <IDENTITY_PROVIDER> sessions
- Suspend the <IDENTITY_PROVIDER> account
- Do not lock the device in <ENDPOINT_MANAGEMENT_PLATFORM> until the final termination date

### **Scenario 3: Covert Access Cut**

- Clear user sessions in <IDENTITY_PROVIDER>
- Remove all MFA devices
- Reset <IDENTITY_PROVIDER> password using a temporary password and ensure sign-out
- Lock the laptop via <ENDPOINT_MANAGEMENT_PLATFORM>
- Do **not** deactivate the <MESSAGING_PLATFORM> account
- Do **not** disable email access unless explicitly told

## **4. Cross-Team Impacts**

- **IT:** De-provision access immediately upon Leave entry
- **HR Ops:** Coordinates dates for:
  - Garden Leave start and end
    - Last day worked vs. first day on leave
    - Estimated termination date
- **Termination Alignment:**
  - Last Day Worked = Leave Start Date
    - Paid Through Date = Termination Date

## **5. Open Questions and Resolutions**

**Q: How much access should be removed upon being placed on leave?** *A: <IDENTITY_PROVIDER> account should be suspended unless directed otherwise by HR. Use the “suspend with leave, deactivate with term” model.*

**Resolved Clarification:**

- If Garden Leave is entered but the term date is undetermined, access must still be cut and equipment collected immediately. The same system notifications apply as if processing a termination.
