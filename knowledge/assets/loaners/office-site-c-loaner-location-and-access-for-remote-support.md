---
id: kb-assets-loaners-office-site-c-loaner-location-and-access-for-remote-support
title: <OFFICE_SITE_C> Loaner Location and Access for Remote Support
canonical_path: knowledge/assets/loaners/office-site-c-loaner-location-and-access-for-remote-support.md
summary: Interview loaner laptops are stored in the Mail Room at <OFFICE_SITE_C> primary office and are
  available exclusively to Recruiting, Hiring Managers, and IT .
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <OFFICE_SITE_C> Loaner Location and Access for Remote Support
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
- account
- access
created: '2026-03-02'
updated: '2026-03-17'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
- Access Management
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
- kb-assets-loaners-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
- Access Management
related_articles:
- kb-assets-loaners-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Interview Loaners

Interview loaner laptops are stored in the **Mail Room at <OFFICE_SITE_C> primary office** and are available **exclusively to Recruiting, Hiring Managers, and IT** .

These devices are intended for temporary interview use and are configured to prevent data persistence or storage.

## Inventory Summary

The current interview loaner laptop inventory consists of:

- **6 Mac laptops**
- **1 browserbook**

**Total Devices: 7**

All devices are logged and tracked in **<ASSET_MANAGEMENT_SYSTEM>** , with the location listed as:

**Mail Room – <OFFICE_SITE_C> primary office**

<ASSET_MANAGEMENT_SYSTEM> serves as the **source of truth** for inventory records.

## Device Configuration & Security Controls

All interview loaner laptops are configured to use **Guest Accounts only** .

### Mac laptops

- Guest login only
- Safari browser access only

### browserbook

- Guest login only
- Browser-only access

### Security Protections

This configuration ensures:

- No user data is saved locally
- No credentials are stored on devices
- All browsing sessions are cleared upon logout
- No persistent profiles are created
- Protection of company and candidate information

## Storage & Physical Setup

- Devices are **clearly labeled**
- Devices remain **connected to power at all times when not in use**
- Devices must remain **charging**
- Devices are stored in the designated **Mail Room area at <OFFICE_SITE_C> primary office**

Devices should not be relocated or stored elsewhere without IT approval.

# Presentation Loaners

Permanent stock locked on the podiums in the GROW room and All-Hands in the kitchen. There is no process necessary and the spaces are available on a first-come-first-served basis, usually reserved by calendar events.

# Repair or Emergency Loaners

Due to the policy of replace and repair later for troubleshooting, no permanent stock is kept available for end user use. In emergent situations, such as a device forgotten while traveling TO the <OFFICE_SITE_C> office, a device may be pulled from Ready to Give and provided in a temporary capacity.
