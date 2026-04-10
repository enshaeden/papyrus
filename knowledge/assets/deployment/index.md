---
id: kb-assets-deployment-index
title: Assets / Deployment
canonical_path: knowledge/assets/deployment/index.md
summary: Collection index for curated seed content under Assets / Deployment.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: Assets / Deployment
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2026-04-07'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
service_name: Endpoint Provisioning
service_criticality: not_classified
dependencies:
- <ASSET_MANAGEMENT_SYSTEM>
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks:
- kb-assets-deployment-asset-deployment
- kb-assets-deployment-mac-laptop-deployment
- kb-assets-deployment-windows-deployment
- kb-assets-deployment-windows-device-user-account-setup-internal
related_known_errors: []
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: migration/import-manifest.yml
  note: Collection Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-assets-deployment-asset-deployment
- kb-assets-deployment-mac-laptop-deployment
- kb-assets-deployment-windows-deployment
- kb-assets-deployment-windows-device-user-account-setup-internal
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
services:
- Endpoint Provisioning
related_articles:
- kb-assets-deployment-asset-deployment
- kb-assets-deployment-mac-laptop-deployment
- kb-assets-deployment-windows-deployment
- kb-assets-deployment-windows-device-user-account-setup-internal
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `assets/deployment` content under the curated KMDB structure.

## Articles
- [Asset Deployment](asset-deployment.md)
- [Mac laptop Deployment](mac-laptop-deployment.md)
- [Windows Deployment](windows-deployment.md)
- [Windows Device User Account Setup (Internal)](windows-device-user-account-setup-internal.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
