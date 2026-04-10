---
id: kb-assets-shipping-shipping-devices-in-region-d-using-shipping-carrier
title: Shipping devices in <REGION_D> using an email-based shipping workflow
canonical_path: knowledge/assets/shipping/shipping-devices-in-region-d-using-shipping-carrier.md
summary: Arrange device shipments in <REGION_D> through the approved email-based shipping workflow.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Shipping devices in <REGION_D> using an email-based shipping workflow
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2026-02-27'
updated: '2026-02-27'
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
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Purpose
Use this procedure when the <REGION_D> shipping process is handled by email rather than a self-service carrier portal.

## General Information
- All bookings are coordinated through the approved shipping inboxes.
- Use the standard purchase order or billing reference documented for the workflow.
- Shipping materials can be requested in the same booking email when needed.
- Give several business days of notice whenever possible, especially if packaging must be delivered before collection.

## Booking Workflow
1. Determine whether the shipment is domestic or international.
2. Send the request to the correct shipping inbox.
3. Include the following in the booking email:
   - Collection date and collection window.
   - Delivery date target and urgency.
   - Goods description and declared value.
   - Number of packages or packaging materials needed.
   - Collection contact details and delivery contact details.
   - Any access notes or special instructions.
4. Request delivery confirmation to <EMAIL_ADDRESS>.
5. Save the booking confirmation in the related ticket.

## Emergency Shipments
- For urgent same-day requests, mark the booking as urgent and include the exact time the package will be ready.
- If the provider cannot meet the requested timing, escalate through the support workflow before promising delivery.

## Logging
1. Record the confirmation email and any tracking reference in the ticket.
2. Update the device status in <ASSET_MANAGEMENT_SYSTEM> to reflect that the shipment is in transit.
3. Once delivery is confirmed, update the ticket and asset record with the completion date.
