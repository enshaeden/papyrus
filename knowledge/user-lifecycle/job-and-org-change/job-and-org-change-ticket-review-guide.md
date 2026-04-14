---
id: kb-user-lifecycle-job-and-org-change-job-and-org-change-ticket-review-guide
title: Job and Org Change Ticket Review Guide
canonical_path: knowledge/user-lifecycle/job-and-org-change/job-and-org-change-ticket-review-guide.md
summary: 'Purpose:'
knowledge_object_type: runbook
legacy_article_type: runbook
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Job and Org Change Ticket Review Guide
team: IT Operations
systems:
- <TICKETING_SYSTEM>
tags: []
created: '2025-11-27'
updated: '2025-12-18'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services: []
prerequisites:
- Review the scope, approvals, and dependencies described in this article before starting.
- Confirm you have the required systems access and escalation path before proceeding.
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
- kb-user-lifecycle-job-and-org-change-index
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-user-lifecycle-job-and-org-change-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

Purpose:

Define IT actions required for <TICKETING_SYSTEM> tickets in the Job and Org change queue.

# **1. Overview**

The “ [Job and Org Change](<INTERNAL_URL>) ” <TICKETING_SYSTEM> queue requires IT review to determine whether an employee’s role, department, or employment-type change has any impact on system access or entitlements.

This queue is **not** meant to hold tickets “for compliance only.”

Ex:

Every ticket must have a **review** and a **documented action** , even if no changes are required.

## **2. Core Principle**

For every job-change ticket:

> **IT must determine whether the job change affects the user’s system access or data permissions.** If access changes are needed → document them. If no changes are needed → document that as well.

***There should never be a ticket closed without evaluation*** .

## **3. Ticket Categories & Required Actions**

Below are the official guidance categories outlined by Security (Tony Dell’Ario / SECD-5823):

### **A. Cross–Business Unit (BU) Transfers**

**Example:** Sales → Finance, Marketing → Engineering, Support → Product.

**Reason:** Different departments rely on different systems and data access.

**IT Action Required:**

- Review all access tied to the previous BU vs. new BU.
- Remove access not required for the new role.
- Ensure the user has all access needed for the new BU.

Follow instructions on [<INTERNAL_URL>](<INTERNAL_URL>)

**Closing Statement to Include:**

> *“Evaluated for access impact; adjustments made to reflect new employment/BU status.”*

### **B. Contractor ↔ Employee Transitions**

These transitions trigger:

- Different onboarding/offboarding flows
- Compliance checks
- License and entitlement changes

**IT Action Required:**

- Please refer this doc [Contractor to FTE Contractor to FTE](../employee-conversion/contractor-to-fte.md) and then close the ticket with statement as below.

Follow instructions on [<INTERNAL_URL>](<INTERNAL_URL>)

**Closing Statement:**

> *“Evaluated for access impact; adjustments made to reflect new employment/BU status.”*

### **C. Role Type / Function Changes/Title Changes**

Examples:

- IC → Manager
- Manager → IC
- Engineering → Non-engineering
- Non-sensitive → Sensitive role

**IT Action Required:**

- Quick review to determine impact.
- If no impact → close with no changes.
- If impact → document changes clearly to be updated in <TICKETING_SYSTEM> ticket.

Follow instructions on [<INTERNAL_URL>](<INTERNAL_URL>)

**Closing Statement (if no action needed):**

> *“Change reviewed against access/entitlement requirements. No action necessary.”*

### **D. All Other Job Changes**

If the change does **not** affect access, permissions, or licensing:

**IT Action Required:**

- Review the change for confirmation.
- Close the ticket with a canned note.

Follow instructions on [<INTERNAL_URL>](<INTERNAL_URL>)

**Canned Closing Statement:**

> *“Change reviewed against access/entitlement requirements. No action necessary.”*

## **4. When Access** ***Is*** **Affected**

If the review finds changes needed:

**Document clearly in the ticket:**

- What access was removed
- What access was added
- Why the change was necessary

**Example Closing Statement:**

> *“Role change requires updates to system access. Removed X, added Y, validated with manager. Access now aligned to new role.”*

## **5. When Access** ***Is Not*** **Affected**

If there is **no impact** , simply close the ticket with the approved response:

> *“Change reviewed against access/entitlement requirements. No action necessary.”*

## **7. Next Steps**

### **IT Team**

- Get review/approval from (Security team).
- Follow the process for every ticket in the queue.
- Begin reviewing and closing tickets once documentation is approved.
- Use consistent notes for compliance traceability.

## **8. Future Steps**

- Build an automation in <TICKETING_SYSTEM> to automatically close tickets once the changes have been reviewed, documented, and confirmed.
