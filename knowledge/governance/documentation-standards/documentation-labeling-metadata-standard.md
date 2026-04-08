---
id: kb-governance-documentation-standards-documentation-labeling-metadata-standard
title: Documentation Labeling & Metadata Standard
canonical_path: knowledge/governance/documentation-standards/documentation-labeling-metadata-standard.md
summary: To ensure consistency, clarity, and searchability in internal IT documentation by standardizing
  label usage.
knowledge_object_type: service_record
legacy_article_type: policy
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Documentation Labeling & Metadata Standard
team: IT Operations
systems: []
tags: []
created: '2025-11-05'
updated: '2025-11-12'
last_reviewed: '2026-04-07'
review_cadence: annual
audience: it_ops
service_name: Documentation Labeling & Metadata Standard
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

## Purpose

To ensure consistency, clarity, and searchability in internal IT documentation by standardizing label usage.

## Label Categories & Usage

| Category | Label Examples | Explanation | Example Use |
| --- | --- | --- | --- |
| **System/Platform** | `windows` , `<ENDPOINT_MANAGEMENT_PLATFORM>` , `<COLLABORATION_PLATFORM>` , `network` | Identifies the technology or system involved | "<ENDPOINT_MANAGEMENT_PLATFORM> device enrollment guide" → `<ENDPOINT_MANAGEMENT_PLATFORM>` |
| **Function/Topic** | `troubleshooting` , `installation` , `configuration` , `policy` , `how-to` | Describes the type of content | "VPN connection fails on Windows 11" → `troubleshooting` |
| **Audience (Internal IT)** | `helpdesk` , `sysadmin` , `security` , `network-team` | Indicates which IT role the page is for | "Password reset workflow for helpdesk staff" → `helpdesk` |
| **Impact Scope** | `single-device` , `multi-user` , `infrastructure` | Shows the scale of the issue or procedure | "Shared drive access outage" → `multi-user` |
| **Urgency/Severity** (optional) | `critical` , `high-priority` , `routine` | Flags importance if relevant | "Critical patch deployment" → `critical` |

## Best Practices

- Apply **2–4 labels per page** — enough for clarity, not clutter.
- Use **lowercase, hyphenated words** (e.g., `password-reset` , not `Password Reset` ).
- Ensure every document has at least **one System/Platform** and **one Function/Topic** label.
- Avoid duplicates or near-duplicates ( `vpn` vs `remote-access` ).
- Review labels quarterly to merge or retire unused ones.
- Do **not** use labels for **status** — rely on <KNOWLEDGE_PORTAL>/<TICKETING_SYSTEM> workflow fields instead.
