---
id: kb-troubleshooting-audio-video-overview-and-maintenance-monthly-av-sweep-process
title: Monthly AV Sweep Process
canonical_path: knowledge/troubleshooting/audio-video/overview-and-maintenance/monthly-av-sweep-process.md
summary: "The Monthly AV Sweep is the foundation of <COMPANY_NAME>\u2019s proactive conference room maintenance\
  \ program."
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Monthly AV Sweep Process
team: Systems Engineering
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
- "The Monthly AV Sweep is the foundation of <COMPANY_NAME>\u2019s proactive conference room maintenance\
  \ program."
scope: "Legacy source does not declare structured scope. Summary: The Monthly AV Sweep is the foundation\
  \ of <COMPANY_NAME>\u2019s proactive conference room maintenance program."
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
  source_ref: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-troubleshooting-audio-video-overview-and-maintenance-index
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
- kb-troubleshooting-audio-video-overview-and-maintenance-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Monthly AV Sweep Process for Technicians**

The Monthly AV Sweep is the foundation of <COMPANY_NAME>’s proactive conference room maintenance program.

Each month, technicians complete standardized inspections across all AV-enabled rooms to ensure systems are fully functional, consistent, and ready for use.

The following process outlines the complete workflow — from preparation through verification and documentation.

# Pre-Sweep Preparation

Before performing any inspections:

- Verify the monthly sweep ticket in <TICKETING_SYSTEM>
- Navigate to the AV project board.
- Confirm a parent issue exists for the current month, e.g.,
- Monthly AV Conference Room Hardware Sweep – <OFFICE_SITE_C> – November 2025.
- If not, automation will generate it automatically on the first business day of the month.
- Review open issues
- Check if any subtasks from the previous month remain unresolved.
- Note repeat offenders or recurring problem rooms for special attention.

# Prepare required materials

- HDMI and USB-C cables
- Laptop with <VIDEO_CONFERENCING_PLATFORM> and <COLLABORATION_PLATFORM> meeting
- Cleaning wipes, cable ties, and spare adapters (if applicable)

# Conducting Room Inspections

Each inspection should be methodical and consistent. The goal is not only to verify functionality but also to identify early warning signs of degradation (loose cables, lagging connections, degraded audio).

### A. Verify Core Components

| **Category** | **Actions** |
| --- | --- |
| Displays | Power on, confirm correct input source (HDMI or wireless), ensure clarity and resolution. |
| Audio (Speakers & Mics) | Test with laptop or conference-room hardware; verify no distortion or dropouts. |
| Cameras | Confirm video feed is detected; test pan, tilt, and <VIDEO_CONFERENCING_PLATFORM> functions if supported. |
| conference-room hardware Systems | Check boot time, registration, and network connectivity. Verify touch or button controls respond properly. |
| Connectivity | Test both wired (HDMI/USB-C) and wireless casting (wireless display adapter or wireless presentation hardware). |
| Network | Confirm strong Wi-Fi or Ethernet connectivity for video conferencing. |
| Room Condition | Check cable management, signage visibility, and cleanliness. |

### **B. Record All Observations**

Use the regional Tech Sweep Form to record inspection results:

- **<OFFICE_SITE_C>:** [<INTERNAL_URL>](<INTERNAL_URL>)
- **<OFFICE_SITE_B>:** [<INTERNAL_URL>](<INTERNAL_URL>)
- **<OFFICE_SITE_A>:** [<INTERNAL_URL>](<INTERNAL_URL>)

Complete one form per room, even if no issues are found.

**Include:**

- Date and technician name
- Room identifier
- Each component’s status
- Comments or observations
- Select either “Ready for Use” or “Needs Maintenance”

# Submitting Form Data & <TICKETING_SYSTEM> Integration

When a technician submits a Tech Form:

- <TICKETING_SYSTEM> automation detects the new submission and links it automatically to that region’s monthly parent ticket.
- The automation applies the correct month’s label (e.g., room-sweep-2025-11) and region (region-sea, region-yvr, or region-hyd).
- If the form includes “Needs Maintenance,” <TICKETING_SYSTEM> creates a subtask for technician follow-up.
- If the form includes “Ready for Use,” <TICKETING_SYSTEM> transitions the subtask to Resolved, marking the room verified for the month.
- Note: Technicians no longer need to manually create <TICKETING_SYSTEM> tickets for routine sweep reports. The integration handles this automatically.

# Maintenance & Troubleshooting

- If an issue is flagged as Needs Maintenance:
- Begin troubleshooting immediately (within the same day, if possible).
- Common fixes include cable reseating, firmware restarts, or conference-room hardware re-registration.
- For hardware failure:
- Document the issue in <TICKETING_SYSTEM> (with clear notes and photos if possible).
- Order replacements or log a vendor ticket if required.
- Leave the room temporarily marked as “Out of Service” until resolved.

**After resolution:**

- Re-test all equipment.
- Submit a new Tech Form entry marking the room Ready for Use.
- <TICKETING_SYSTEM> will automatically close or transition the subtask to Resolved.

# End-of-Month Review

**At the end of the sweep cycle:**

Return to your monthly parent <TICKETING_SYSTEM> issue.

**Verify:**

- All room subtasks are either Resolved or linked as carryovers to the next month.
- The total number of inspected rooms matches your office directory.
- Add a summary comment in <TICKETING_SYSTEM> documenting:
- Rooms inspected
- Issues found/resolved
- Equipment replaced
- Repeat problem areas (if any)

This creates a clear historical record that rolls up into the Global AV Monthly Maintenance parent issue for global visibility.
