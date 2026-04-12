---
id: kb-assets-shipping-canada-and-us-shipping-carrier
title: <REGION_B> and <REGION_C> - <SHIPPING_CARRIER>
canonical_path: knowledge/assets/shipping/canada-and-us-shipping-carrier.md
summary: Create laptop and accessory shipments for <REGION_B> and <REGION_C> using the shared carrier
  workflow.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <REGION_B> and <REGION_C> - <SHIPPING_CARRIER>
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-08-20'
updated: '2026-02-26'
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

# Purpose
Use this procedure when shipping laptops or accessories for <REGION_B> and <REGION_C> through the shared carrier workflow.

## General Information
- Use the approved shared shipping account stored in <PASSWORD_MANAGER_VAULT>.
- Confirm the recipient, shipping address, asset tag, and requested delivery window before booking.
- Use carrier-provided laptop packaging when available. If non-standard packaging is used, enter package dimensions manually.
- Add shipment notifications for both the operator and recipient.

## Packaging Guidance
- Include the laptop, supported charger, and any return materials required for the workflow.
- Add internal padding so the device cannot move during transit.
- For replacement shipments, place the printed return label inside the box before sealing it.

## Procedure
1. Sign in to the carrier portal at <SUPPLIER_PORTAL_URL>.
2. Start a new shipment and select the saved regional shipping profile when one is available.
3. Confirm the ship-from address for the correct office or pickup site.
4. Enter or verify the deliver-to address.
5. Enter package weight and dimensions.
6. Choose the required service tier:
   - Use the standard service for planned deliveries.
   - Use the expedited tier only when the request is time-sensitive and approved.
7. Add a return label if the user must send equipment back.
8. Add shipment notifications to <EMAIL_ADDRESS> and the recipient.
9. Finalize the shipment, print the label, and attach it securely.

## Logging
- Record the tracking number and proof of shipment in the related ticket.
- Update the asset record in <ASSET_MANAGEMENT_SYSTEM> to show the device is in transit.
- After delivery, update the related asset or onboarding workflow with the delivery date.
