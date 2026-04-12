---
id: kb-troubleshooting-audio-video-overview-and-maintenance-global-av-maintenance-sop-overview
title: Global AV Maintenance SOP Overview
canonical_path: knowledge/troubleshooting/audio-video/overview-and-maintenance/global-av-maintenance-sop-overview.md
summary: This Standard Operating Procedure (SOP) defines the global process for performing, documenting,
  and tracking monthly AV conference room sweeps across all <COMPANY_NAME> offices. The sweeps ensure
  that AV systems are fully...
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Global AV Maintenance SOP Overview
team: Workplace Engineering
systems:
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: '2025-11-21'
updated: '2026-01-21'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Collaboration
symptoms:
- This Standard Operating Procedure (SOP) defines the global process for performing, documenting, and
  tracking monthly AV conference room sweeps across all <COMPANY_NAME> offices. The sweeps ensure that
  AV systems are fully...
scope: 'Legacy source does not declare structured scope. Summary: This Standard Operating Procedure (SOP)
  defines the global process for performing, documenting, and tracking monthly AV conference room sweeps
  across all <COMPANY_NAME> offices. The sweeps ensure that AV systems are fully...'
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

# Purpose

This Standard Operating Procedure (SOP) defines the global process for performing, documenting, and tracking monthly AV conference room sweeps across all <COMPANY_NAME> offices. The sweeps ensure that AV systems are fully functional, issues are identified proactively, and employees experience consistent, high-quality hybrid meetings.

Each region addressed issues reactively—often relying on user reports after a meeting failure—leading to inconsistent maintenance, untracked downtime, and poor visibility into global AV health.

Implementing this Global Conference Room Sweep SOP improves operations by:

- Establishing a proactive monthly workflow for AV health.
- Standardizing maintenance and reporting across all regions.
- Using <TICKETING_SYSTEM> automation for transparent, trackable issue resolution.
- Reducing end-user downtime and meeting interruptions.
- Enabling data-driven decisions through global reporting and trend analysis.

This SOP transitions <COMPANY_NAME> from a reactive support model to a structured, preventative AV management framework—ensuring predictable meeting experiences across all global offices.

# Scope

This SOP applies to:

- IT Support Technicians at all <COMPANY_NAME> offices globally.
- Regional IT Leads overseeing AV health and compliance.
- End Users reporting AV issues using local QR codes or forms.

Applies to all global offices with conference room AV infrastructure:

- <OFFICE_SITE_C> (primary office)
- <OFFICE_SITE_B>
- <OFFICE_SITE_A>

# Roles & Responsibilities

| **Roles** | **Responsibilities** |
| --- | --- |
| IT Support Technicians (Global) | Monitor sweep completion, oversee <TICKETING_SYSTEM> ticket automation, and escalate recurring issues. |
| Regional IT Leads | Monitor sweep completion, oversee <TICKETING_SYSTEM> ticket automation, and escalate recurring issues. |
| End Users | Report AV issues via QR codes or the Global End User Request Form. |

# [**<TICKETING_SYSTEM> Workflow Automation**](<INTERNAL_URL>)

<TICKETING_SYSTEM> automation drives the entire process — from ticket creation to reporting.

| Automation | Purpose |
| --- | --- |
| **Monthly Sweep Creation (<OFFICE_SITE_C>/YVR/HYD)** | Creates regional sweep tickets automatically on the first business day of each month. |
| **Global Rollup Creation** | Generates a global “umbrella” issue linking all regional sweeps together. |
| **Task Automation** | Creates and links subtasks based on Tech Form input — “Needs Maintenance” or “Ready for Use.” |
| **Linking Regionals to Global** | Connects all regional sweep tickets to the monthly global issue for consolidated reporting. |

**Labels Used:** `region-sea` , `region-yvr` , `region-hyd` , `room-sweep-YYYY-MM` , `global-sweep`

---

# [**Monthly AV Sweep Process**](<INTERNAL_URL>)

1. **Preparation**
  - Confirm monthly sweep tickets exist in <TICKETING_SYSTEM>.
    - Gather tools: HDMI/USB-C cables, laptop (<VIDEO_CONFERENCING_PLATFORM> & <COLLABORATION_PLATFORM> meeting), and cleaning supplies.
2. **Room Inspection**
  - Inspect displays, cameras, audio, Polycoms, and connectivity.
    - Record findings in the **regional Tech Form** (one per room).
3. **Form Submission**
  - “Needs Maintenance” → Creates task for technician work.
    - “Ready for Use” → Auto-resolves and logs inspection as complete.
4. **End of Month**
  - Verify all tasks are closed or carried over.
    - Add summary comment to the regional <TICKETING_SYSTEM> ticket.

**Outcome:** All sweep data rolls into the **Global AV Maintenance** issue for reporting and visibility.

---

# [**Regional AV Operations**](<INTERNAL_URL>)

| Region | Sweep Time | Tech Form | Focus Areas |
| --- | --- | --- | --- |
| [**<OFFICE_SITE_C> (primary office)**](<INTERNAL_URL>) | 9:00 AM PST | [Form](<INTERNAL_URL>) | conference-room hardware connectivity, HDMI stability, wireless display adapter pairing |
| [**<OFFICE_SITE_B>**](<INTERNAL_URL>) | 9:00 AM PST | [Form](<INTERNAL_URL>) | Microphone calibration, wireless presentation hardware/wireless display adapter wireless casting |
| [**<OFFICE_SITE_A>**](<INTERNAL_URL>) | 9:00 AM IST | [Form](<INTERNAL_URL>) | room video firmware, wireless presentation hardware base pairing, dual display sync |

# **Key Benefits**

- Global consistency in AV maintenance
- Full visibility via automated <TICKETING_SYSTEM> tracking
- Reduced meeting downtime
- Streamlined reporting and accountability
