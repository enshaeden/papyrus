---
id: kb-applications-business-apps-productivity-platform-productivity-platform-licensing-apps-e3-no-teams-and-teams-enterprise
title: '<PRODUCTIVITY_PLATFORM> licensing: core productivity tier, mailbox tier, and messaging tier'
canonical_path: knowledge/applications/business-apps/productivity-platform/productivity-platform-licensing-core-and-messaging-tiers.md
summary: Compare the three approved <PRODUCTIVITY_PLATFORM> license tiers and apply the correct assignment
  workflow.
knowledge_object_type: runbook
legacy_article_type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: '<PRODUCTIVITY_PLATFORM> licensing: core productivity tier, mailbox tier, and messaging
  tier'
team: Identity and Access
systems:
- <COLLABORATION_PLATFORM>
tags: []
created: '2025-10-24'
updated: '2025-11-25'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services: []
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
- kb-applications-business-apps-productivity-platform-index
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-applications-business-apps-productivity-platform-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Overview
This article describes the three approved <PRODUCTIVITY_PLATFORM> license tiers used in the seed KMDB.

## License Tiers
| Tier | Primary Use | Includes | Excludes | Notes |
| --- | --- | --- | --- | --- |
| **Core productivity tier** | Productivity apps without mailbox access | Document editing, spreadsheets, presentations, notes, desktop email client configuration | Mailbox service, messaging add-on | Default option when only productivity apps are required. |
| **Mailbox tier** | Productivity apps plus mailbox access | Core productivity apps, mailbox service, collaboration file storage | Messaging add-on | Use only when documented mailbox access is required. |
| **Messaging tier** | Messaging and meeting access for approved business cases | Messaging, meetings, screen sharing | Mailbox service, full productivity app bundle | Use only when the business case requires this add-on. |

## Assignment Rules
1. Confirm the requested tier and business justification.
2. Verify manager approval where required.
3. Add the user to the correct entitlement group in <IDENTITY_PROVIDER>.
4. Assign the corresponding license in the productivity administration workflow.
5. Confirm the user has only the intended entitlement group.

## Review Guidance
- Use the core productivity tier whenever mailbox service is not required.
- Use the mailbox tier only for roles with a documented mailbox dependency.
- Use the messaging tier only when the collaboration requirement cannot be met by the default toolset.

## Validation
- The correct group membership is present in <IDENTITY_PROVIDER>.
- The user holds only one of the mutually exclusive productivity tiers.
- The license count is updated in the relevant inventory or procurement record.
