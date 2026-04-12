---
id: kb-user-lifecycle-onboarding-new-hires-master-new-hire-report-access-export-and-post-onboarding-cleanup-guide
title: 'Master New Hire Report: Access, Export, and Post-Onboarding Cleanup Guide'
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/master-new-hire-report-access-export-and-post-onboarding-cleanup-guide.md
summary: If any critical data is missing, contact HR immediately to resolve it before proceeding with
  device setup or shipping.
knowledge_object_type: runbook
legacy_article_type: onboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: 'Master New Hire Report: Access, Export, and Post-Onboarding Cleanup Guide'
team: Identity and Access
systems:
- <HR_SYSTEM>
tags:
- account
- onboarding
- access
created: '2026-02-25'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
related_services:
- Access Management
- Onboarding
prerequisites:
- Verify the request, identity details, and required approvals before changing access or account state.
- Confirm the target system and business context match the scope of this article.
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
- kb-user-lifecycle-onboarding-new-hires-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
- Onboarding
related_articles:
- kb-user-lifecycle-onboarding-new-hires-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# How to use the Master New Hire Report?

## **Accessing the Report:**

- This report is sent to all **IT technicians who are subscribed** to receive it.
- **New IT team members** must submit a **<TICKETING_SYSTEM> request** to gain access to the report in **<HR_SYSTEM>** .
- Access is granted by the **Enterprise Applications team** .
- Once approved, you can also **run the report manually** within <HR_SYSTEM> by searching for its name.

## **Exporting & Filtering:**

- Export the report from **<HR_SYSTEM> to <COLLABORATION_PLATFORM> Sheets** for easier filtering and sorting.
- Use filters to view data by **region** and **start date** , which helps with planning device provisioning and handoffs.

## **Shipping Information:**

- The report includes details on whether a laptop needs to be **shipped** or will be **picked up in person** , along with **shipping address** and contact details.
- If a shipping label is needed, make sure you have:
  - **Delivery address**
    - **Phone number**
    - **Email address**

## **Post-Onboarding Cleanup:**

- After the new hires have been successfully onboarded, **delete the filtered sheet** you created in <COLLABORATION_PLATFORM> Sheets to keep data clean and secure.

## **Missing Information:**

If any critical data is missing, **contact HR immediately** to resolve it before proceeding with device setup or shipping.
