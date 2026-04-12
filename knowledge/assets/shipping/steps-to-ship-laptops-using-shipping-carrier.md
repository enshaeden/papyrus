---
id: kb-assets-shipping-steps-to-ship-laptops-using-shipping-carrier
title: Steps to ship laptops using <SHIPPING_CARRIER>
canonical_path: knowledge/assets/shipping/steps-to-ship-laptops-using-shipping-carrier.md
summary: Quick-start guide for laptop shipments through the shared carrier workflow.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Steps to ship laptops using <SHIPPING_CARRIER>
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-10-27'
updated: '2025-10-27'
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
Use this quick-start when you need a concise checklist for shipping a laptop through the shared carrier workflow.

## Checklist
1. Confirm the request, shipping address, and asset details.
2. Retrieve the approved carrier credentials from <PASSWORD_MANAGER_VAULT>.
3. Sign in to the carrier portal at <SUPPLIER_PORTAL_URL>.
4. Create the shipment using the saved laptop profile when available.
5. Add package dimensions if you are not using the standard carrier packaging.
6. Select the approved service tier.
7. Add shipment notifications to <EMAIL_ADDRESS> and the recipient.
8. Print the label, attach it securely, and place any return label inside the box if needed.
9. Record the tracking number in the ticket and update <ASSET_MANAGEMENT_SYSTEM>.

## When To Escalate
- The saved profile does not match the sender office.
- The recipient address cannot be verified.
- The requested delivery speed requires an exception or cost approval.
