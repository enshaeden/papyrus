---
id: kb-troubleshooting-meeting-room-av-triage
title: Meeting Room AV Triage
canonical_path: knowledge/troubleshooting/meeting-room-av-triage.md
summary: Triage common meeting room audio, display, and conferencing issues before escalating to facilities or engineering.
type: troubleshooting
status: active
owner: Collaboration Engineering
source_type: native
team: Workplace Engineering
systems:
  - Zoom Rooms
  - Ticketing Queue
services:
  - Collaboration
tags:
  - av
  - service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: service_desk
prerequisites:
  - Ticket includes room name, meeting start time, and observed failure.
  - Access to room health status or the conferencing admin console.
steps:
  - Determine whether the issue is display, audio, camera, controller, or room scheduling related.
  - Check the room status in Zoom Rooms before dispatching onsite support.
  - Have the onsite contact confirm power, cable seating, and whether the room controller is responsive.
  - Restart the room controller or conferencing app only if the room is between meetings or the current meeting owner approves.
  - Escalate to Workplace Engineering when the issue repeats in the same room within seven days or involves room hardware failure.
verification:
  - Room can join a test meeting successfully.
  - Camera, microphone, and display function in the test call.
  - Ticket records the failing component and the exact remediation used.
rollback:
  - Restore the room to the prior configuration if a profile or peripheral reassignment causes additional failures.
  - Reopen the incident ticket immediately if the room cannot be returned to a known-good state.
related_articles:
  - kb-troubleshooting-printer-queue
replaced_by: null
retirement_reason: null
references:
  - title: Room support contact list
    note: Identify the onsite contact before requesting a manual cable or power check.
change_log:
  - date: 2026-04-07
    summary: Initial seed article.
    author: Repository bootstrap
---

## Notes

For executive briefing rooms, skip ad hoc troubleshooting that interrupts an active meeting and escalate directly to the designated room owner.
