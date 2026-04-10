---
id: kb-assets-printers-index
title: Assets / Printers
canonical_path: knowledge/assets/printers/index.md
summary: Collection index for curated seed content under Assets / Printers.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: Assets / Printers
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <PRINTER_MANAGEMENT_PLATFORM>
tags:
- endpoint
- printer
created: '2026-04-07'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
service_name: Assets / Printers
service_criticality: not_classified
dependencies:
- <ASSET_MANAGEMENT_SYSTEM>
- <PRINTER_MANAGEMENT_PLATFORM>
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks:
- kb-assets-printers-overview-region-a-office-printers
- kb-assets-printers-overview-office-site-b-office-printer
- kb-assets-printers-printing-in-the-region-d-office
- kb-assets-printers-user-guide-printing-in-the-region-a-office-site-a-hub
- kb-assets-printers-user-guide-printing-in-the-office-site-b-office-mac
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
- kb-assets-printers-overview-region-a-office-printers
- kb-assets-printers-overview-office-site-b-office-printer
- kb-assets-printers-printing-in-the-region-d-office
- kb-assets-printers-user-guide-printing-in-the-region-a-office-site-a-hub
- kb-assets-printers-user-guide-printing-in-the-office-site-b-office-mac
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
- Printing
related_articles:
- kb-assets-printers-overview-region-a-office-printers
- kb-assets-printers-overview-office-site-b-office-printer
- kb-assets-printers-printing-in-the-region-d-office
- kb-assets-printers-user-guide-printing-in-the-region-a-office-site-a-hub
- kb-assets-printers-user-guide-printing-in-the-office-site-b-office-mac
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `assets/printers` content under the curated KMDB structure.

## Articles
- [Overview - <REGION_A> Office Printers](overview-region-a-office-printers.md)
- [Overview - <OFFICE_SITE_B> Office Printer](overview-office-site-b-office-printer.md)
- [Printing in the <REGION_D> Office](printing-in-the-region-d-office.md)
- [User Guide - Printing in the <REGION_A> - <OFFICE_SITE_A> Hub](user-guide-printing-in-the-region-a-office-site-a-hub.md)
- [User Guide - Printing in the <OFFICE_SITE_B> Office (Mac)](user-guide-printing-in-the-office-site-b-office-mac.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
