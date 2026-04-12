---
id: kb-applications-access-and-license-management-managing-identity-provider-access-requests-general-app-requests
title: Managing <IDENTITY_PROVIDER> Access Requests & General App Requests
canonical_path: knowledge/applications/access-and-license-management/managing-identity-provider-access-requests-general-app-requests.md
summary: 'Summary: This simplified guide explains how the <COMPANY_NAME> IT Helpdesk team supports access
  requests made through <IDENTITY_PROVIDER>. It covers automated requests, general requests routed via
  <TICKETING_SYSTEM>, and how to manage approval updates...'
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Managing <IDENTITY_PROVIDER> Access Requests & General App Requests
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
- access
created: '2025-10-27'
updated: '2025-10-27'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Identity
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
  source_ref: docs/migration/seed-migration-rationale.md
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
- Identity
- Access Management
related_articles:
- kb-applications-access-and-license-management-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Overview
This guide explains how the IT helpdesk should handle access requests that originate in <IDENTITY_PROVIDER>.

## Supported Request Paths
- **Automated access requests:** approved requests are provisioned automatically and usually do not require IT action.
- **General application requests:** requests that cannot be fulfilled automatically are converted into <TICKETING_SYSTEM> tickets for manual review.
- **Approver updates:** if the configured approver is unavailable, IT may need to move the approval to the next appropriate approver.

## Current Automated Request Categories
The automated flow is intended for a small set of pre-approved business applications and baseline access bundles. Each automated item should have:
- a documented owner,
- a defined approval path,
- clear licensing rules, and
- an auditable fulfillment method.

If an application is not in the automated set, treat it as a manual request.

## Manual Request Workflow
1. Open the request in the <IDENTITY_PROVIDER> access request dashboard.
2. Confirm whether the item should stay in <IDENTITY_PROVIDER> or be handled in <TICKETING_SYSTEM>.
3. If the request requires manual action, make sure the linked <TICKETING_SYSTEM> ticket contains:
   - requester identity,
   - requested application or role,
   - approval evidence,
   - required license tier or access level,
   - rollback notes if the request is temporary.
4. Route the ticket according to the support ownership model.

## Changing the Approver
1. Open the request in the dashboard.
2. Confirm the original approver is unavailable.
3. Reassign the approval to the next appropriate approver in the management chain.
4. Record the reason for the change in the ticket.

## Need Help?
- For escalation support, contact IT leadership.
- For routing guidance, use the application owner directory or the master routing article.

## Canned Response
Use this response when a requester submits a software-access ticket directly in <TICKETING_SYSTEM> even though the request should start in <IDENTITY_PROVIDER>.

> Please submit future software access requests through <IDENTITY_PROVIDER> so the request follows the documented approval and fulfillment workflow. We will process this request once, but future requests should use the approved self-service path. If you need help finding the correct request form, contact the IT helpdesk.
