---
id: kb-helpdesk-configuration-and-automation-ticketing-creation-source-labelling
title: '[<QUEUE_NAME>]-creation-source-labelling'
canonical_path: knowledge/helpdesk/configuration-and-automation/ticketing-creation-source-labelling.md
summary: "This <TICKETING_SYSTEM> automation rule adds a label to newly created tickets in the <QUEUE_NAME>\
  \ project to identify the ticket\u2019s creation source (email, portal, <TICKETING_SYSTEM>, or API).\
  \ It uses the <TICKETING_SYSTEM> Service Management issue property..."
knowledge_object_type: runbook
legacy_article_type: SOP
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: '[<QUEUE_NAME>]-creation-source-labelling'
team: Service Desk
systems:
- <TICKETING_SYSTEM>
tags:
- service-desk
created: '2026-02-25'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: service_desk
related_services: []
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
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-helpdesk-configuration-and-automation-index
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-helpdesk-configuration-and-automation-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## <TICKETING_SYSTEM> Automation Documentation: **[<QUEUE_NAME>] Creation source labelling** ### Overview This <TICKETING_SYSTEM> automation rule adds a **label** to newly created tickets in the **<QUEUE_NAME>** project to identify the ticket’s **creation source** (email, portal, <TICKETING_SYSTEM>, or API). It uses the <TICKETING_SYSTEM> Service Management issue property **request.channel.type** (referenced via JQL request-channel-type ) to determine the channel. **Rule description (as configured):** Adds a label for the ticket that identifies the creation source by leveraging the issue property "request.channel.type" <INTERNAL_URL> ## Rule Metadata - **Rule name:** [<QUEUE_NAME>] Creation source labelling
- **State:** Enabled
- **Trigger:** Issue Created ( <TICKETING_SYSTEM>:issue_created )
- **Scope:** Project 10602
- **Other rules triggering:** Disabled ( canOtherRuleTrigger=false ) ## When it runs ### Trigger The rule runs **every time a new issue is created** in the scoped project. ### Global condition A JQL condition ensures the issue is in the <QUEUE_NAME> project: - project = <QUEUE_NAME> ## What it does On issue creation, the rule evaluates the ticket’s request channel type and **adds a corresponding label** : - Email → created_by_email
- Portal → created_by_portal
- <TICKETING_SYSTEM> → created_by_ticketing_system
- API → created_by_api_or_message_integration All label operations are **ADD** operations (no removes configured). ## Label assignment logic ### A. If request channel type is **email** **Condition (JQL):** request-channel-type = email **Action:** Add label → created_by_email **Notifications:** sendNotifications=true ### B. If request channel type is **portal** **Condition (JQL):** request-channel-type = portal **Action:** Add label → created_by_portal **Notifications:** sendNotifications=true ### C. If request channel type is **<TICKETING_SYSTEM>** **Condition (JQL):** request-channel-type = <TICKETING_SYSTEM> **Action:** Add label → created_by_ticketing_system **Notifications:** sendNotifications=true ### D. If request channel type is **api** **Condition (JQL):** request-channel-type = api **Action:** Add label → created_by_api_or_message_integration **Notifications:** sendNotifications=false [Unverified] The label name implies <MESSAGING_PLATFORM> may also map to this branch, but the rule condition explicitly checks only request-channel-type = api . Whether <MESSAGING_PLATFORM>-created requests present as api depends on your <TICKETING_SYSTEM>/<MESSAGING_PLATFORM> integration behavior. ## Examples (expected outcomes) ### Example 1 **Ticket created via email** **Result:** Label added → created_by_email ### Example 2 **Ticket created via portal** **Result:** Label added → created_by_portal ### Example 3 **Ticket created within <TICKETING_SYSTEM>** **Result:** Label added → created_by_ticketing_system ### Example 4 **Ticket created via API** **Result:** Label added → created_by_api_or_message_integration ## Operational notes / maintenance considerations - This rule is purely additive: it **adds** one label based on channel type and does not remove or normalize existing labels.
- Notification behavior differs by branch: - email/portal/<TICKETING_SYSTEM> branches set sendNotifications=true - api branch sets sendNotifications=false
- If additional channels are introduced (or channel values change), you’ll need to add new conditions and labels accordingly. ## Source Rule export JSON: automation-rule-01996302-59a2-7a5c-9b9d-e3c8ff833c1f-<PHONE_NUMBER>.json
