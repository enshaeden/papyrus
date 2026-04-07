---
id: kb-applications-business-apps-collaboration-platform-collaboration-platform-monthly-audit-script
title: <COLLABORATION_PLATFORM> Monthly audit script
canonical_path: knowledge/applications/business-apps/collaboration-platform/collaboration-platform-monthly-audit-script.md
summary: Generate a monthly audit export for inactive, suspended, or archived <COLLABORATION_PLATFORM>
  accounts.
type: SOP
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: <COLLABORATION_PLATFORM> Monthly audit script
team: Identity and Access
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <COLLABORATION_PLATFORM>
services: []
tags: []
created: '2025-12-10'
updated: '2025-12-18'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
prerequisites:
- Review the scope, approvals, and dependencies described in this article before starting.
- Confirm you have the required systems access and escalation path before proceeding.
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
- kb-applications-business-apps-collaboration-platform-index
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

# Purpose
Use this procedure to generate a monthly audit report for inactive, suspended, or archived accounts in <COLLABORATION_PLATFORM>.

## Input Expectations
- Export a JSON file from the platform administration area that contains account email, status, and last sign-in timestamp.
- Save the export in a local working directory that is appropriate for temporary audit files.

## Recommended Script Behavior
The script should:
1. Load the JSON export.
2. Normalize the account list.
3. Count suspended accounts.
4. Count accounts that have not signed in for more than 30 days.
5. Count archived accounts.
6. Write the inactive or reclaimable accounts to a CSV file for follow-up.

## Safe Example Workflow
1. Open a terminal.
2. Create a temporary working directory for the monthly audit.
3. Save the JSON export as `collaboration_platform_licenses.json`.
4. Save the audit script as `collaboration_platform_license_audit.py`.
5. Run the script with the standard Python interpreter available on the workstation.
6. Review the generated CSV output and attach the result to the audit ticket.

## Validation
- Confirm the JSON export loaded successfully.
- Confirm the CSV output contains only the expected account email column.
- Confirm the counts in the script output match the exported data sample.

## Troubleshooting
- If the script cannot find the JSON file, make sure both files are in the same working directory.
- If the output file is empty, confirm the export still includes status and sign-in fields.
- If the export format changes, update the parser before re-running the audit.
