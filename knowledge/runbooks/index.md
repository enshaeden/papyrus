---
id: kb-runbooks-index
title: Runbooks
canonical_path: knowledge/runbooks/index.md
summary: Collection index for curated seed content under Runbooks.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Laptop Provisioning Runbook
team: Workplace Engineering
systems:
- <ENDPOINT_ENROLLMENT_PORTAL>
tags:
- endpoint
- template
created: '2026-04-07'
updated: '2026-04-12'
last_reviewed: '2026-04-12'
review_cadence: quarterly
audience: service_desk
service_name: Runbook Library
service_criticality: not_classified
dependencies:
- <ENDPOINT_ENROLLMENT_PORTAL>
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
- kb-runbooks-laptop-provisioning
prerequisites:
- Review the collection summary and choose the child article that matches the operational workflow before acting.
steps:
- Open the runbook article and follow its procedure exactly rather than acting from the collection summary alone.
- Record unresolved migration cleanup in the maintained migration record when the child article still relies on placeholders.
verification:
- Operators can navigate from this collection page to the required child article without ambiguity.
rollback:
- Use the child article rollback guidance for any operational change; this collection page is navigation-only context.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-runbooks-laptop-provisioning
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Collection sanitized source record.
change_log:
- date: '2026-04-12'
  summary: Added the missing top-level Runbooks collection index and aligned it with the maintained migration record.
  author: codex
---

## Scope
This collection page organizes general runbook guidance under the curated Papyrus knowledge model.

## Child Articles
- [Laptop Provisioning](laptop-provisioning.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
