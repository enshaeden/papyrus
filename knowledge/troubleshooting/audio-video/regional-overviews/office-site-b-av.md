---
id: kb-troubleshooting-audio-video-regional-overviews-office-site-b-av
title: <OFFICE_SITE_B> AV
canonical_path: knowledge/troubleshooting/audio-video/regional-overviews/office-site-b-av.md
summary: 'Overview: The <OFFICE_SITE_B> site contains roughly 5 AV equipped rooms designed for small team
  collaboration. These rooms use streamlined setups for quick deployment and consistent user experience.'
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: <OFFICE_SITE_B> AV
team: Workplace Engineering
systems:
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: '2025-11-21'
updated: '2025-11-21'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Collaboration
symptoms:
- 'Overview: The <OFFICE_SITE_B> site contains roughly 5 AV equipped rooms designed for small team collaboration.
  These rooms use streamlined setups for quick deployment and consistent user experience.'
scope: 'Legacy source does not declare structured scope. Summary: Overview: The <OFFICE_SITE_B> site contains
  roughly 5 AV equipped rooms designed for small team collaboration. These rooms use streamlined setups
  for quick deployment and consistent user experience.'
cause: Legacy source does not declare a structured cause field.
diagnostic_checks:
- Review the imported procedure body below and confirm the documented symptoms match the live issue.
- Work through the diagnostic and remediation steps in order, recording any deviations in the ticket.
- Escalate when the documented checks fail or the issue exceeds the article scope.
mitigations:
- Undo any reversible change documented in the procedure if validation fails.
- Escalate to the owning team with the captured symptom and actions already taken.
permanent_fix_status: unknown
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-troubleshooting-audio-video-regional-overviews-index
prerequisites:
- Capture the exact symptom, affected scope, and recent changes before troubleshooting.
- Confirm you have the required system access or escalation path before making changes.
steps:
- Review the imported procedure body below and confirm the documented symptoms match the live issue.
- Work through the diagnostic and remediation steps in order, recording any deviations in the ticket.
- Escalate when the documented checks fail or the issue exceeds the article scope.
verification:
- The reported symptom no longer reproduces after the documented steps are completed.
- The ticket or case record contains the troubleshooting outcome and any follow-up actions.
rollback:
- Undo any reversible change documented in the procedure if validation fails.
- Escalate to the owning team with the captured symptom and actions already taken.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
related_articles:
- kb-troubleshooting-audio-video-regional-overviews-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

**Overview:** The <OFFICE_SITE_B> site contains roughly 5 AV-equipped rooms designed for small team collaboration. These rooms use streamlined setups for quick deployment and consistent user experience.

**Automation Details:**

- Monthly automation trigger: 9:00 AM PST, first business day of each month.
- Regional <TICKETING_SYSTEM> label: `region-yvr`
- Tech Form: [<INTERNAL_URL>](<INTERNAL_URL>)
- Sweep tickets automatically link to the `room-sweep-YYYY-MM` parent task.

**Room Types & Equipment:**

| Room Type | Typical Equipment | Notes |
| --- | --- | --- |
| Small Meeting Rooms (4–6 people) | room video bar, direct HDMI | Verify naming consistency between display and booking system. |
| Huddle Pods | USB conference camera, room cameras, HDMI + USB-C | Check cable condition and labeling monthly. |

**Maintenance Notes:**

- Check wireless presentation hardware and wireless display adapter connectivity during every sweep.
- Verify microphone sensitivity; recalibrate if clarity is degraded.
- Confirm firmware is current for all PolyStudio units.

**Best Practices:**

- Maintain one backup PolyStudio unit for immediate replacement.
- Ensure conference room names match <VIDEO_CONFERENCING_PLATFORM> and <COLLABORATION_PLATFORM> meeting identifiers.
