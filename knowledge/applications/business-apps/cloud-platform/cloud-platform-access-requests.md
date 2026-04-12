---
id: kb-applications-business-apps-cloud-platform-cloud-platform-access-requests
title: <CLOUD_PLATFORM> access requests
canonical_path: knowledge/applications/business-apps/cloud-platform/cloud-platform-access-requests.md
summary: Route cloud platform access through approved eligibility, role, and production-access controls.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <CLOUD_PLATFORM> access requests
team: Identity and Access
systems:
- <CLOUD_PLATFORM>
- <IDENTITY_PROVIDER>
tags:
- account
- access
created: '2025-10-28'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Access Management
prerequisites:
- Verify the requestor, business need, and approval path before assigning access.
- Confirm whether the request is for tile visibility, role eligibility, or privileged access.
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
- kb-applications-business-apps-cloud-platform-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-business-apps-cloud-platform-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Overview

<CLOUD_PLATFORM> access is not birthright access. The requestor must first be eligible to see the platform tile in <IDENTITY_PROVIDER>, then must be assigned to the correct role-based group for the requested environment.

## Standard Assignment Model

1. Add the user to the approved eligibility group that exposes the <CLOUD_PLATFORM> application tile.
2. Add the user to the role-appropriate non-production or business-function group when the request matches an approved baseline.
3. Route any production, security-sensitive, or elevated access request through the dedicated approval group and record that approval in the ticket.

## Grouping Rules

- Use separate groups for eligibility, standard-role access, and privileged access.
- Do not manually add users to automated production-mapping groups unless the access owner explicitly approves an exception.
- If a group is populated by automation or rule-based assignment, correct the upstream request data instead of overriding the downstream group manually.

## Role Guidance

- Finance or reporting users should receive only the finance-scoped role set they need.
- Engineering or operations users should receive the lowest environment level that satisfies the request.
- Security-sensitive roles require explicit approval and a documented expiration or review plan when applicable.

## Validation

- Confirm the user can see the <CLOUD_PLATFORM> tile in <IDENTITY_PROVIDER>.
- Confirm the expected environment or role is visible after assignment.
- Record the exact eligibility group, role group, and approval evidence in the ticket.

## Escalation

- Escalate requests that exceed the documented role catalog.
- Escalate any request that requires direct membership changes to automated production groups.
