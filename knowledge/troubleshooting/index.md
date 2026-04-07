---
id: kb-troubleshooting-index
title: Troubleshooting
canonical_path: knowledge/troubleshooting/index.md
summary: Collection index for curated seed content under Troubleshooting.
type: reference
status: active
owner: service_owner
source_type: derived
source_system: knowledge_portal
source_title: Hours, Location, and Coverage
team: Service Desk
systems: []
services: []
tags:
- service-desk
created: '2025-10-28'
updated: '2025-12-29'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: service_desk
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
- kb-troubleshooting-audio-video-index
- kb-troubleshooting-device-index
- kb-troubleshooting-network-index
- kb-troubleshooting-identity-provider-index
- kb-troubleshooting-onsite-support-index
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
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize `troubleshooting` content under the curated KMDB structure.

## Imported Context
IT Support covers a 21x5 model due to our geographic distribution. Centered around our <OFFICE_SITE_C> primary office operation, and, therefor, PST, the hours and coverage are as follows:
**Sunday** 20:00 PST to **Monday** 17:00 PST (Monday 0830 IST to Tuesday 0530 IST)

## Child Collections
- [Troubleshooting / Audio and Video](audio-video/index.md)
- [Troubleshooting / Device](device/index.md)
- [Troubleshooting / Network](network/index.md)
- [Troubleshooting / <IDENTITY_PROVIDER>](identity-provider/index.md)
- [Troubleshooting / Onsite Support](onsite-support/index.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
