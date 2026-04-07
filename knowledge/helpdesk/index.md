---
id: kb-helpdesk-index
title: Helpdesk
canonical_path: knowledge/helpdesk/index.md
summary: Collection index for curated seed content under Helpdesk.
type: reference
status: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: IT group configurations and general links
team: Service Desk
systems:
- <TICKETING_SYSTEM>
services: []
tags:
- service-desk
created: '2026-02-19'
updated: '2026-03-11'
last_reviewed: '2026-04-07'
review_cadence: quarterly
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
- kb-helpdesk-configuration-and-automation-index
- kb-helpdesk-policies-index
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `helpdesk` content under the curated KMDB structure.

## Imported Context
[<QUEUE_NAME>](<INTERNAL_URL>) - for direct communication with the Security team
[<QUEUE_NAME><COMPANY_NAME>](<INTERNAL_URL>) - for non-email comms with <TEAM_NAME>

## Child Collections
- [Helpdesk / Configuration and Automation](configuration-and-automation/index.md)
- [Helpdesk / Policies](policies/index.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
