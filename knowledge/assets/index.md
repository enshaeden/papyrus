---
id: kb-assets-index
title: Assets
canonical_path: knowledge/assets/index.md
summary: Collection index for curated seed content under Assets.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Asset Management Overview
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-10-28'
updated: '2025-12-10'
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
related_runbooks: []
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
- kb-assets-acquisition-index
- kb-assets-audits-and-recordkeeping-index
- kb-assets-decommissioning-index
- kb-assets-deployment-index
- kb-assets-loaners-index
- kb-assets-overview-index
- kb-assets-printers-index
- kb-assets-shipping-index
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
- kb-assets-acquisition-index
- kb-assets-audits-and-recordkeeping-index
- kb-assets-decommissioning-index
- kb-assets-deployment-index
- kb-assets-loaners-index
- kb-assets-overview-index
- kb-assets-printers-index
- kb-assets-shipping-index
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `assets` content under the curated KMDB structure.

## Imported Context
Asset Management breaks down into two categories - Workstations and Accessories/Peripherals.
The workstation category comprises any compute hardware that is used for primary job function; usually a Laptop-type device with either MacOS or Windows.

## Child Collections
- [Assets / Acquisition](acquisition/index.md)
- [Assets / Audits and Recordkeeping](audits-and-recordkeeping/index.md)
- [Assets / Decommissioning](decommissioning/index.md)
- [Assets / Deployment](deployment/index.md)
- [Assets / Loaners](loaners/index.md)
- [Assets / Overview](overview/index.md)
- [Assets / Printers](printers/index.md)
- [Assets / Shipping](shipping/index.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
