---
id: kb-user-lifecycle-onboarding-new-hires-rescinded-or-delayed-onboarding
title: Rescinded or Delayed onboarding
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/rescinded-or-delayed-onboarding.md
summary: In such cases, users typically do not join after accepting the offer. We should follow the standard process for <IDENTITY_PROVIDER> deactivation. For <COLLABORATION_PLATFORM>, after suspending the account, the user can be directly archived...
type: onboarding
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Rescinded or Delayed onboarding
team: Identity and Access
systems:
- <HR_SYSTEM>
services:
- Onboarding
tags:
- account
- onboarding
created: '2025-11-06'
updated: '2025-11-06'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
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
related_articles:
- kb-user-lifecycle-onboarding-new-hires-index
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Rescinded onboarding

In such cases, users typically do not join after accepting the offer. We should follow the standard process for <IDENTITY_PROVIDER> deactivation. For <COLLABORATION_PLATFORM>, after suspending the account, the user can be directly archived in the admin portal

For rescinded users, we generate return shipping labels and email them to remote users to facilitate the return of office assets to the designated office location.

# Delayed Onboarding

If a user moves their start date after Monday or does not work with IT within the first hour of their start day to configure devices and accounts their access must be paused to prevent potential security incidents or illegal work practices (doing work before your official start date is illegal!)

In these instances, move the user’s <IDENTITY_PROVIDER> account to the <<IDENTITY_PROVIDER> group>
