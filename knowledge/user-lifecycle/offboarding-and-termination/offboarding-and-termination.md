---
id: kb-user-lifecycle-offboarding-and-termination-offboarding-and-termination
title: Offboarding and Termination
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/offboarding-and-termination.md
summary: This SOP defines how IT handles user access removal and asset retrieval when someone leaves the
  company, distinguishing between Immediate and Scheduled terminations and outlining SLAs and checklist
  items.
knowledge_object_type: runbook
legacy_article_type: offboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Offboarding and Termination
team: Identity and Access
systems:
- <HR_SYSTEM>
tags:
- offboarding
created: '2025-10-15'
updated: '2026-03-04'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
related_services:
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

This SOP defines how IT handles [user access removal](<INTERNAL_URL>) and [asset retrieval](<INTERNAL_URL>) when someone leaves the company, distinguishing between **Immediate** and **Scheduled** terminations and outlining SLAs and checklist items.

---

# **Termination Type**

Termination falls into two categories; although the processes are identical, their SLAs differ.

To ensure proper and complete termination, IT team members must use the [Termination Checklist](<INTERNAL_URL>) for every termination ticket.

## **Immediate term**

The HR team will notify all immediate terminations via the <MESSAGING_PLATFORM> channel [<QUEUE_NAME>](<INTERNAL_URL>) . This includes contractors and FTE terminations (e.g., when an employee leaves without prior notice and HR later learns of the resignation).

**Immediate terminations occur at the moment of notice and have P0 priority, requiring acknowledgment within 5 minutes and resolution within 15 minutes.**

## **Scheduled term**

Once the HR team enters and finalizes termination details in **<HR_SYSTEM>** before the employee’s termination date a backend automation triggers a **<TICKETING_SYSTEM> ticket** for the Helpdesk team **seven days before the target date** . This ticket routes automatically to the [**Open Offboarding queue**](<INTERNAL_URL>) in <TICKETING_SYSTEM>, where the appropriate regional team can act and follow up.

Scheduled terminations occur at 17:00 local time on the termination day unless HR or Legal notifies otherwise.

---

# **Termination Checklist (Access)**

Locate the TERM ticket in [Open Offboarding queue](<INTERNAL_URL>) , then copy and paste this checklist into the comments and update as you complete each action.

> INFO: **Mandatory:**
>
> [] [Termination Checklist Action items <IDENTITY_PROVIDER>](termination-checklist-action-items.md) - Reset access and deactivate
>
> [] [Termination Checklist Action items <PRODUCTIVITY_PLATFORM>](termination-checklist-action-items.md) - Revoke Office licenses
>
> [] [Termination Checklist Action items <PASSWORD_MANAGER>](termination-checklist-action-items.md) - Suspend or verify no account
>
> **Verification (or action if necessary):**
>
> [] [Termination Checklist Action items <COLLABORATION_PLATFORM>](termination-checklist-action-items.md) - Verify “Suspended” status
>
> [] [Termination Checklist Action items <VIDEO_CONFERENCING_PLATFORM>](termination-checklist-action-items.md) - Verify “deactivated”
>
> [] [Termination Checklist Action items <ENDPOINT_MANAGEMENT_PLATFORM>](termination-checklist-action-items.md) - Verify device “lock” command sent
>
> **For WPS (make a separate ticket and link):**
>
> [] Disable KeyCard Building Access
>
> **P&E Terms:**
>
> [] [Termination Checklist Action items <BUSINESS_APPLICATION_B> and <COMPANY_NAME> Test](termination-checklist-action-items.md)
>
> **<REGION_D> Only:**
>
> [] [Termination Checklist Action items Remove Mobile Data](termination-checklist-action-items.md)
>
> **Upon request:**
>
> [] Setup Mail Forwarding

---

# **Termed Asset retrieval**

After the account termination process, follow the standard regional asset retrieval process for all locations. **Make sure to link the TERM - ASSET RETURN TICKET to the corresponding TERM ticket.**

[Obtaining Assets from Terminated Users Obtaining Assets from Terminated Users](obtaining-assets-from-terminated-users.md)

The asset return ticket can be closed once the asset has been received from the terminated user.

## Determine asset “Hold” Status

A termination hold secures, recovers, and processes assigned assets per the organization’s policies. It prevents asset loss or misuse and ensures secure data management. If a user/asset is flagged for hold, make sure to follow the linked process below.

Notifications that a device has been placed on term hold will come through [<QUEUE_NAME>](<INTERNAL_URL>) and a corresponding Device Status field will be updated to reflect the Term Hold.

[Asset Term Hold Process Asset Term Hold Process](asset-term-hold-process.md)

---

# Reference

[Termination Checklist Action items Termination Checklist Action items](termination-checklist-action-items.md)

**Enterprise Apps** Termination Ticket Logic Termination Ticket Logic
