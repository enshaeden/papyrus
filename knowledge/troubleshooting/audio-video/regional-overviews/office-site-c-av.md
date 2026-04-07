---
id: kb-troubleshooting-audio-video-regional-overviews-office-site-c-av
title: <OFFICE_SITE_C> AV
canonical_path: knowledge/troubleshooting/audio-video/regional-overviews/office-site-c-av.md
summary: "Overview: <OFFICE_SITE_C> is the primary hub for <COMPANY_NAME>\u2019s AV operations and serves as the baseline model for global processes. The <OFFICE_SITE_C> primary office spans two floors (4th and 5th) and includes over 40 AV enabled rooms, ranging..."
type: troubleshooting
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: <OFFICE_SITE_C> AV
team: Workplace Engineering
systems:
- <VIDEO_CONFERENCING_PLATFORM>
services:
- Collaboration
tags:
- av
- service-desk
created: '2025-11-21'
updated: '2025-11-21'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
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
related_articles:
- kb-troubleshooting-audio-video-regional-overviews-index
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

**Overview:** <OFFICE_SITE_C> is the primary hub for <COMPANY_NAME>’s AV operations and serves as the baseline model for global processes. The <OFFICE_SITE_C> primary office spans multiple floors and includes a large set of AV-enabled rooms, ranging from small huddle rooms to large conference and event spaces.

**Automation Details:**

- Monthly automation trigger: 9:00 AM PST, first business day of each month.
- Regional <TICKETING_SYSTEM> label: `region-sea`
- Tech Form: [<INTERNAL_URL>](<INTERNAL_URL>)
- Automation links all submissions to the monthly parent issue labeled `room-sweep-YYYY-MM` .

**Room Types & Equipment:**

| Room Type | Typical Equipment | Notes |
| --- | --- | --- |
| Large Meeting Rooms (12–50 people) | Dual displays, conference-room hardware Trio 8800, room cameras, PolyStudio systems | Perform complete AV and dual display checks. |
| Huddle Rooms (4–8 people) | room video bar or X30, single display, wireless display adapter | Verify cable labeling and wireless casting. |
| Interview Rooms | conference-room hardware Trio, LED display, wireless display adapter | Test microphones and network connection. |
| Private/Focus Rooms | Display + HDMI input | Confirm cable labeling and signage accuracy. |

**Maintenance Notes:**

- Common issue: conference-room hardware registration failures during firmware updates.
- Verify wireless display adapter pairing and HDMI integrity monthly.
- Large rooms require dual testing (conference-room hardware and passthrough laptop input).

**Best Practices:**

- Conduct sweeps early morning or late afternoon to avoid meeting conflicts.
- Document the room identifier in <TICKETING_SYSTEM> comments for traceability.
