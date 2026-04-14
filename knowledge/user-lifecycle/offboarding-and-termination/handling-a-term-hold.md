---
id: kb-user-lifecycle-offboarding-and-termination-handling-a-term-hold
title: Handling a Term Hold
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/handling-a-term-hold.md
summary: 'Devices in Term Hold will trigger:'
knowledge_object_type: runbook
legacy_article_type: offboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Handling a Term Hold
team: IT Operations
systems:
- <HR_SYSTEM>
tags:
- offboarding
created: '2025-11-26'
updated: '2025-11-26'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
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

# **Change the Device Status to Term Hold**

1. Update the device’s **Status** field to the appropriate **Term Hold** status based on the terminated user’s role:
  - Via an automation, this action will automatically:
      - Remove the assignee from the device.
          - Assign the device to the IT Team.
2. Once all devices assigned to the user have been processed, tick the **Completed** checkbox in the **Terminations** view:
  - This removes the employee from the **Terminations** view.
    - This action will mark that the member of the IT Team who ticked completed is accountable for the changes made to the devices returned.
3. In [<IDENTITY_PROVIDER> Devices](<INTERNAL_URL>) , DEACTIVATE the returned asset. Confirm the Serial Number first.

---

# **Track the Term Hold Period**

Devices in **Term Hold** will trigger:

1. A confirmation message in the **it-<APPLICATION_CATALOG>-updates** <MESSAGING_PLATFORM> channel.
2. A Term Hold reminder added to the **IT Term Reminders** calendar.

---

# **Process the Device After Term Hold**

Once the Term Hold cycle ends:

1. Change the device’s **Status** to **Needs Setup or Erase** .
2. Erase the device, ensuring all data is wiped.
3. Update the device to the latest version of its OS
4. Clean the device thoroughly and update its **Status** to **Ready To Give** for redeployment.
5. Place the device in the **Ready To Give** section of storage.
