---
id: kb-user-lifecycle-offboarding-and-termination-obtaining-assets-from-terminated-users
title: Obtaining Assets from Terminated Users
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/obtaining-assets-from-terminated-users.md
summary: To ensure best practices, security, and compliance, it is essential to retrieve assets from terminated
  employees. Please follow this procedure to facilitate the return of these assets.
knowledge_object_type: runbook
legacy_article_type: offboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Obtaining Assets from Terminated Users
team: IT Operations
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <HR_SYSTEM>
tags:
- endpoint
- offboarding
created: '2026-02-17'
updated: '2026-02-26'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services:
- Endpoint Provisioning
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
  source_ref: docs/migration/seed-migration-rationale.md
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
- Endpoint Provisioning
- Offboarding
related_articles:
- kb-user-lifecycle-offboarding-and-termination-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

To ensure best practices, security, and compliance, it is essential to retrieve assets from terminated employees. Please follow this procedure to facilitate the return of these assets.

# Monitor the [Terminations View](<INTERNAL_URL>)

- Employees automatically appear here when they have a device assigned, and their termination date is added or their status is changed to **Deprovisioned** .
- The team also receives an alert in the **it-<APPLICATION_CATALOG>-updates** <MESSAGING_PLATFORM> channel when a new employee enters the view.
- The trigger for this is either that their **Termination Date** is added or their status changed to **Deprovisioned** while still having devices assigned to them.
- If the termination was triggered by a <TICKETING_SYSTEM> ticket, the ticket will be automatically linked to the employee record in <ASSET_MANAGEMENT_SYSTEM> via the **<TICKETING_SYSTEM> Ticket #** field.
- Use the **<TICKETING_SYSTEM> Ticket Status** and **Open In <TICKETING_SYSTEM>** fields for quick access and tracking.
- These are auto-assigned using the **Auto Add Term Ticket** automation, which extracts the Employee ID from the <TICKETING_SYSTEM> summary.
- In [<IDENTITY_PROVIDER> Devices](<INTERNAL_URL>) , SUSPEND the terminated user’s asset(s). Confirm the Serial Number(s) first.

> INFO: If a user is marked as “Deprovisioned” and the termination date field is empty then a message is sent to the [<QUEUE_NAME>](<INTERNAL_URL>) channel requesting the team to manually add the term date.

# **Verify the Collection Handler is assigned**

1. This should occur automatically when:
  1. TERM - ASSET RETURN tickets are assigned to a technician
2. If the automation fails, find the **Collection Handler** field in <ASSET_MANAGEMENT_SYSTEM> and manually assign it to match the ticket owner

# **Confirm the Return**

1. When a user confirms the return of their device:
  - Check the **Hold Chase Emails** box in <ASSET_MANAGEMENT_SYSTEM> to stop further automated emails and avoid escalation.
    - Update the **Notes** field with any specifics given by the user. Including dates of expected return

# **Inspect the Device**

1. When the device is physically received:
  - Inspect it for damage.
    - Verify the serial number matches the <ASSET_MANAGEMENT_SYSTEM> record.
    - Add the <ASSET_MANAGEMENT_SYSTEM> **Asset Number** to the device for easier future identification.

---

# **Automations and Communication**

1. Users are automatically emailed return instructions via an <ASSET_MANAGEMENT_SYSTEM> automation:
  1. *Cadence and verbiage for all emails can be found here -* [<INTERNAL_URL>](<INTERNAL_URL>)
      1. Instructions vary by location and include specific details for returning the device.
          2. Emails are sent every 7 days until the device is returned or 4 weeks pass.
          3. After 4 weeks, the case escalated to Keith.
    2. Users are instructed to reply to Service Desk, creating a ticket for the return process.
      - IT team members must add updates or user responses to the **Notes** field in <ASSET_MANAGEMENT_SYSTEM> for visibility.
