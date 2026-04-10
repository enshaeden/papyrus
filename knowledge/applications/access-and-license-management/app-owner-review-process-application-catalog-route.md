---
id: kb-applications-access-and-license-management-app-owner-review-process-application-catalog-route
title: Application Catalog App Owner Review Process
canonical_path: knowledge/applications/access-and-license-management/app-owner-review-process-application-catalog-route.md
summary: Review and update application ownership records when the listed owner is no longer active.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Application Catalog App Owner Review Process
team: Identity and Access
systems:
- <APPLICATION_CATALOG>
- <ASSET_MANAGEMENT_SYSTEM>
- <TICKETING_SYSTEM>
tags:
- account
- access
created: '2025-11-06'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Access Management
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
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-applications-access-and-license-management-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-access-and-license-management-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Purpose

Review and update application ownership records when the listed owner is no longer active, so approvals and escalations continue to route to the right person.

## Source Of Truth

Use the application ownership register or catalog record that tracks each application and its primary and backup owners.

## Manual Review Workflow

1. Look up the inactive owner and identify the current manager or delegated business owner.
2. Contact that owner using the approved ownership-update template.
3. Request the new primary owner and, when available, a backup owner.
4. Update the ownership record only after the response is received and recorded.

## Automation Guidance

If automation is added later:

- Trigger the workflow only when every listed owner is inactive.
- Route ambiguous cases to `<QUEUE_NAME>` for manual review.
- Store the workflow outcome and review date on the catalog record.

## Required Audit Notes

- Previous owner state
- New owner and backup owner
- Request date and approval source
- Date the ownership register was updated
