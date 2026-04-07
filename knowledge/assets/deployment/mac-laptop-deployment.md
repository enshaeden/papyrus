---
id: kb-assets-deployment-mac-laptop-deployment
title: Mac laptop Deployment
canonical_path: knowledge/assets/deployment/mac-laptop-deployment.md
summary: All Mac laptops are configured through the automated device enrollment. Once purchased from an approved device supplier, devices are added to <ENDPOINT_ENROLLMENT_PORTAL> (<ENDPOINT_ENROLLMENT_PORTAL>) and are automatically enrolled in our <ENDPOINT_MANAGEMENT_PLATFORM> environment during the...
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Mac laptop Deployment
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
services:
- Endpoint Provisioning
tags:
- endpoint
- macos
created: '2026-02-25'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
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
related_articles:
- kb-assets-deployment-index
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## **Macbook Setup**

All Mac laptops are configured through the automated device enrollment. Once purchased from an approved device supplier, devices are added to <ENDPOINT_ENROLLMENT_PORTAL> (<ENDPOINT_ENROLLMENT_PORTAL>) and are automatically enrolled in our <ENDPOINT_MANAGEMENT_PLATFORM> environment during the setup process.

Important Guidelines:

- Never deploy a Mac laptop that is not listed in <ENDPOINT_ENROLLMENT_PORTAL>.
- New hires must **complete their <IDENTITY_PROVIDER> account and MFA setup** (as outlined in Step 1) before logging in.
- Once a user begins the login process, they must complete it **fully and reach the desktop** . *If setup is interrupted mid-way, the device may become bricked.*
