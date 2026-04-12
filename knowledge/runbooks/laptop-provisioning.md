---
id: kb-runbooks-laptop-provisioning
title: Laptop Provisioning
canonical_path: knowledge/runbooks/laptop-provisioning.md
summary: Prepare and hand off a standard employee laptop with inventory, identity, and compliance checks
  completed.
knowledge_object_type: runbook
legacy_article_type: runbook
object_lifecycle_state: active
owner: it_operations
source_type: native
source_system: repository
source_title: Laptop Provisioning
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
- <TICKETING_SYSTEM>
tags:
- endpoint
- macos
- windows
- onboarding
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: it_ops
related_services:
- Endpoint Provisioning
- Onboarding
prerequisites:
- Approved onboarding ticket with start date, manager, and hardware profile.
- Spare laptop in supported inventory status.
- Admin access to the endpoint management platform for the target device type.
steps:
- Confirm the ticket includes the employee name, manager, office location, and requested ship or pickup
  date.
- 'Verify the device serial number: <SERIAL_NUMBER>'
- Enroll the device in <ENDPOINT_MANAGEMENT_PLATFORM> for macOS or <PRODUCTIVITY_PLATFORM> <ENDPOINT_MANAGEMENT_PLATFORM>
  for Windows and apply the baseline security profile.
- Install the standard productivity package, VPN client, endpoint protection agent, and remote support
  tooling.
- Sign in with the staging account only long enough to confirm encryption, disk health, and MDM compliance.
- 'Update Endpoint Inventory and the onboarding ticket with the serial number: <SERIAL_NUMBER>'
verification:
- Device reports compliant in the management console.
- Local admin and recovery credentials are escrowed according to policy.
- 'Asset record and onboarding ticket show the same serial number: <SERIAL_NUMBER>'
rollback:
- If enrollment fails, wipe the device and return it to unassigned inventory status.
- Remove the assigned user from Endpoint Inventory if the handoff is cancelled.
- Return the ticket to the onboarding queue with a clear failure note and next action.
citations:
- article_id: kb-onboarding-employee-onboarding-checklist
  source_title: Onboarding checklist
  source_type: document
  source_ref: knowledge/user-lifecycle/onboarding-new-hires/employee-onboarding-checklist.md
  note: Use this checklist to confirm the laptop handoff is aligned with the broader onboarding workflow.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
- article_id: null
  source_title: Asset inventory record
  source_type: document
  source_ref: Asset inventory record
  note: 'Confirm serial number: <SERIAL_NUMBER>'
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-onboarding-employee-onboarding-checklist
- kb-access-software-access-request
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
- Onboarding
related_articles:
- kb-onboarding-employee-onboarding-checklist
- kb-access-software-access-request
references:
- title: Onboarding checklist
  article_id: kb-onboarding-employee-onboarding-checklist
  path: knowledge/user-lifecycle/onboarding-new-hires/employee-onboarding-checklist.md
  note: Use this checklist to confirm the laptop handoff is aligned with the broader onboarding workflow.
- title: Asset inventory record
  note: 'Confirm serial number: <SERIAL_NUMBER>'
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Scope

Use this runbook for standard employee laptops. Do not use it for executive, kiosk, or lab devices that require a separate build profile.

## Escalation

Escalate to Workplace Engineering if the device fails encryption, cannot complete enrollment, or is already assigned to another user in inventory.
