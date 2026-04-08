---
id: kb-troubleshooting-audio-video-boardrooms-office-site-a-av-enabled-meeting-rooms-user-guide
title: AV Enabled Meeting Rooms - User Guide
canonical_path: knowledge/troubleshooting/audio-video/boardrooms/office-site-a/av-enabled-meeting-rooms-user-guide.md
summary: The AV-enabled rooms in this room set share the same setup.
knowledge_object_type: known_error
legacy_article_type: troubleshooting
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: AV Enabled Meeting Rooms - User Guide
team: Workplace Engineering
systems:
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: '2025-11-27'
updated: '2025-11-27'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Collaboration
symptoms:
- The AV-enabled rooms in this room set share the same setup.
scope: 'Legacy source does not declare structured scope. Summary: The AV-enabled rooms in this room set
  share the same setup.'
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
- kb-troubleshooting-audio-video-boardrooms-office-site-a-index
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
- kb-troubleshooting-audio-video-boardrooms-office-site-a-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Room Introduction

These AV-enabled rooms share the same setup.

These conference rooms include:

- **USB conference video bar** (camera, microphone, and speaker)
- **TV display** for meetings and screen sharing
- **USB-C cable** to connect your laptop to the TV
- **USB-C cable** to connect your laptop to the USB conference video bar

You will use your **laptop** to join <VIDEO_CONFERENCING_PLATFORM> meetings. The TV and USB conference video bar enhance the experience by providing larger video and clearer sound.

# Joining a Meeting

1. Plug the **USB cable** from the USB conference video bar into your laptop.
2. Plug the **USB-C cable** into your laptop to connect it to TV
3. Use the **TV remote** to select the correct **HDMI input** .
4. Launch the **<VIDEO_CONFERENCING_PLATFORM> app** on your laptop.
5. Join your scheduled meeting or start a new one.

# During the Meeting

### Audio and Video Setup in <VIDEO_CONFERENCING_PLATFORM>

Make sure <VIDEO_CONFERENCING_PLATFORM> is using the USB conference video bar for all inputs and outputs:

- **Camera** : Select **USB conference video bar**
- **Microphone** : Select **USB conference video bar**
- **Speaker** : Select **USB conference video bar** (or choose your **TV** for louder room audio)

To confirm or change:

- Click the small **arrow next to the microphone or video icon** in <VIDEO_CONFERENCING_PLATFORM>.
- Choose the appropriate device from the list.

# Audio Controls

- Use the **mute/unmute** button in <VIDEO_CONFERENCING_PLATFORM> to control your microphone.
- The **conference-room microphone** clearly picks up voices in the room.
- If using the **R30’s speaker** , adjust the volume from the **<VIDEO_CONFERENCING_PLATFORM> audio settings** :
  - In <VIDEO_CONFERENCING_PLATFORM>, go to **Settings > Audio > Speaker Volume** and drag the slider.
- If using the **TV’s speaker** , use the **TV remote** to adjust volume.

# Sharing Your Screen

To share your screen during the meeting:

1. Click **“Share Screen”** in the <VIDEO_CONFERENCING_PLATFORM> toolbar.
2. Select the screen or window you want to share.
3. The shared content will appear on both your laptop and the TV.

# Ending the Meeting

1. Click **“Leave”** or **“End Meeting”** in <VIDEO_CONFERENCING_PLATFORM>.
2. Unplug the **USB** and **HDMI** cables from your laptop.
3. Turn off the TV using the remote.

# Troubleshooting Tips

| Column 1 | Column 2 |
| --- | --- |
| **Issue** | **Solution** |
| No Video | Confirm camera is set to USB conference video bar in <VIDEO_CONFERENCING_PLATFORM> |
| No Sound | Check speaker settings in <VIDEO_CONFERENCING_PLATFORM>; adjust volume in <VIDEO_CONFERENCING_PLATFORM> or on TV |
| Camera not working | Make sure correct camera is selected in <VIDEO_CONFERENCING_PLATFORM>- ‘USB conference video bar’ |
| Nothing on TV | Ensure HDMI cable is secure and correct input is selected |
| Echo or feedback | Use only one speaker source; mute laptop mic if needed |
| Microphone issues | Ensure you are in the Camera view to be audible |
