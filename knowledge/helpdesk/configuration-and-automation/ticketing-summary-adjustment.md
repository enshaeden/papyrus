---
id: kb-helpdesk-configuration-and-automation-ticketing-summary-adjustment
title: '[<QUEUE_NAME>]-summary-adjustment'
canonical_path: knowledge/helpdesk/configuration-and-automation/ticketing-summary-adjustment.md
summary: Standardize a request summary on ticket creation for a specific service request type.
type: SOP
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: '[<QUEUE_NAME>]-summary-adjustment'
team: Service Desk
systems:
- <TICKETING_SYSTEM>
services:
- Access Management
tags:
- service-desk
created: '2026-02-25'
updated: '2026-04-07'
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

## Rule Intent

This automation updates the ticket summary when a specific service request type is created so the summary is predictable and searchable.

## Trigger

- Event: issue created
- Scope: the configured service desk project
- Request type: the targeted accessory-request type or equivalent intake

## Action

Set the summary to:

`Accessory request for {{issue.reporter.displayName}}`

Then refresh the issue so the updated summary is visible to downstream rules and operators.

## Example Outcomes

- If the reporter is `<PERSON_NAME>`, the summary becomes `Accessory request for <PERSON_NAME>`.
- If the request type does not match the targeted intake, the rule does not update the summary.

## Operational Notes

- This rule depends on exact request-type matching. If the request type is renamed, update the rule.
- If display-name formatting changes, the resulting summary text will change as well.
- Confirm notification behavior before enabling the rule in production.
