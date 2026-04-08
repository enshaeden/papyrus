---
id: kb-troubleshooting-meeting-room-av-triage
title: Meeting Room AV Triage
canonical_path: knowledge/troubleshooting/meeting-room-av-triage.md
summary: Triage common meeting room audio, display, and conferencing issues before escalating to facilities
  or engineering.
knowledge_object_type: known_error
legacy_article_type: troubleshooting
status: active
owner: service_owner
source_type: native
source_system: repository
source_title: Meeting Room AV Triage
team: Workplace Engineering
systems:
- <TICKETING_SYSTEM>
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: service_desk
related_services:
- Collaboration
symptoms:
- Triage common meeting room audio, display, and conferencing issues before escalating to facilities or
  engineering.
scope: 'Legacy source does not declare structured scope. Summary: Triage common meeting room audio, display,
  and conferencing issues before escalating to facilities or engineering.'
cause: Legacy source does not declare a structured cause field.
diagnostic_checks:
- Determine whether the issue is display, audio, camera, controller, or room scheduling related.
- Check the room status in <VIDEO_CONFERENCING_PLATFORM> before dispatching onsite support.
- Have the onsite contact confirm power, cable seating, and whether the room controller is responsive.
- Restart the room controller or conferencing app only if the room is between meetings or the current
  meeting owner approves.
- Escalate to Workplace Engineering when the issue repeats in the same room within seven days or involves
  room hardware failure.
mitigations:
- Restore the room to the prior configuration if a profile or peripheral reassignment causes additional
  failures.
- Reopen the incident ticket immediately if the room cannot be returned to a known-good state.
permanent_fix_status: unknown
citations:
- article_id: null
  source_title: Room support contact list
  source_type: document
  source_ref: Room support contact list
  note: Identify the onsite contact before requesting a manual cable or power check.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-troubleshooting-printer-queue
prerequisites:
- Ticket includes room name, meeting start time, and observed failure.
- Access to room health status or the conferencing admin portal.
steps:
- Determine whether the issue is display, audio, camera, controller, or room scheduling related.
- Check the room status in <VIDEO_CONFERENCING_PLATFORM> before dispatching onsite support.
- Have the onsite contact confirm power, cable seating, and whether the room controller is responsive.
- Restart the room controller or conferencing app only if the room is between meetings or the current
  meeting owner approves.
- Escalate to Workplace Engineering when the issue repeats in the same room within seven days or involves
  room hardware failure.
verification:
- Room can join a test meeting successfully.
- Camera, microphone, and display function in the test call.
- Ticket records the failing component and the exact remediation used.
rollback:
- Restore the room to the prior configuration if a profile or peripheral reassignment causes additional
  failures.
- Reopen the incident ticket immediately if the room cannot be returned to a known-good state.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
related_articles:
- kb-troubleshooting-printer-queue
references:
- title: Room support contact list
  note: Identify the onsite contact before requesting a manual cable or power check.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Notes

For executive briefing rooms, skip ad hoc troubleshooting that interrupts an active meeting and escalate directly to the designated room owner.
