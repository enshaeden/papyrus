---
id: kb-offboarding-employee-offboarding-checklist
title: Employee Offboarding Checklist
canonical_path: knowledge/offboarding/employee-offboarding-checklist.md
summary: Disable access, recover assets, and preserve required records when a user leaves the organization.
type: offboarding
status: active
owner: IT Operations Manager
source_type: native
team: IT Operations
systems:
  - HRIS Export
  - Endpoint Inventory
  - Google Workspace
  - Microsoft 365
  - Okta
  - Ticketing Queue
services:
  - Offboarding
  - Identity
  - Access Management
tags:
  - offboarding
  - checklist
  - account
  - endpoint
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: monthly
audience: it_ops
prerequisites:
  - Approved offboarding ticket or HRIS export with effective departure date and manager.
  - Confirmation of any legal hold, mailbox retention, or forwarding requirement.
steps:
  - Confirm the departure date and whether the termination is immediate or scheduled.
  - Disable interactive access in the identity provider at the approved time.
  - Remove or suspend mailbox, collaboration, VPN, and privileged access according to the role profile.
  - Recover assigned hardware or record the status of unrecovered assets in Endpoint Inventory.
  - Document completion, retained data decisions, and outstanding asset issues in the ticket.
verification:
  - User can no longer authenticate to the primary identity provider.
  - Asset recovery status is recorded for every assigned device.
  - Ticket captures retention or forwarding decisions approved by management.
rollback:
  - If the separation is reversed, restore access only after written approval from HR and the manager.
  - Reissue recovered hardware only after the user record is returned to active status.
related_articles:
  - kb-access-password-reset-account-lockout
  - kb-onboarding-employee-onboarding-checklist
replaced_by: null
retirement_reason: null
references:
  - title: Asset inventory record
    note: Use current inventory data when confirming device recovery status.
change_log:
  - date: 2026-04-07
    summary: Initial seed article.
    author: Repository bootstrap
---

## Notes

Immediate terminations may require concurrent security review. Do not delay access removal while waiting for hardware recovery.
