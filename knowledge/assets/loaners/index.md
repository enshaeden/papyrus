---
id: kb-assets-loaners-index
title: Assets / Loaners
canonical_path: knowledge/assets/loaners/index.md
summary: Collection index for curated seed content under Assets / Loaners.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Assets / Loaners
team: Systems Engineering
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
- kb-assets-loaners-loaner-laptops
- kb-assets-loaners-region-d-loaner-location-and-access-for-remote-support
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-c-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-b-loaner-location-and-access-for-remote-support
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
- kb-assets-loaners-loaner-laptops
- kb-assets-loaners-region-d-loaner-location-and-access-for-remote-support
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-c-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-b-loaner-location-and-access-for-remote-support
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
- kb-assets-loaners-loaner-laptops
- kb-assets-loaners-region-d-loaner-location-and-access-for-remote-support
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-c-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-b-loaner-location-and-access-for-remote-support
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
This collection page organizes the shared loaner-device policy and the site-specific storage or pickup pages used to fulfill the request.

## Articles
- [Loaner Laptops](loaner-laptops.md)
- [<REGION_D> Loaner Location and Access for Remote Support](region-d-loaner-location-and-access-for-remote-support.md)
- [<REGION_A> Loaner Location and Access for Remote Support](region-a-loaner-location-and-access-for-remote-support.md)
- [<OFFICE_SITE_C> Loaner Location and Access for Remote Support](office-site-c-loaner-location-and-access-for-remote-support.md)
- [<OFFICE_SITE_B> Loaner Location and Access for Remote Support](office-site-b-loaner-location-and-access-for-remote-support.md)

## Migration Notes
- Use [Loaner Laptops](loaner-laptops.md) for shared eligibility, inventory, and ticketing rules.
- Use the location pages for office- or region-specific storage, pickup, and approval differences.
