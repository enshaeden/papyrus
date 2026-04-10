---
id: kb-assets-audits-and-recordkeeping-not-in-endpoint-enrollment-portal
title: Not in <ENDPOINT_ENROLLMENT_PORTAL>
canonical_path: knowledge/assets/audits-and-recordkeeping/not-in-endpoint-enrollment-portal.md
summary: To ensure all devices are properly accounted for in <ENDPOINT_ENROLLMENT_PORTAL>, a new automation
  has been implemented in <ASSET_MANAGEMENT_SYSTEM>. This automation tracks devices that are missing from
  <ENDPOINT_ENROLLMENT_PORTAL> and alerts the team when action is required.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Not in <ENDPOINT_ENROLLMENT_PORTAL>
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
created: '2026-02-17'
updated: '2026-02-17'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
prerequisites:
- Confirm the device, asset record, and office or shipping context before taking action.
- Verify you have the required inventory, MDM, or ticketing access for the task.
steps:
- Review the imported procedure body below and confirm the documented scope matches the task at hand.
- Execute the documented steps in order and record the outcome in the relevant ticket or audit trail.
- Stop and escalate if approvals, prerequisites, or expected checkpoints do not match the live request.
verification:
- The expected outcome described in the procedure is confirmed in the target system or ticket record.
- Completion notes, exceptions, and evidence are recorded in the relevant audit or support workflow.
rollback:
- Revert any reversible change described in the procedure if verification fails.
- Pause the workflow and escalate when the documented rollback path is unclear or incomplete.
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
- kb-assets-audits-and-recordkeeping-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-audits-and-recordkeeping-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Tracking Devices Missing from <ENDPOINT_ENROLLMENT_PORTAL>**

To ensure all devices are properly accounted for in <ENDPOINT_ENROLLMENT_PORTAL>, a new automation has been implemented in <ASSET_MANAGEMENT_SYSTEM>. This automation tracks devices that are missing from <ENDPOINT_ENROLLMENT_PORTAL> and alerts the team when action is required.

## **How It Works:**

- **New Field: "Missing From <ENDPOINT_ENROLLMENT_PORTAL>"** A new field called "Missing From <ENDPOINT_ENROLLMENT_PORTAL>" has been added to the Asset Tracker. When a device is missing from <ENDPOINT_ENROLLMENT_PORTAL>, this field should be checked.
- **Automation Notification:**
  1. Any device marked as "Missing From <ENDPOINT_ENROLLMENT_PORTAL>" will trigger a notification in the **<QUEUE_NAME>** channel when its status changes.
    2. If you see a notification related to a Mac you're handling, please prioritize adding the device to <ENDPOINT_ENROLLMENT_PORTAL>.
- **Actions:**
  1. **If the device is missing from <ENDPOINT_ENROLLMENT_PORTAL>:**
      - Check the "Missing From <ENDPOINT_ENROLLMENT_PORTAL>" field.
          - Once the device is added to <ENDPOINT_ENROLLMENT_PORTAL>, **uncheck** the "Missing From <ENDPOINT_ENROLLMENT_PORTAL>" field.
    2. **If the device is not in <ENDPOINT_ENROLLMENT_PORTAL> but should be:**
      - Ensure the "Missing From <ENDPOINT_ENROLLMENT_PORTAL>" field is checked.

#### **Best Practices:**

- Always prioritize adding devices to <ENDPOINT_ENROLLMENT_PORTAL> when notified, to maintain accurate inventory tracking.
- Regularly monitor the **<QUEUE_NAME>** channel to stay on top of missing devices and updates.
