---
id: kb-access-index
title: Access
canonical_path: knowledge/access/index.md
summary: Collection index for curated seed content under Access.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Password Reset and Account Lockout Response
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
- <TICKETING_SYSTEM>
tags:
- access
- service-desk
created: '2026-04-07'
updated: '2026-04-12'
last_reviewed: '2026-04-12'
review_cadence: quarterly
audience: service_desk
service_name: Access Management
service_criticality: not_classified
dependencies:
- <IDENTITY_PROVIDER>
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
- kb-access-password-reset-account-lockout
- kb-access-software-access-request
prerequisites:
- Review the collection summary and choose the child article that matches the task before acting.
steps:
- Open the relevant child article and follow its procedure exactly rather than acting from the collection summary alone.
- Record unresolved migration cleanup in the maintained migration record when the child article still relies on placeholders.
verification:
- Operators can navigate from this collection page to the required child article without ambiguity.
rollback:
- Use the child article rollback guidance for any operational change; this collection page is navigation-only context.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-access-password-reset-account-lockout
- kb-access-software-access-request
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Collection sanitized source record.
change_log:
- date: '2026-04-12'
  summary: Added the missing top-level Access collection index and aligned it with the maintained migration record.
  author: codex
---

## Scope
This collection page organizes access-management guidance under the curated Papyrus knowledge model.

## Child Articles
- [Password Reset and Account Lockout Response](password-reset-account-lockout.md)
- [Software and Access Request](software-access-request.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
