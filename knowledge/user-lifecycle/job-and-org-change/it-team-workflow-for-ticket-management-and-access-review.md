---
id: kb-user-lifecycle-job-and-org-change-it-team-workflow-for-ticket-management-and-access-review
title: IT Team Workflow for Ticket Management and Access Review
canonical_path: knowledge/user-lifecycle/job-and-org-change/it-team-workflow-for-ticket-management-and-access-review.md
summary: 'Choose one category:'
type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: IT Team Workflow for Ticket Management and Access Review
team: Identity and Access
systems:
- <TICKETING_SYSTEM>
services:
- Access Management
tags:
- account
- access
created: '2025-12-18'
updated: '2025-12-18'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
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
related_articles:
- kb-user-lifecycle-job-and-org-change-index
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

## **Workflow for the IT Team**

### **Step 1 —** [**Pick a Ticket From the Queue**](<INTERNAL_URL>)

- Ensure to sync the user details from [<HR_SYSTEM> → <IDENTITY_PROVIDER>](<INTERNAL_URL>)
- Confirm the nature of the job change.

### **Step 2 — Review Access**

- Cross-check entitlements in:
  - [<IDENTITY_PROVIDER> admin portal](<INTERNAL_URL>)
    - All SaaS apps (Where-ever applicable)
    - [<COLLABORATION_PLATFORM> admin portal](<INTERNAL_URL>)
    - Department-level access (shared drives, internal tools)

### **Step 3 — Determine Impact**

Choose one category:

- BU Transfer
- [Contractor to FTE Contractor ↔ Employee transition](../employee-conversion/contractor-to-fte.md)
- Role type change
- Other / No-Impact change

### **Step 4 — Take Action**

- Update or remove access **if needed** .
- If no action required, document review and close.

### **Step 5 — Add the Correct Closing Statement**

- Add an applicable closing statement as per the Job and Org change type ((From the canned list above.)

### **Step 6 — Close the Ticket**

- Ensure proper notes are added.
- Link the ticket to related onboarding/offboarding tasks if needed.
