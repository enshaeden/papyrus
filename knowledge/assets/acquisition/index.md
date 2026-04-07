---
id: kb-assets-acquisition-index
title: Assets / Acquisition
canonical_path: knowledge/assets/acquisition/index.md
summary: Collection index for curated seed content under Assets / Acquisition.
type: reference
status: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: Assets / Acquisition
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
services:
- Endpoint Provisioning
tags:
- endpoint
created: '2026-04-07'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
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
- kb-assets-acquisition-adding-mobile-devices-to-endpoint-enrollment-portal
- kb-assets-acquisition-device-enrollment-windows-workstation-setup-user-guide
- kb-assets-acquisition-device-acquisition-and-registration
- kb-assets-acquisition-mac-acquisition-and-configuration
- kb-assets-acquisition-receiving-a-new-windows-device
- kb-assets-acquisition-windows-device-lifecycle
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `assets/acquisition` content under the curated KMDB structure.

## Articles
- [Adding tablet devices/mobile devices to <ENDPOINT_ENROLLMENT_PORTAL>](adding-mobile-devices-to-endpoint-enrollment-portal.md)
- [device enrollment - Windows Workstation Setup - User Guide](device-enrollment-windows-workstation-setup-user-guide.md)
- [Device Acquisition and Registration](device-acquisition-and-registration.md)
- [Mac Acquisition and Configuration](mac-acquisition-and-configuration.md)
- [Receiving a new Windows device](receiving-a-new-windows-device.md)
- [Windows Device Lifecycle](windows-device-lifecycle.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
