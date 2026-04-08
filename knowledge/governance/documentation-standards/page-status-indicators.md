---
id: kb-governance-documentation-standards-page-status-indicators
title: Page Status Indicators
canonical_path: knowledge/governance/documentation-standards/page-status-indicators.md
summary: The "Status" flags in <TICKETING_SYSTEM> <KNOWLEDGE_PORTAL> are visual indicators used to represent
  the current state or progress of a task, project, or piece of content. They help teams quickly understand
  the status of work items at...
knowledge_object_type: service_record
legacy_article_type: reference
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Page Status Indicators
team: IT Operations
systems: []
tags: []
created: '2025-12-01'
updated: '2025-12-01'
last_reviewed: '2026-04-07'
review_cadence: annual
audience: it_ops
service_name: Page Status Indicators
service_criticality: not_classified
dependencies: []
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks: []
related_known_errors: []
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
- kb-governance-documentation-standards-index
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
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-governance-documentation-standards-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

The "Status" flags in <TICKETING_SYSTEM> <KNOWLEDGE_PORTAL> are visual indicators used to represent the current state or progress of a task, project, or piece of content. They help teams quickly understand the status of work items at a glance. Here are some key points about the "Status" flags:

- **Color-Coded Indicators** : Status flags are typically color-coded (e.g., green for "Done," yellow for "In Progress," red for "Blocked") to convey information quickly and effectively.
- **Integration with Workflows** : Status flags can be integrated into various workflows within <KNOWLEDGE_PORTAL>, making it easier to track progress and manage tasks collaboratively.
- **Visibility** : These flags enhance visibility for team members, ensuring everyone is aware of the current status of different tasks or projects.

Overall, "Status" flags are a useful feature in <KNOWLEDGE_PORTAL> for improving communication and project management within teams.

The Status indicators that we use for IT purposes are designed for use as follows:

# Rough Draft (Yellow)

This status is used to indicate a document that is not yet completed but has been Published and is visible for use. Steps may be missing, subject to change without notice, or still in “scratch” or pseudo-code format.

Rough Draft documents that are Published **can be used** for the outlined steps but feedback should be provided to the document author on any component that does not work or is missing in order to help improve the documentation towards being In Progress. No document should remain in Rough Draft for more than six business weeks (30 days).

# In Progress (Light Blue)

This status is used to indicate a document that is mostly complete. All steps are ironed out, the process is confirmed working, and the team can replicate the steps outlined with little to no error.

This status should be used as a transitional state between Rough Draft and Ready for Review and it should only be used while working on final edits prior to the Review state and should only apply for no more that 2 business weeks (10 days).

If a document is In Progress for more that 2 business weeks it will automatically become eligible for Ready for Review

# Ready for Review (Green)
