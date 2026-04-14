---
id: kb-assets-shipping-shipping-instructions-and-best-practices
title: Shipping Instructions and Best Practices
canonical_path: knowledge/assets/shipping/shipping-instructions-and-best-practices.md
summary: 'If shipping is required, follow the steps below to ensure timely and accurate delivery of equipment:'
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Shipping Instructions and Best Practices
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2026-02-25'
updated: '2026-03-03'
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
- kb-assets-shipping-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-shipping-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Shipping Instructions

## Gather the shipping address
- New hires: use the approved onboarding source.
- Existing users: confirm the current address directly with the user.
- Former users: confirm the return address directly with the user or the offboarding workflow.

## Choose the regional workflow
- [<REGION_B> and <REGION_C> - <SHIPPING_CARRIER>](canada-and-us-shipping-carrier.md)
- [<REGION_A> - <SHIPPING_CARRIER> shipping](region-a-shipping-carrier-shipping.md)
- [Shipping devices in <REGION_D> using an email-based shipping workflow](shipping-devices-in-region-d-using-shipping-carrier.md)
- [Steps to ship laptops using <SHIPPING_CARRIER>](steps-to-ship-laptops-using-shipping-carrier.md)

## Notifications and Tracking
- Add <EMAIL_ADDRESS> to shipment notifications when supported.
- Record tracking details in the related ticket and asset record.
- Update the asset status after delivery is confirmed.

## Best Practices
- Batch shipments from the same office when practical.
- Plan ahead for regional holidays, weather delays, and customs lead times.
- Use return labels for replacement shipments and recoveries whenever possible.
