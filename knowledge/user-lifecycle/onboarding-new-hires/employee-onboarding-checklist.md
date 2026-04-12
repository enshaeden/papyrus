---
id: kb-onboarding-employee-onboarding-checklist
title: Employee Onboarding Checklist
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/employee-onboarding-checklist.md
summary: Coordinate endpoint, identity, and communications tasks required before a new hire starts.
knowledge_object_type: runbook
legacy_article_type: onboarding
object_lifecycle_state: active
owner: it_operations
source_type: native
source_system: repository
source_title: Employee Onboarding Checklist
team: IT Operations
systems:
- <COLLABORATION_PLATFORM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
- <HR_SYSTEM>
- <IDENTITY_PROVIDER>
- <TICKETING_SYSTEM>
tags:
- onboarding
- checklist
- endpoint
- account
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: monthly
audience: it_ops
related_services:
- Onboarding
- Endpoint Provisioning
- Identity
- Access Management
prerequisites:
- HRIS export or approved hiring ticket with start date and manager.
- Approved role profile or baseline application set for the new hire.
steps:
- Create or verify the ticket as soon as the HRIS export lands and confirm the manager, start date, and
  office location.
- Create the identity account and baseline groups through the approved onboarding workflow.
- Prepare the laptop and peripherals using the laptop provisioning runbook.
- Confirm mailbox, collaboration, and MFA readiness at least one business day before the start date.
- Record all completion details in the onboarding ticket and hand off exceptions to the manager before
  the start date.
verification:
- Identity account can authenticate and required groups are in place.
- Device is ready for pickup or shipment and inventory has been updated.
- Ticket shows a complete record of completed and pending tasks.
rollback:
- Disable or delay account activation if the start date changes or the hire is cancelled.
- Return prepared equipment to unassigned inventory if the onboarding request is withdrawn.
citations:
- article_id: kb-runbooks-laptop-provisioning
  source_title: Laptop provisioning runbook
  source_type: document
  source_ref: knowledge/runbooks/laptop-provisioning.md
  note: Use this runbook to complete the hardware preparation task.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-user-lifecycle-onboarding-new-hires-index
- kb-runbooks-laptop-provisioning
- kb-access-software-access-request
- kb-offboarding-employee-offboarding-checklist
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Onboarding
- Endpoint Provisioning
- Identity
- Access Management
related_articles:
- kb-user-lifecycle-onboarding-new-hires-index
- kb-runbooks-laptop-provisioning
- kb-access-software-access-request
- kb-offboarding-employee-offboarding-checklist
references:
- title: Laptop provisioning runbook
  article_id: kb-runbooks-laptop-provisioning
  path: knowledge/runbooks/laptop-provisioning.md
  note: Use this runbook to complete the hardware preparation task.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
- date: 2026-04-07
  summary: Moved the checklist into the user-lifecycle onboarding collection to consolidate lifecycle content.
  author: codex
---

## Notes

This checklist is intended for standard employee onboarding. Contractor onboarding may require a separate approval and provisioning path.
