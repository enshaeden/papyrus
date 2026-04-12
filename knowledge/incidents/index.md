---
id: kb-incidents-index
title: Incidents
canonical_path: knowledge/incidents/index.md
summary: Collection index for curated seed content under Incidents.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Incident Response Template
team: Service Desk
systems:
- <TICKETING_SYSTEM>
tags:
- incident
- service-desk
created: '2026-04-07'
updated: '2026-04-12'
last_reviewed: '2026-04-12'
review_cadence: quarterly
audience: service_desk
service_name: Incident Response
service_criticality: not_classified
dependencies:
- <TICKETING_SYSTEM>
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks: []
related_known_errors: []
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: docs/migration/seed-migration-rationale.md
  note: Collection sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-incidents-incident-response-template
prerequisites:
- Review the collection summary and choose the child article that matches the incident workflow before acting.
steps:
- Open the incident article and follow its procedure exactly rather than acting from the collection summary alone.
- Record unresolved migration cleanup in the maintained migration record when the child article still relies on placeholders.
verification:
- Operators can navigate from this collection page to the required child article without ambiguity.
rollback:
- Use the child article rollback guidance for any operational change; this collection page is navigation-only context.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Incident Management
related_articles:
- kb-incidents-incident-response-template
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Collection sanitized source record.
change_log:
- date: '2026-04-12'
  summary: Added the missing top-level Incidents collection index and aligned it with the maintained migration record.
  author: codex
---

## Scope
This collection page organizes incident-response guidance under the curated Papyrus knowledge model.

## Child Articles
- [Incident Response Template](incident-response-template.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
