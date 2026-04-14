---
id: kb-assets-shipping-region-a-shipping-carrier-shipping
title: <REGION_A> - <SHIPPING_CARRIER> shipping
canonical_path: knowledge/assets/shipping/region-a-shipping-carrier-shipping.md
summary: Create shipment labels for <REGION_A> through the approved carrier portal workflow.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <REGION_A> - <SHIPPING_CARRIER> shipping
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-08-29'
updated: '2026-02-25'
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
Use this procedure to create outbound or return shipping labels for devices handled through the shared carrier portal for <REGION_A>.

## Prerequisites
- Approved access to the shared carrier account in <PASSWORD_MANAGER_VAULT>.
- Sender, recipient, and package details.
- Related ticket or asset record for logging.

## Procedure
1. Sign in to the carrier portal at <SUPPLIER_PORTAL_URL> using the approved shared account.
2. Open the shipment creation workflow.
3. Select the saved shipping template if one exists. If not, enter ship-from and deliver-to details manually.
4. Enter package weight and dimensions.
5. Choose the correct profile:
   - Use the standard laptop profile for device shipments.
   - Use the priority document profile for paperwork-only shipments.
6. Select the approved service tier for the request.
7. Enable a return label when shipping a replacement device or return kit.
8. Add shipment notifications to <EMAIL_ADDRESS> and the recipient.
9. Finalize the shipment and print the label.

## Validation
- Confirm the tracking number is generated.
- Confirm the label shows the correct sender and recipient.
- Confirm the ticket and <ASSET_MANAGEMENT_SYSTEM> record were updated.
