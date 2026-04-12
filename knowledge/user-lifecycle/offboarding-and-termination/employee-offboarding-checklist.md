---
id: kb-offboarding-employee-offboarding-checklist
title: Employee Offboarding Checklist
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/employee-offboarding-checklist.md
summary: Disable access, recover assets, and preserve required records when a user leaves the organization.
knowledge_object_type: runbook
legacy_article_type: offboarding
object_lifecycle_state: active
owner: it_operations
source_type: native
source_system: repository
source_title: Employee Offboarding Checklist
team: IT Operations
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <COLLABORATION_PLATFORM>
- <HR_SYSTEM>
- <IDENTITY_PROVIDER>
- <TICKETING_SYSTEM>
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
related_services:
- Offboarding
- Identity
- Access Management
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
citations:
- article_id: null
  source_title: Asset inventory record
  source_type: document
  source_ref: Asset inventory record
  note: Use current inventory data when confirming device recovery status.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-user-lifecycle-offboarding-and-termination-index
- kb-access-password-reset-account-lockout
- kb-onboarding-employee-onboarding-checklist
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Offboarding
- Identity
- Access Management
related_articles:
- kb-user-lifecycle-offboarding-and-termination-index
- kb-access-password-reset-account-lockout
- kb-onboarding-employee-onboarding-checklist
references:
- title: Asset inventory record
  note: Use current inventory data when confirming device recovery status.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
- date: 2026-04-07
  summary: Moved the checklist into the user-lifecycle offboarding collection to consolidate lifecycle content.
  author: codex
---

## Notes

Immediate terminations may require concurrent security review. Do not delay access removal while waiting for hardware recovery.
