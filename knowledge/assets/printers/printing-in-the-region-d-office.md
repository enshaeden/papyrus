---
id: kb-assets-printers-printing-in-the-region-d-office
title: Printing in the <REGION_D> Office
canonical_path: knowledge/assets/printers/printing-in-the-region-d-office.md
summary: 'Option 2: Connecting physically'
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Printing in the <REGION_D> Office
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <PRINTER_MANAGEMENT_PLATFORM>
services:
- Endpoint Provisioning
- Printing
tags:
- endpoint
- printer
created: '2025-12-02'
updated: '2026-03-05'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
prerequisites:
- Confirm the device, asset record, and office or shipping context before taking action.
- Verify you have the required inventory, MDM, or ticketing access for the task.
steps:
- Review the imported procedure body below and confirm the documented scope matches
  the task at hand.
- Execute the documented steps in order and record the outcome in the relevant ticket
  or audit trail.
- Stop and escalate if approvals, prerequisites, or expected checkpoints do not match
  the live request.
verification:
- The expected outcome described in the procedure is confirmed in the target system
  or ticket record.
- Completion notes, exceptions, and evidence are recorded in the relevant audit or
  support workflow.
rollback:
- Revert any reversible change described in the procedure if verification fails.
- Pause the workflow and escalate when the documented rollback path is unclear or
  incomplete.
related_articles:
- kb-assets-printers-index
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

# Print Setup
1. Open the operating system printer settings.
2. Add the default office printer advertised on the local network.
3. Accept the recommended driver if prompted.
4. Print a single-page test job and confirm the correct paper size.

## Validation
- Confirm the printer appears in the device list.
- Confirm the first test page prints successfully.
- If the wrong paper size is selected, update the setting in both the printer dialog and the application before retrying.
