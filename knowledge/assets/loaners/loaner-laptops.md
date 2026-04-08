---
id: kb-assets-loaners-loaner-laptops
title: Loaner Laptops
canonical_path: knowledge/assets/loaners/loaner-laptops.md
summary: "This policy defines a consistent, global approach for issuing temporary loaner laptops and other\
  \ approved devices when an employee\u2019s primary corporate device experiences a qualifying hardware\
  \ failure. The goal is to..."
knowledge_object_type: runbook
legacy_article_type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Loaner Laptops
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-12-11'
updated: '2026-03-02'
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
- kb-assets-loaners-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-loaners-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Purpose**

This policy defines a consistent, global approach for issuing temporary loaner laptops and other approved devices when an employee’s primary corporate device experiences a qualifying hardware failure. The goal is to minimise downtime, maintain business continuity, and ensure accurate asset tracking.

# Policy

Loaner devices are issued for the shortest time necessary. Users must return loaner devices promptly once a primary device is repaired or replaced. All issuance/returns must be tracked in the ticketing system and the asset inventory system.

# Eligibility

Loaner devices are for:

- On-site interviews
- Presentations
- Primary device left behind while travelling
- Hardware failure that prevents productive work

# Inventory and tracking

All loaners are registered in <ASSET_MANAGEMENT_SYSTEM> as permanent Loaner stock. You can view the inventory for all regions on this [<ASSET_MANAGEMENT_SYSTEM> View](<INTERNAL_URL>) .

The loaner-specific status' are as follows:

| **Status** | **Use case** |
| --- | --- |
| Needs Setup/Restore | Indicates that the loaner device has been received after a loan and needs to be set up as new. |
| Ready for Loan | Is erased and setup as new. Available to reserve upon request. |
| Reserved for Loan | Has been requested, pending pickup by the end user. |
| Loan | Has been handed to the user and is assigned. |

Help Desk team members are expected to update and maintain the status of the devices as they would any other device in our inventory.

## Physical Inventory and Access policies

[<REGION_A> Loaner Location and Access for Remote Support <REGION_A> Loaner Location and Access for Remote Support](region-a-loaner-location-and-access-for-remote-support.md)

[<REGION_D> Loaner Location and Access for Remote Support <REGION_D> Loaner Location and Access for Remote Support](region-d-loaner-location-and-access-for-remote-support.md)

[<OFFICE_SITE_C> Loaner Location and Access for Remote Support <OFFICE_SITE_C> Loaner Location and Access for Remote Support](office-site-c-loaner-location-and-access-for-remote-support.md)

[<OFFICE_SITE_B> Loaner Location and Access for Remote Support <OFFICE_SITE_B> Loaner Location and Access for Remote Support](office-site-b-loaner-location-and-access-for-remote-support.md)
