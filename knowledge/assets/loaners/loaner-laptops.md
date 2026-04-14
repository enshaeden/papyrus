---
id: kb-assets-loaners-loaner-laptops
title: Loaner Laptops
canonical_path: knowledge/assets/loaners/loaner-laptops.md
summary: Shared canonical policy for issuing, tracking, and routing temporary loaner devices, with site-specific pickup and storage handled in linked location pages.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Loaner Laptops
team: Systems Engineering
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
- Confirm the loan request is tied to an approved business use case or a qualifying hardware failure.
- Verify the target site, inventory status, and ticketing workflow before assigning a device.
- Confirm you can update both the ticket and <ASSET_MANAGEMENT_SYSTEM> before releasing the loaner.
steps:
- Confirm the request qualifies under the shared eligibility policy and choose the correct site-specific access page below.
- Create or update the ticket that tracks the loan, expected return date, and device handoff.
- Reserve or deploy the selected device in <ASSET_MANAGEMENT_SYSTEM> only after you confirm physical availability.
- Follow the site-specific pickup, storage, or approval instructions for the office in scope.
- Record the device status, assigned user, issue summary, and expected return date before closing the handoff.
verification:
- The ticket and asset record show the same assigned device, user, and expected return date.
- The selected site-specific access page matches the office or storage location used for the handoff.
- The user has a working device path and understands the return expectation.
rollback:
- Return the device to the prior inventory state if the handoff cannot be completed safely.
- Reverse the reservation or deployment in <ASSET_MANAGEMENT_SYSTEM> if the selected device or site path was incorrect.
- Escalate if no maintained site-specific access page matches the request.
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
- kb-assets-loaners-index
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
- kb-assets-loaners-region-d-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-b-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-c-loaner-location-and-access-for-remote-support
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-loaners-index
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
- kb-assets-loaners-region-d-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-b-loaner-location-and-access-for-remote-support
- kb-assets-loaners-office-site-c-loaner-location-and-access-for-remote-support
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
- date: '2026-04-07'
  summary: Promoted this article to the shared loaner-device policy and moved site-specific differences into linked location pages.
  author: codex
---

## Purpose

This policy defines a consistent, global approach for issuing temporary loaner laptops and other approved devices when an employee’s primary corporate device experiences a qualifying hardware failure. The goal is to minimise downtime, maintain business continuity, and ensure accurate asset tracking.

## Policy

Loaner devices are issued for the shortest time necessary. Users must return loaner devices promptly once a primary device is repaired or replaced. All issuance/returns must be tracked in the ticketing system and the asset inventory system.

## Eligibility

Loaner devices are for:

- On-site interviews
- Presentations
- Primary device left behind while travelling
- Hardware failure that prevents productive work

## Shared Intake And Tracking Workflow

1. Confirm the request qualifies and determine the correct office or region.
2. Create or update the loan ticket with the user, reason, and expected return date.
3. Confirm the selected device is physically available before reserving it in <ASSET_MANAGEMENT_SYSTEM>.
4. Set the status to the correct handoff state:
   - `Reserved for Loan` when the device is awaiting pickup
   - `Loan` when the device has been handed to the user
5. Record the user, issue summary, and return expectation in both the ticket and the asset record.
6. Move the device back to `Needs Setup/Restore` or `Ready for Loan` when it is returned and reset.

## Inventory And Tracking

All loaners are registered in <ASSET_MANAGEMENT_SYSTEM> as permanent Loaner stock. You can view the inventory for all regions on this [<ASSET_MANAGEMENT_SYSTEM> View](<INTERNAL_URL>) .

The loaner-specific status' are as follows:

| **Status** | **Use case** |
| --- | --- |
| Needs Setup/Restore | Indicates that the loaner device has been received after a loan and needs to be set up as new. |
| Ready for Loan | Is erased and setup as new. Available to reserve upon request. |
| Reserved for Loan | Has been requested, pending pickup by the end user. |
| Loan | Has been handed to the user and is assigned. |

Help Desk team members are expected to update and maintain the status of the devices as they would any other device in our inventory.

## Site-Specific Access And Storage

[<REGION_A> Loaner Location and Access for Remote Support](region-a-loaner-location-and-access-for-remote-support.md)

[<REGION_D> Loaner Location and Access for Remote Support](region-d-loaner-location-and-access-for-remote-support.md)

[<OFFICE_SITE_C> Loaner Location and Access for Remote Support](office-site-c-loaner-location-and-access-for-remote-support.md)

[<OFFICE_SITE_B> Loaner Location and Access for Remote Support](office-site-b-loaner-location-and-access-for-remote-support.md)

Use these linked pages for local storage, pickup, approval, and after-hours access differences. Keep shared eligibility, inventory states, and tracking expectations in this article.
