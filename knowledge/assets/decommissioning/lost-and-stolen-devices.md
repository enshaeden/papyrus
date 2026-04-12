---
id: kb-assets-decommissioning-lost-and-stolen-devices
title: Lost and Stolen devices
canonical_path: knowledge/assets/decommissioning/lost-and-stolen-devices.md
summary: In the event that a <COMPANY_NAME> asset is reported lost or stolen, it is imperative to act
  swiftly to mitigate any potential security risks. Adherence to the procedures outlined below is required.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Lost and Stolen devices
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-12-08'
updated: '2026-03-06'
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
  source_ref: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-assets-decommissioning-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-decommissioning-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

In the event that a <COMPANY_NAME> asset is reported lost or stolen, it is imperative to act swiftly to mitigate any potential security risks. Adherence to the procedures outlined below is required.

End user guidance can be found here: < [What to Do If Your Laptop Is Lost or Stolen](<INTERNAL_URL>) >

# Track the incident

1. Confirm or create a <TICKETING_SYSTEM> ticket for the stolen machine/asset for tracking purposes.
  1. Be sure to add a the label “Lost/Stolen Company Asset” within the <TICKETING_SYSTEM> ticket for tracking purposes.
2. Assign the ticket to yourself and comment that you have received the report.

# Secure the device

## MacOS

[MacOS Lost or Stolen devices MacOS Lost or Stolen devices](macos-lost-or-stolen-devices.md)

## Windows

[Windows Lost or Stolen Procedures Windows Lost or Stolen Procedures](windows-lost-or-stolen-procedures.md)

# Update the ticket

1. Update the ticket noting the action taken according to the above sections, “Secure the accounts” and “Secure the device”
2. Followup with the user to get the following details:
  1. Police report/case number
      1. This should also be added to the notes field in <ASSET_MANAGEMENT_SYSTEM>
    2. Details about the incident (if not already provided in initial comms)
      1. Where the device was last seen
          2. Were any passwords written on stickies/stored near the device?
          3. Were any registered MFA devices part of the incident?
            1. Phone
                  2. Yubikey
                  3. SmartCard

# Notify our partner teams

## Security

Post a message in [<QUEUE_NAME>](<INTERNAL_URL>) letting them know what has occurred and link the ticket for visibility. If Security deems this incident a risk you may need to [secure the accounts](<INTERNAL_URL>)

### Secure the accounts

Pause or suspend access to:

<IDENTITY_PROVIDER>

<COLLABORATION_PLATFORM>

> INFO: Do NOT suspend <MESSAGING_PLATFORM> access as this may be the only way to communicate with the user.

## Accounting

1. Notify <EMAIL_ADDRESS> of the lost asset for follow up ( [Email Comm for Accounting](<INTERNAL_URL>) ). Send them the invoice for the device (Found in <ENDPOINT_ENROLLMENT_PORTAL>).
  1. Update the <TICKETING_SYSTEM> ticket with the actions taken

# Replace the device

1. Create a separate ticket and link it to the lost/stolen ticket
2. Allocate or order a replacement device that matches their prior device spec
  1. If the user is based in an office, a temporary loaner device may be provided if an equivalent machine is not immediately available.
3. Tag the user’s manager of the incident so they are aware that the user is offline until the replacement arrives

Once the user has confirmed the device is received, all tickets can be closed. If you suspended the user’s accounts in the Security partner step, make sure to reinstate their access prior to setting up the new device.
