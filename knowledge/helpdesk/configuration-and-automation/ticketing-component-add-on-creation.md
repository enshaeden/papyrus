---
id: kb-helpdesk-configuration-and-automation-ticketing-component-add-on-creation
title: '[<QUEUE_NAME>]-component-add-on-creation'
canonical_path: knowledge/helpdesk/configuration-and-automation/ticketing-component-add-on-creation.md
summary: This <TICKETING_SYSTEM> automation rule sets the Component(s) on newly created issues in a specific Service Desk project, based on keywords found in the issue Summary .
type: SOP
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: '[<QUEUE_NAME>]-component-add-on-creation'
team: Service Desk
systems:
- <TICKETING_SYSTEM>
services: []
tags:
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

## <TICKETING_SYSTEM> Automation Documentation: **[<QUEUE_NAME>] Component add on creation** ### Overview This <TICKETING_SYSTEM> automation rule sets the **Component(s)** on newly created issues in a specific Service Desk project, based on keywords found in the issue **Summary** . ## Rule Metadata - **Rule name:** [<QUEUE_NAME>] Component add on creation
- **State:** Enabled
- **Trigger:** Issue Created
- **Scope:** Project 10602
- **Other rules triggering:** Disabled ( canOtherRuleTrigger=false )
- **Notification behavior:** Actions in this rule have sendNotifications=true ## When it runs ### Trigger The rule runs **every time a new issue is created** in the scoped project. ## What it does On issue creation, the rule evaluates the issue **Summary** and applies a **SET** operation to the **Components** field for matching conditions. ## Component assignment logic ### A. If Summary contains **“General Access Request from OIG”** **Condition:** Summary **CONTAINS** General Access Request from OIG **Action:** Set **Components** to: - <IDENTITY_PROVIDER> Identity (App requests) ### B. If Summary contains **“<REMOTE_WORKSPACE_PLATFORM>”** **Condition:** Summary **CONTAINS** <REMOTE_WORKSPACE_PLATFORM> **Action:** Set **Components** to: - <REMOTE_WORKSPACE_PLATFORM> ## Examples (expected outcomes) ### Example 1 **Summary:** General Access Request from OIG - New user **Result:** Components → <IDENTITY_PROVIDER> Identity (App requests) ### Example 2 **Summary:** <REMOTE_WORKSPACE_PLATFORM> - Install request **Result:** Components → <REMOTE_WORKSPACE_PLATFORM> ### Example 3 **Summary:** <REMOTE_WORKSPACE_PLATFORM> + General Access Request from OIG **Result:** Components outcome depends on which matching action is applied last. - [Inference] Because both actions use **SET** on components , if both conditions match in one execution, the final value will be whichever action runs last. I cannot verify the exact execution ordering from this export alone. ## Operational notes / maintenance considerations - This rule uses **Summary keyword matching** . If request naming conventions change, the conditions will stop matching.
- Both actions use **SET** on Components (not add/append). If other automation rules or manual edits set Components, this rule can overwrite them at create-time.
- sendNotifications=true means <TICKETING_SYSTEM> may notify watchers/participants when Components are changed (depends on your <TICKETING_SYSTEM> notification scheme). ## Source Rule export JSON: automation-rule-0199ba0a-7aad-7eb4-ab87-da2f8386b828-<PHONE_NUMBER>.json
