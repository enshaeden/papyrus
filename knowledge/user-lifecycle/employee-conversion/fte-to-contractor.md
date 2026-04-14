---
id: kb-user-lifecycle-employee-conversion-fte-to-contractor
title: FTE to Contractor
canonical_path: knowledge/user-lifecycle/employee-conversion/fte-to-contractor.md
summary: Coordinate identity, email, and downstream account updates when a full-time employee converts
  to contractor status.
knowledge_object_type: runbook
legacy_article_type: runbook
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: FTE to Contractor
team: IT Operations
systems:
- <HR_SYSTEM>
- <IDENTITY_PROVIDER>
- <COLLABORATION_PLATFORM>
tags:
- account
- offboarding
created: '2025-10-28'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services:
- Identity
- Offboarding
- Access Management
prerequisites:
- Review the scope, approvals, and dependencies described in this article before starting.
- Confirm you have the required systems access and escalation path before proceeding.
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
- kb-user-lifecycle-employee-conversion-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
- Offboarding
- Access Management
related_articles:
- kb-user-lifecycle-employee-conversion-index
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

Use this runbook when a full-time employee converts to contractor status and the person keeps a single identity record through the transition.

## Intake And Pre-Checks

1. Confirm the conversion date, new contractor owner, manager, and approved access profile in `<HR_SYSTEM>`.
2. Verify the conversion ticket is linked to any related offboarding, onboarding, and hardware tickets.
3. Confirm whether the person will keep the same primary identity record or whether HR will perform a terminate-and-rehire action.

## Before The Effective Date

1. Coordinate with `<TEAM_NAME>` and the HR owner to make sure any early email-domain change is reversed until the approved effective date.
2. Confirm which entitlements must be reduced, preserved, or converted to contractor-safe access.
3. Identify downstream applications that require manual username or email updates after the conversion.

## Effective-Date Actions

1. Verify that `<HR_SYSTEM>` updates the existing worker record in place.
2. Confirm the primary email, worker type, department, and manager values are correct for the contractor state.
3. Watch the sync into `<IDENTITY_PROVIDER>` and `<COLLABORATION_PLATFORM>` and confirm the primary login changes on the approved effective date.
4. If the person is processed as a termination and rehire instead of an in-place update, stop and escalate before continuing.

## Downstream Application Review

Review IT-managed applications that do not reliably follow the upstream identity change. Update usernames or email addresses only where the application owner documents that step as safe.

Typical follow-up systems include:

- `<MESSAGING_PLATFORM>`
- `<VIDEO_CONFERENCING_PLATFORM>`
- `<CREATIVE_PLATFORM>`
- `<PASSWORD_MANAGER>`

For each application:

1. Verify the user can still authenticate with the contractor identity.
2. Update the email or username only if the application requires a manual correction.
3. Return any temporary individual assignment back to the correct group-based assignment when applicable.
4. Confirm the person retains only the entitlements approved for contractor access.

## Optional Follow-Up Actions

- Mailbox transfer is not a default step. Perform it only with documented leadership approval.
- Email aliases are optional and require explicit approval from the manager or designated approver.
- Stored-file ownership transfer is optional and should follow the owning platform’s approved process.

## Completion

1. Confirm the user can access only the approved contractor systems.
2. Confirm related tickets record the final email, manual updates performed, and any access reductions.
3. Close the conversion ticket only after validation succeeds.
