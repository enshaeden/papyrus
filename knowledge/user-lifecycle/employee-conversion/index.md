---
id: kb-user-lifecycle-employee-conversion-index
title: User Lifecycle / Employee Conversion
canonical_path: knowledge/user-lifecycle/employee-conversion/index.md
summary: Collection index for curated seed content under User Lifecycle / Employee Conversion.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Employee Conversion
team: IT Operations
systems: []
tags: []
created: '2025-10-15'
updated: '2025-10-15'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
service_name: User Lifecycle / Employee Conversion
service_criticality: not_classified
dependencies: []
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks:
- kb-user-lifecycle-employee-conversion-contractor-to-fte
- kb-user-lifecycle-employee-conversion-fte-to-contractor
- kb-user-lifecycle-employee-conversion-intern-to-fte
related_known_errors: []
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: docs/migration/seed-migration-rationale.md
  note: Collection Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-user-lifecycle-employee-conversion-contractor-to-fte
- kb-user-lifecycle-employee-conversion-fte-to-contractor
- kb-user-lifecycle-employee-conversion-intern-to-fte
prerequisites:
- Review the collection summary and choose the child article that matches the task before acting.
- Confirm the target region, platform, or lifecycle path aligns with the selected child article.
steps:
- Read the collection overview to identify the correct workflow or region-specific article.
- Open the relevant child article and follow its procedure exactly rather than acting from the collection
  summary alone.
- Record exceptions or missing migration details for follow-up in the migration manifest or rationale
  doc.
verification:
- The selected child article clearly matches the task, region, and system in scope.
- Operators can navigate from this collection page to the required child articles without ambiguity.
rollback:
- Use the child article rollback guidance for any operational change; this collection page is navigation-only
  context.
- Escalate to the owning team if none of the child articles match the task safely.
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-user-lifecycle-employee-conversion-contractor-to-fte
- kb-user-lifecycle-employee-conversion-fte-to-contractor
- kb-user-lifecycle-employee-conversion-intern-to-fte
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Collection Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Created as synthetic collection index during <KNOWLEDGE_PORTAL> seed migration.
  author: seed_sanitization
---

## Scope
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `user-lifecycle/employee-conversion` content under the curated KMDB structure.

## Imported Context
This SOP outlines the steps the IT team must follow when an employee transitions between a **Contractor** and a **Full-Time Employee (FTE)** , in either direction. Each direction is documented as a separate workflow.
Confirm that the sync completes successfully and that the user's <IDENTITY_PROVIDER> and <COLLABORATION_PLATFORM> profile reflect the correct email and identity updates.

## Articles
- [Contractor to FTE](contractor-to-fte.md)
- [FTE to Contractor](fte-to-contractor.md)
- [Intern to FTE](intern-to-fte.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
