---
id: kb-access-software-access-request
title: Software and Access Request
canonical_path: knowledge/access/software-access-request.md
summary: Review and fulfill routine software installation and entitlement requests through an auditable approval workflow.
type: access
status: active
owner: Service Desk Lead
source_type: native
team: Service Desk
systems:
  - Okta
  - Google Workspace
  - Microsoft 365
  - Ticketing Queue
services:
  - Access Management
tags:
  - access
  - service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: service_desk
prerequisites:
  - Request ticket identifies the software or entitlement being requested.
  - Manager approval is attached if the request affects licensed, privileged, or restricted access.
  - The requester is a valid active user in the identity system.
steps:
  - Confirm the requested software or group is part of the supported catalog and identify whether approval is required.
  - Validate the requester and cost center information against the ticket and current user record.
  - Apply the software deployment or entitlement change through the approved admin workflow.
  - Record the approval source, license impact, and fulfillment action in the ticket before closure.
  - Redirect out-of-catalog requests to the owning team if the service desk is not authorized to grant them.
verification:
  - User can see or use the newly granted application or group membership.
  - Ticket includes the approval record and exact entitlement granted.
  - License counts or seat usage were reviewed when applicable.
rollback:
  - Remove the granted entitlement if the wrong group or software package was assigned.
  - Notify the requester and manager if the access must be rolled back due to licensing or policy constraints.
related_articles:
  - kb-access-password-reset-account-lockout
  - kb-onboarding-employee-onboarding-checklist
replaced_by: null
retirement_reason: null
references:
  - title: Onboarding checklist
    article_id: kb-onboarding-employee-onboarding-checklist
    path: knowledge/onboarding/employee-onboarding-checklist.md
    note: Use this when the request is part of a new hire setup rather than an ad hoc access change.
change_log:
  - date: 2026-04-07
    summary: Initial seed article.
    author: Repository bootstrap
---

## Notes

Do not grant privileged access outside the documented approval path. Escalate restricted requests to the system owner when the entitlement is not clearly pre-approved.
