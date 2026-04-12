---
id: kb-troubleshooting-audio-video-boardrooms-touch-controller-room-user-guide
title: Touch Controller Room User Guide
canonical_path: knowledge/troubleshooting/audio-video/boardrooms/touch-controller-room-user-guide.md
summary: Shared operator guide for meeting rooms that use a room video bar and touch controller for native room joins.
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: it_operations
source_type: native
source_system: repository
source_title: Touch Controller Room User Guide
team: Workplace Engineering
systems:
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: systems_admins
related_services:
- Collaboration
symptoms:
- Operators need one maintained guide for touch-controller room systems that can join meetings natively without a laptop-driven AV workflow.
scope: Use this guide for rooms with a room video bar, touch controller, and native meeting join workflow. Use site-specific overview or room notes only for local room mapping, labels, or unique hardware exceptions.
cause: Multiple site and room guides repeated the same touch-controller meeting flow, creating unnecessary copy-based variants.
diagnostic_checks:
- Confirm the room has a touch controller and room system join flow rather than a USB-only laptop setup.
- Verify the meeting was scheduled with the room resource when using one-touch join.
- Escalate to the site-specific room article if the room has special hardware beyond this shared controller-based baseline.
mitigations:
- Keep the common controller workflow here and reserve site articles for local room naming, room lists, or unique equipment.
- Re-open this shared guide if controller-based room standards diverge across sites.
permanent_fix_status: unknown
citations:
- article_id: kb-troubleshooting-audio-video-boardrooms-office-site-a-video-conferencing-platform-enabled-meeting-rooms-user-guide
  source_title: <VIDEO_CONFERENCING_PLATFORM> Enabled Meeting Rooms - User Guide
  source_type: document
  source_ref: knowledge/troubleshooting/audio-video/boardrooms/office-site-a/video-conferencing-platform-enabled-meeting-rooms-user-guide.md
  note: Imported source used to consolidate the repeated touch-controller procedure.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
- article_id: kb-troubleshooting-audio-video-boardrooms-office-site-b-meeting-room-user-guide-room-name-d
  source_title: Meeting Room User Guide – <ROOM_NAME_D>
  source_type: document
  source_ref: knowledge/troubleshooting/audio-video/boardrooms/office-site-b/meeting-room-user-guide-room-name-d.md
  note: Matching room-specific variant used during consolidation.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-troubleshooting-audio-video-boardrooms-index
- kb-troubleshooting-audio-video-boardrooms-office-site-a-overview-office-site-a-meeting-rooms
- kb-troubleshooting-audio-video-boardrooms-office-site-b-overview-office-site-b-meeting-rooms
- kb-troubleshooting-audio-video-boardrooms-office-site-a-video-conferencing-platform-enabled-meeting-room-user-guide-for-room-name-f
prerequisites:
- Confirm the room uses a touch controller and native room-system join flow.
- Confirm the operator can identify the matching room from the local site overview before acting.
steps:
- Use the touch controller for one-touch join, manual join, or instant-meeting flow as appropriate.
- Adjust room audio and sharing controls from the room system rather than from an end-user laptop when possible.
- Use the linked site overview or room-specific guide if local room mapping or unique hardware notes are required.
verification:
- The room can join meetings and present content through the controller-based workflow.
- The operator can map the shared guide to the correct site room without ambiguity.
rollback:
- End the room session and return the controller and room system to an idle state if setup fails.
- Escalate to the site owner if the room hardware or workflow does not match the shared controller-based baseline.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
related_articles:
- kb-troubleshooting-audio-video-boardrooms-index
- kb-troubleshooting-audio-video-boardrooms-office-site-a-overview-office-site-a-meeting-rooms
- kb-troubleshooting-audio-video-boardrooms-office-site-b-overview-office-site-b-meeting-rooms
- kb-troubleshooting-audio-video-boardrooms-office-site-a-video-conferencing-platform-enabled-meeting-room-user-guide-for-room-name-f
references:
- title: Overview - <OFFICE_SITE_A> Meeting Rooms
  article_id: kb-troubleshooting-audio-video-boardrooms-office-site-a-overview-office-site-a-meeting-rooms
  path: knowledge/troubleshooting/audio-video/boardrooms/office-site-a/overview-office-site-a-meeting-rooms.md
  note: Use the site overview to map this shared guide to the applicable room set in <OFFICE_SITE_A>.
- title: Overview - <OFFICE_SITE_B> Meeting Rooms
  article_id: kb-troubleshooting-audio-video-boardrooms-office-site-b-overview-office-site-b-meeting-rooms
  path: knowledge/troubleshooting/audio-video/boardrooms/office-site-b/overview-office-site-b-meeting-rooms.md
  note: Use the site overview to map this shared guide to the applicable room set in <OFFICE_SITE_B>.
- title: <VIDEO_CONFERENCING_PLATFORM> Enabled Meeting Room - User Guide for <ROOM_NAME_F>
  article_id: kb-troubleshooting-audio-video-boardrooms-office-site-a-video-conferencing-platform-enabled-meeting-room-user-guide-for-room-name-f
  path: knowledge/troubleshooting/audio-video/boardrooms/office-site-a/video-conferencing-platform-enabled-meeting-room-user-guide-for-room-name-f.md
  note: Keep using the room-specific article when <ROOM_NAME_F> requires local images or notes in addition to the shared controller workflow.
change_log:
- date: 2026-04-07
  summary: Created a shared touch-controller room guide to replace repeated site-specific copies.
  author: codex
---

## Room Introduction

Use this guide for rooms that provide:

- Room video bar with camera, microphones, and speakers
- Touch controller for room-system meeting control
- Native join options for <VIDEO_CONFERENCING_PLATFORM> and other approved meeting services
- Wired or wireless content-sharing options tied to the room system

If the room instead depends on connecting a laptop directly to the display and USB peripherals, use [Standard AV Room User Guide](standard-av-room-user-guide.md).

## One-Touch Join

When the meeting is scheduled with the room resource:

1. Wake the touch controller if needed.
2. Tap the scheduled meeting name on the controller.
3. Confirm the room system joins on the connected display.

## Manual Join

For meetings that were not booked with the room:

1. Tap `Join` on the touch controller.
2. Enter the meeting code or meeting ID and passcode if required.
3. Confirm the meeting launches on the room display before inviting in-room participants to speak.

## Instant Meetings

1. Tap `New Meeting` or the equivalent room-system option on the controller.
2. Invite participants from the approved room-system workflow.
3. Share the meeting link or code with remote participants if the meeting was created ad hoc.

## Audio And Content Controls

- Use the touch controller to mute or unmute room microphones.
- Adjust room speaker volume from the controller rather than from a participant laptop.
- Use the room's approved wired or wireless content-sharing path.
- Avoid enabling laptop microphone or speaker audio in parallel with the room system.

## Troubleshooting Tips

| Issue | Check |
| --- | --- |
| One-touch join missing | Confirm the room was invited on the calendar event and the controller is online. |
| Cannot join manually | Re-enter the meeting code, then verify the room system has network connectivity. |
| No room audio | Check controller mute state and the room volume slider before changing client settings. |
| Camera framing is wrong | Use the room camera controls or remote where available. |
| Sharing does not appear | Verify the room is on the correct sharing input or controller workflow for wired or wireless presentation. |

## Site Deltas

- Use site overview pages to map this controller workflow to room names and local support contacts.
- Keep room-specific image walkthroughs or exceptional hardware instructions in the unique room article only when the shared steps are insufficient.
