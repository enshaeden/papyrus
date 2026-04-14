---
id: kb-applications-access-and-license-management-add-collaboration-platform-enterprise-plus-licenses
title: Add <COLLABORATION_PLATFORM> advanced tier licenses
canonical_path: knowledge/applications/access-and-license-management/add-collaboration-platform-advanced-tier-licenses.md
summary: Add capacity for the <COLLABORATION_PLATFORM> advanced tier through the approved licensing workflow.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Add <COLLABORATION_PLATFORM> advanced tier licenses
team: IT Operations
systems:
- <COLLABORATION_PLATFORM>
tags:
- account
- access
created: '2026-03-17'
updated: '2026-03-17'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: it_ops
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

# Prerequisites
- Approved access to the licensing portal or reseller workflow.
- An authorized administrative account for the target tenant.
- Approval to increase the advanced license tier.

# Procedure
1. Sign in to the approved licensing workflow.
2. Confirm you are managing the correct tenant or subscription.
3. Locate the advanced license tier for <COLLABORATION_PLATFORM>.
4. Enter the number of licenses to add.
5. Review the order details, cost impact, and effective date.
6. Submit the change and save the confirmation.

## Expected Result
- The requested number of advanced-tier licenses is added.
- The updated count is visible in the licensing workflow.
- The related ticket or procurement record contains the confirmation details.
