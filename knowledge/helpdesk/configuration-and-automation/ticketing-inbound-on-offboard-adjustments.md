---
id: kb-helpdesk-configuration-and-automation-ticketing-inbound-on-offboard-adjustments
title: '[<QUEUE_NAME>]-inbound-on-offboard-adjustments'
canonical_path: knowledge/helpdesk/configuration-and-automation/ticketing-inbound-on-offboard-adjustments.md
summary: This <TICKETING_SYSTEM> automation rule automatically applies Components (and in one case, assignee
  group routing ) to newly created issues in a specific <TICKETING_SYSTEM> project, based on keywords
  found in the issue Summary .
knowledge_object_type: runbook
legacy_article_type: SOP
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: '[<QUEUE_NAME>]-inbound-on-offboard-adjustments'
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
  source_ref: docs/migration/seed-migration-rationale.md
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
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Overview This <TICKETING_SYSTEM> automation rule automatically applies **Components** (and in one case, **assignee group routing** ) to newly created issues in a specific <TICKETING_SYSTEM> project, based on keywords found in the issue **Summary** . # Rule Metadata - **Rule name:** [<QUEUE_NAME>] Inbound on/offboard adjustments
- **State:** Enabled
- **Trigger:** Issue Created
- **Scope:** One project (project ARI in rule scope)
- **Notifications:** Does **not** send notifications when it edits issues (sendNotifications = false) # When it runs ## Trigger The rule runs **every time a new issue is created** in the scoped project. ## What it does The rule evaluates the issue **Summary** and performs actions in two groups: 1. **Component assignment (based on Summary text)**
2. **Assignment routing (<REGION_A> keyword routing)** # Component assignment logic All comparisons below are **CONTAINS** checks against the issue **Summary** (case handling depends on the specific condition’s modifier settings). ### A. If Summary contains **“NEW HIRE”** **Action:** Set **Components** to: - Onboarding ### B. If Summary contains **“SPECIAL LEAVE:”** **Action:** Set **Components** to: - Offboarding ### C. If Summary contains **“TERM - ”** **Action:** Set **Components** to: - Offboarding
- Asset Recovery ### D. If Summary contains **“TERM”** AND Summary does **NOT** contain **“Asset”** **Action:** Set **Components** to: - Offboarding **Important note about overlaps** - If a Summary includes **“TERM - ”** , it also includes **“TERM”** , so multiple conditions may match in the same run.
- Each matching branch uses **SET** on Components, meaning later matches can overwrite earlier ones (depending on the rule’s execution order in the engine). - [Inference] The platform typically evaluates rule branches top-to-bottom as defined, but I cannot verify the exact runtime ordering from this export alone. # Assignment routing logic ### If Summary contains **“<REGION_A>”** **Action:** Assign the issue using **Round Robin** within a specific **group** (group ID is defined in the rule). - Assign type: GROUP
- Method: ROUNDROBIN
- Group: (by group ID in rule config) ## Examples (expected outcomes) ### Example 1 **Summary:** NEW HIRE - John Doe - <OFFICE_SITE_C> **Result:** Components → Onboarding ### Example 2 **Summary:** TERM - <PERSON_NAME> - Laptop return needed **Result:** Components → Offboarding , Asset Recovery ### Example 3 **Summary:** TERM - <REGION_A> - Contractor **Result:** - Components → Offboarding , Asset Recovery
- Assigned via <REGION_A> group round-robin ### Example 4 **Summary:** TERM - Asset: already recovered **Result:** Components behavior depends on which matching branch “wins” if multiple match. - “TERM - ” branch sets Offboarding + Asset Recovery
- “TERM” AND NOT_CONTAIN “Asset” branch would **not** match because Summary contains “Asset” ## Operational notes / maintenance considerations - **Summary formatting is critical.** This automation relies on standardized keywords in the Summary (e.g., “NEW HIRE”, “TERM - ”).
- **Components are overwritten (SET), not appended.** If manual components are added before the rule runs (or if other rules modify components), this rule can replace them.
- **<REGION_A> routing is keyword-based.** Any issue with “<REGION_A>” in the Summary will be routed, even if it’s unrelated to onboarding/offboarding. - [Inference] If false positives occur, consider tightening the condition (e.g., require both “<REGION_A>” AND “NEW HIRE/TERM”).
