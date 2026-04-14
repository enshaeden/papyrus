---
id: kb-assets-overview-asset-management-overview
title: Asset Management Overview
canonical_path: knowledge/assets/overview/asset-management-overview.md
summary: Asset Management breaks down into two categories Workstations and Accessories/Peripherals.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Asset Management Overview
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-10-28'
updated: '2025-12-10'
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
- kb-assets-overview-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-overview-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

Asset Management breaks down into two categories - Workstations and Accessories/Peripherals.

The workstation category comprises any compute hardware that is used for primary job function; usually a Laptop-type device with either MacOS or Windows.

The Accessory and Peripheral category usually comprises keyboards, mice, printers, and other similar non-compute hardware.

All serialized assets (Computers, tablet devices, etc) must be recorded into <ASSET_MANAGEMENT_SYSTEM> upon receipt into the environment. Further, devices should be enrolled in their respective MDM solution - <ENDPOINT_MANAGEMENT_PLATFORM>, <ENDPOINT_MANAGEMENT_PLATFORM>, or otherwise.

# Asset Intake

## All Serialized product

[Device Acquisition and Registration Device Acquisition and Registration](../acquisition/device-acquisition-and-registration.md)

Receiving & Handling New IT Hardware Receiving & Handling New IT Hardware

### MacOS

#### <ENDPOINT_MANAGEMENT_PLATFORM>

#### <ENDPOINT_ENROLLMENT_PORTAL> (<ENDPOINT_ENROLLMENT_PORTAL>)

Manually enrolling laptops that aren’t in <ENDPOINT_ENROLLMENT_PORTAL> Manually enrolling laptops that aren’t in <ENDPOINT_ENROLLMENT_PORTAL>

### Windows

#### <ENDPOINT_MANAGEMENT_PLATFORM> Overview <ENDPOINT_MANAGEMENT_PLATFORM>

#### Entra

# Repair or Replacement

# Decomissioning

[Quarterly Finance Asset Review – IT Helpdesk Procedure Quarterly Finance Asset Review – IT Helpdesk Procedure](../audits-and-recordkeeping/quarterly-finance-asset-review-it-helpdesk-procedure.md)

# Exceptional Circumstances

## Lost or Stolen devices

In the event that a <COMPANY_NAME> asset is reported lost or stolen, it is imperative to act swiftly to mitigate any potential security risks. Adherence to the procedures outlined below is required.

[Lost and Stolen devices Lost and Stolen devices](../decommissioning/lost-and-stolen-devices.md)

## Legal Holds
