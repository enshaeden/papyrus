---
id: kb-helpdesk-configuration-and-automation-ticketing-prevent-reopen-after-30-days
title: <QUEUE_NAME>]-prevent-reopen-after-30-days
canonical_path: knowledge/helpdesk/configuration-and-automation/ticketing-prevent-reopen-after-30-days.md
summary: "This <TICKETING_SYSTEM> automation rule prevents customers from \u201Cre opening\u201D or continuing work on older, already resolved tickets by posting guidance when the reporter comments on a ticket that was resolved 30+ days ago . It then..."
type: SOP
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: <QUEUE_NAME>]-prevent-reopen-after-30-days
team: Service Desk
systems:
- <HR_SYSTEM>
- <TICKETING_SYSTEM>
services: []
tags:
- account
- service-desk
created: '2026-02-25'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: service_desk
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
related_articles:
- kb-helpdesk-configuration-and-automation-index
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

This <TICKETING_SYSTEM> automation rule prevents customers from “re-opening” or continuing work on older, already-resolved tickets by posting guidance when the **reporter** comments on a ticket that was resolved **30+ days ago** . It then transitions the issue back to a defined status. # Rule Metadata - **Rule name:** [<QUEUE_NAME>] Prevent re-open after 30 days
- **State:** Enabled
- **Trigger:** Issue commented (primary action)
- **Scope:** Project 10602 (Service Desk project type)
- **Other rules triggering:** Disabled ( canOtherRuleTrigger=false ) # When it runs ## Trigger The rule runs when an issue receives a **comment** event (PRIMARY_ACTION) in the scoped project. ## Preconditions (all must be true) The automation only continues if **all** of the following conditions match: 1. **Comment initiator is the issue reporter** 1. Condition: initiator USER_IS {{issue.reporter}}
2. **Issue type is one of two specific issue type IDs** 1. IssueType IDs: Service Request or Software or Hardware
3. **Current status is one of:** 1. Resolved , Closed , Done , Completed ## Decision logic (IF blocks) ### Block A: If the ticket was resolved **30+ days ago** **Condition (JQL):** resolutiondate <= -30d **Action:** Add a **public comment** (only once) telling the reporter to open a new ticket instead of updating an old resolved one. - publicComment=true
- addCommentOnce=true
- sendNotifications=true **Comment text (verbatim):** Thank you for reaching out for support. As a best practice, please do not update a ticket has been resolved for 30 days or longer. This ticket was resolved 30+ days ago. Therefore, please create a new ticket with the IT team for this issue to ensure continuity of service and proper issue tracking. If this ticket is relevant to the new one, please reference it when creating the new issue so that the team can link the two. ### Block B: Otherwise (ticket resolved less than 30 days ago) **Action:** Transition the issue to status In Progress . - destinationStatus.value = "In Progress"
- sendNotifications=true ## Examples (expected outcomes) ### Example 1 (blocked re-open behavior) **Scenario:** Reporter comments on a ticket in Resolved and it was resolved 45 days ago. **Result:** Automation posts the public guidance comment (once) asking them to open a new ticket. ### Example 2 (recent resolved ticket) **Scenario:** Reporter comments on a ticket in Resolved and it was resolved 7 days ago. **Result:** Automation transitions the ticket to status ID 3 . ### Example 3 (non-reporter comment) **Scenario:** An agent comments (not the reporter). **Result:** Rule does not proceed past the initiator condition (no actions). # Operational notes / maintenance considerations - This rule only applies to two specific **issue types by ID** ( Service Request , Software or Hardware ). If new request types should follow the same behavior, they must be added explicitly.
- The “30+ days” logic is driven by JQL on resolutiondate . Tickets without a resolution date won’t match that block.
