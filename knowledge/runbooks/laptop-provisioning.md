---
id: kb-runbook-laptop-provisioning
title: Laptop Provisioning
canonical_path: knowledge/runbooks/laptop-provisioning.md
summary: Prepare and hand off a standard employee laptop with inventory, identity, and compliance checks completed.
type: runbook
status: active
owner: Endpoint Engineering
source_type: native
team: Workplace Engineering
systems:
  - Jamf Pro
  - Microsoft Intune
  - Endpoint Inventory
  - Ticketing Queue
services:
  - Endpoint Provisioning
  - Onboarding
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
prerequisites:
  - Approved onboarding ticket with start date, manager, and hardware profile.
  - Spare laptop in supported inventory status.
  - Admin access to the endpoint management platform for the target device type.
steps:
  - Confirm the ticket includes the employee name, manager, office location, and requested ship or pickup date.
  - Verify the device serial number and asset tag are unassigned in Endpoint Inventory before imaging or enrollment.
  - Enroll the device in Jamf Pro for macOS or Microsoft Intune for Windows and apply the baseline security profile.
  - Install the standard productivity package, VPN client, endpoint protection agent, and remote support tooling.
  - Sign in with the staging account only long enough to confirm encryption, disk health, and MDM compliance.
  - Update Endpoint Inventory and the onboarding ticket with the serial number, asset tag, assigned user, and handoff status.
verification:
  - Device reports compliant in the management console.
  - Local admin and recovery credentials are escrowed according to policy.
  - Asset record and onboarding ticket show the same serial number and assigned user.
rollback:
  - If enrollment fails, wipe the device and return it to unassigned inventory status.
  - Remove the assigned user from Endpoint Inventory if the handoff is cancelled.
  - Return the ticket to the onboarding queue with a clear failure note and next action.
related_articles:
  - kb-onboarding-employee-onboarding-checklist
  - kb-access-software-access-request
replaced_by: null
retirement_reason: null
references:
  - title: Onboarding checklist
    article_id: kb-onboarding-employee-onboarding-checklist
    path: knowledge/onboarding/employee-onboarding-checklist.md
    note: Use this checklist to confirm the laptop handoff is aligned with the broader onboarding workflow.
  - title: Asset inventory record
    note: Confirm serial number, asset tag, and assigned user match before closing the request.
change_log:
  - date: 2026-04-07
    summary: Initial seed article.
    author: Repository bootstrap
---

## Scope

Use this runbook for standard employee laptops. Do not use it for executive, kiosk, or lab devices that require a separate build profile.

## Escalation

Escalate to Workplace Engineering if the device fails encryption, cannot complete enrollment, or is already assigned to another user in inventory.
