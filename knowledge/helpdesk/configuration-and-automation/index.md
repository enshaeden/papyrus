---
id: kb-helpdesk-configuration-and-automation-index
title: Helpdesk / Configuration and Automation
canonical_path: knowledge/helpdesk/configuration-and-automation/index.md
summary: Collection index for curated seed content under Helpdesk / Configuration and Automation.
type: reference
status: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: Helpdesk / Configuration and Automation
team: Service Desk
systems:
- <TICKETING_SYSTEM>
services: []
tags:
- service-desk
created: '2026-04-07'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: service_desk
prerequisites:
- Review the collection summary and choose the child article that matches the task before acting.
- Confirm the target region, platform, or lifecycle path aligns with the selected child article.
steps:
- Read the collection overview to identify the correct workflow or region-specific article.
- Open the relevant child article and follow its procedure exactly rather than acting from the collection summary alone.
- Record exceptions or missing migration details for follow-up in the migration manifest or rationale doc.
verification:
- The selected child article clearly matches the task, region, and system in scope.
- Operators can navigate from this collection page to the required child articles without ambiguity.
rollback:
- Use the child article rollback guidance for any operational change; this collection page is navigation-only context.
- Escalate to the owning team if none of the child articles match the task safely.
related_articles:
- kb-helpdesk-configuration-and-automation-ticketing-ticketing-system-automations
- kb-helpdesk-configuration-and-automation-ticketing-prevent-reopen-after-30-days
- kb-helpdesk-configuration-and-automation-sla-policy-and-definitions
- kb-helpdesk-configuration-and-automation-ticketing-component-add-on-creation
- kb-helpdesk-configuration-and-automation-ticketing-creation-source-labelling
- kb-helpdesk-configuration-and-automation-ticketing-inbound-on-offboard-adjustments
- kb-helpdesk-configuration-and-automation-ticketing-summary-adjustment
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Collection Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Created as synthetic collection index during <KNOWLEDGE_PORTAL> seed migration.
  author: seed_sanitization
---

## Scope
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `helpdesk/configuration-and-automation` content under the curated KMDB structure.

## Articles
- [<QUEUE_NAME> (<TICKETING_SYSTEM>) Automations](ticketing-ticketing-system-automations.md)
- [<QUEUE_NAME>]-prevent-reopen-after-30-days](hsd-prevent-reopen-after-30-days.md)
- [SLA Policy and Definitions](sla-policy-and-definitions.md)
- [[<QUEUE_NAME>]-component-add-on-creation](hsd-component-add-on-creation.md)
- [[<QUEUE_NAME>]-creation-source-labelling](hsd-creation-source-labelling.md)
- [[<QUEUE_NAME>]-inbound-on-offboard-adjustments](hsd-inbound-on-offboard-adjustments.md)
- [[<QUEUE_NAME>]-summary-adjustment](hsd-summary-adjustment.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
