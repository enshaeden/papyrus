---
id: kb-user-lifecycle-index
title: User Lifecycle
canonical_path: knowledge/user-lifecycle/index.md
summary: Collection index for curated seed content under User Lifecycle.
type: reference
status: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: User Lifecycle Management
team: Identity and Access
systems: []
services: []
tags: []
created: '2025-10-28'
updated: '2026-03-23'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
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
- kb-user-lifecycle-employee-conversion-index
- kb-user-lifecycle-employee-rehire-index
- kb-user-lifecycle-job-and-org-change-index
- kb-user-lifecycle-offboarding-and-termination-index
- kb-user-lifecycle-onboarding-new-hires-index
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `user-lifecycle` content under the curated KMDB structure.

## Imported Context
This section of the IT documentation specifically actions the user lifecycle - from new hires to terminations, all user account activity will exist in this space.
As a matter of ensuring that we meet all compliance and audit requirements, these steps MUST be adhered to for every step of the journey. Each action must be notated for audits and review.

## Child Collections
- [User Lifecycle / Employee Conversion](employee-conversion/index.md)
- [User Lifecycle / Employee Rehire](employee-rehire/index.md)
- [User Lifecycle / Job and Org Change](job-and-org-change/index.md)
- [User Lifecycle / Offboarding and Termination](offboarding-and-termination/index.md)
- [User Lifecycle / Onboarding New Hires](onboarding-new-hires/index.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
