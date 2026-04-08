---
id: kb-troubleshooting-audio-video-boardrooms-standard-av-room-user-guide
title: Standard AV Room User Guide
canonical_path: knowledge/troubleshooting/audio-video/boardrooms/standard-av-room-user-guide.md
summary: Shared operator guide for meeting rooms that use a laptop-connected USB conference video bar and TV display.
knowledge_object_type: known_error
legacy_article_type: troubleshooting
status: active
owner: service_owner
source_type: native
source_system: repository
source_title: Standard AV Room User Guide
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
- Operators need one consistent procedure for laptop-driven meeting rooms that share the same USB video bar and TV workflow across multiple sites.
scope: Use this guide for standard AV rooms where the user joins from their laptop and connects both the room display and the USB conference video bar locally.
cause: Legacy site articles copied the same connection, meeting, and troubleshooting steps into multiple room-set pages, which made shared updates drift-prone.
diagnostic_checks:
- Confirm the room uses a laptop-connected USB conference video bar and TV rather than a touch-controller room system.
- Verify the display path and the USB conference video bar path are both connected before troubleshooting application settings.
- Escalate to the site-specific overview if the room hardware does not match this shared setup.
mitigations:
- Use this shared guide for the common operator workflow and keep site-specific room lists in local overview pages.
- Escalate to the owning team if a site introduces a materially different standard AV room design.
permanent_fix_status: unknown
citations:
- article_id: kb-troubleshooting-audio-video-boardrooms-office-site-a-av-enabled-meeting-rooms-user-guide
  source_title: AV Enabled Meeting Rooms - User Guide
  source_type: document
  source_ref: knowledge/troubleshooting/audio-video/boardrooms/office-site-a/av-enabled-meeting-rooms-user-guide.md
  note: Imported source used to consolidate the repeated standard AV room procedure.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
- article_id: kb-troubleshooting-audio-video-boardrooms-office-site-b-meeting-room-user-guide-room-set-a
  source_title: Meeting Room User Guide - <ROOM_NAME_A>, <ROOM_NAME_B>, <ROOM_NAME_C>
  source_type: document
  source_ref: knowledge/troubleshooting/audio-video/boardrooms/office-site-b/meeting-room-user-guide-room-set-a.md
  note: Matching site variant used during consolidation.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-troubleshooting-audio-video-boardrooms-index
- kb-troubleshooting-audio-video-boardrooms-office-site-a-overview-office-site-a-meeting-rooms
- kb-troubleshooting-audio-video-boardrooms-office-site-b-overview-office-site-b-meeting-rooms
prerequisites:
- Confirm the room uses a laptop-connected USB conference video bar and TV display.
- Confirm the operator can identify the matching room from the local site overview before acting.
steps:
- Connect the room video bar and display paths to the laptop.
- Launch the meeting client, select the room peripherals, and complete the meeting or sharing workflow.
- Use the linked site overview if room naming or local room-mapping context is needed.
verification:
- Audio, video, and screen sharing work through the room peripherals.
- The operator can map the shared guide to the correct site room without ambiguity.
rollback:
- Disconnect the room peripherals and restore the room to its pre-session state if setup fails.
- Escalate to the site owner if the room hardware does not match the shared standard.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
related_articles:
- kb-troubleshooting-audio-video-boardrooms-index
- kb-troubleshooting-audio-video-boardrooms-office-site-a-overview-office-site-a-meeting-rooms
- kb-troubleshooting-audio-video-boardrooms-office-site-b-overview-office-site-b-meeting-rooms
references:
- title: Overview - <OFFICE_SITE_A> Meeting Rooms
  article_id: kb-troubleshooting-audio-video-boardrooms-office-site-a-overview-office-site-a-meeting-rooms
  path: knowledge/troubleshooting/audio-video/boardrooms/office-site-a/overview-office-site-a-meeting-rooms.md
  note: Use the site overview to map this shared guide to room names in <OFFICE_SITE_A>.
- title: Overview - <OFFICE_SITE_B> Meeting Rooms
  article_id: kb-troubleshooting-audio-video-boardrooms-office-site-b-overview-office-site-b-meeting-rooms
  path: knowledge/troubleshooting/audio-video/boardrooms/office-site-b/overview-office-site-b-meeting-rooms.md
  note: Use the site overview to map this shared guide to room names in <OFFICE_SITE_B>.
change_log:
- date: 2026-04-07
  summary: Created a shared standard AV room guide to replace repeated site-specific copies.
  author: codex
---

## Room Introduction

Use this guide for meeting rooms that share the same laptop-driven setup:

- USB conference video bar for camera, microphone, and speakers
- TV display for meeting video and screen sharing
- One cable path for the display connection
- One cable path for the USB conference video bar

If the room instead has a dedicated touch controller and room-system join flow, use [Touch Controller Room User Guide](touch-controller-room-user-guide.md).

## Joining A Meeting

1. Connect the USB cable from the room video bar to the laptop.
2. Connect the display cable to the laptop.
3. Use the TV remote to select the correct HDMI input.
4. Launch the <VIDEO_CONFERENCING_PLATFORM> app on the laptop.
5. Join the scheduled meeting or start a new meeting from the laptop.

## During The Meeting

Confirm the <VIDEO_CONFERENCING_PLATFORM> client is using the USB conference video bar for:

- Camera
- Microphone
- Speaker, unless the room uses the TV speaker for louder playback

Use the device picker next to the microphone or camera controls to correct the room peripherals if the wrong device is selected.

## Audio Controls

- Mute and unmute from the meeting client.
- Adjust TV speaker volume with the room remote if the TV is the selected speaker path.
- Adjust application speaker volume in the meeting client when the USB conference video bar is the active speaker.
- Avoid using the laptop microphone and room microphone at the same time to prevent echo.

## Screen Sharing

1. Click the screen-share control in the meeting client.
2. Select the screen or window to present.
3. Confirm the shared content appears on both the laptop and the room display.

## Ending The Meeting

1. Leave or end the meeting from the meeting client.
2. Disconnect the room cables from the laptop.
3. Turn off the TV if the site standard requires it after the meeting.

## Troubleshooting Tips

| Issue | Check |
| --- | --- |
| No video | Confirm the camera is set to the USB conference video bar in <VIDEO_CONFERENCING_PLATFORM>. |
| No sound | Verify the correct speaker is selected and adjust either the TV or application volume. |
| Nothing on TV | Re-seat the display cable and confirm the correct HDMI input is selected. |
| Camera not detected | Reconnect the USB conference video bar cable and reselect the camera in the meeting client. |
| Echo or feedback | Use only one speaker path and mute any unused laptop audio devices. |

## Site Deltas

- Use the site overview pages for room names, room counts, and local escalation notes.
- Do not copy this shared procedure into new site folders unless the operational steps materially differ.
