---
id: kb-troubleshooting-audio-video-overview-and-maintenance-ticketing-system-workflow-av-automation-workflow
title: <TICKETING_SYSTEM> Workflow AV Automation Workflow
canonical_path: knowledge/troubleshooting/audio-video/overview-and-maintenance/ticketing-system-workflow-av-automation-workflow.md
summary: The following automations power the Global AV Maintenance SOP . They ensure all regional AV sweep
  activity (<OFFICE_SITE_C>, <OFFICE_SITE_B>, <OFFICE_SITE_A>) rolls up into a single global issue for
  consistent tracking, visibility, and...
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <TICKETING_SYSTEM> Workflow AV Automation Workflow
team: Workplace Engineering
systems:
- <TICKETING_SYSTEM>
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: '2025-11-21'
updated: '2025-11-24'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Collaboration
symptoms:
- The following automations power the Global AV Maintenance SOP . They ensure all regional AV sweep activity
  (<OFFICE_SITE_C>, <OFFICE_SITE_B>, <OFFICE_SITE_A>) rolls up into a single global issue for consistent
  tracking, visibility, and...
scope: 'Legacy source does not declare structured scope. Summary: The following automations power the
  Global AV Maintenance SOP . They ensure all regional AV sweep activity (<OFFICE_SITE_C>, <OFFICE_SITE_B>,
  <OFFICE_SITE_A>) rolls up into a single global issue for consistent tracking, visibility, and...'
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

The following automations power the **Global AV Maintenance SOP** . They ensure all regional AV sweep activity (<OFFICE_SITE_C>, <OFFICE_SITE_B>, <OFFICE_SITE_A>) rolls up into a single **global issue** for consistent tracking, visibility, and reporting.

# **Monthly Regional Sweep Creation**

### **Trigger:**

- Runs automatically on the first business day of each month at 9:00 AM local time.
- Checks if a sweep ticket already exists for the region.
- If not, creates a new parent issue for that month.

### **Action:**

- Creates regional tasks with:
- Summary: Monthly AV Conference Room Hardware Sweep – [Region] – {{Month Year}}
- Labels: region-sea, region-yvr, region-hyd, and room-sweep-YYYY-MM
- Links to the correct regional Tech Form
- Issue type: Task within the AV project

### **Purpose:**

Establishes regional sweep tickets automatically, ensuring monthly consistency without manual setup.

# **Global Rollup Creation**

### **Trigger:**

- Scheduled monthly automation (9 AM Sydney time).
- Searches for existing issues labeled global-sweep and room-sweep-YYYY-MM.
- If no match, creates a new Global Rollup issue.

### **Action:**

- Creates a Global Rollup issue titled:
- Global AV Monthly Maintenance – {{Month Year}}
- Labels: global-sweep, room-sweep-YYYY-MM
- Description: “Rollup for <OFFICE_SITE_C>, <OFFICE_SITE_B>, <OFFICE_SITE_A> – {{Month Year}}”

### **Purpose:**

Acts as the umbrella issue for all regional sweeps, consolidating data and providing a single view of global AV health.

# **Subtask & Status Automation**

### **Trigger:**

- Activated when a new issue is created in the AV project.
- Conditions:
- Excludes unrelated issue types (e.g., Service Desk requests).
- Checks summary and description for:
- Regional keywords (<OFFICE_SITE_C>, <OFFICE_SITE_B>, <OFFICE_SITE_A>, or <OFFICE_SITE_C>/YVR/HYD)
- Status keywords (Needs Maintenance or Ready for Use)

### **Actions:**

- **If “Needs Maintenance” detected:**
  - Links the issue to the correct regional parent sweep.
    - Adds the label room-sweep-YYYY-MM.
    - Keeps the issue open for technician review.
- **If “Ready for Use” detected:**
  - Links to the correct regional parent sweep.
    - Adds the label room-sweep-YYYY-MM.
    - Automatically transitions the issue to Resolved.

### **Purpose:**

This ensures technician submissions automatically associate with the right region and status, maintaining real-time accuracy without manual linking.

# **Linking Regional Issues to the Global Rollup**

### **Trigger:**

Manual or scheduled job that runs once all regional tickets exist.

### **Action:**

- Finds the active Global Rollup issue (global-sweep + room-sweep-YYYY-MM).
- Finds all regional sweep tickets with labels (region-sea, region-yvr, region-hyd).
- Creates parent-child issue links between them.

### **Purpose:**

Ensures every regional sweep issue is connected to the global rollup, providing unified tracking and reporting.

# **Workflow Diagram**

[CDATA[┌─────────────────────────────────────────────┐ │ Global Rollup (global-sweep, room-sweep) │ │ e.g., Global AV Monthly Maintenance - Nov 25 │ └───────────────┬─────────────────────────────┘ │ ▼ ┌─────────────────────────────────────────────┐ │ Regional Sweeps (<OFFICE_SITE_C> / YVR / HYD) │ │ region-[code], room-sweep-[month] │ └───────────────┬─────────────────────────────┘ │ ▼ ┌────────────────────────────┬────────────────────────────┐ │ Needs Maintenance │ Ready for Use │ │ - Linked automatically │ - Linked & auto-resolved │ │ - Open for tech resolution │ - Closed in <TICKETING_SYSTEM> │ └────────────────────────────┴────────────────────────────┘ ]]

# **Reporting & Benefits**

### **Automatically Captured Metrics:**

- Total rooms swept per region per month
- Maintenance vs. Ready-for-Use ratio
- Average time to resolution
- Recurring issue frequency

### **Key Benefits:**

- No manual linking or tracking required
- Real-time visibility across all regions
- Consistent monthly structure supports analytics
- Enables proactive replacement and planning decisions

### <TICKETING_SYSTEM> Automation Exports
