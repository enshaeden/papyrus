---
id: kb-assets-overview-managing-it-hardware-and-software-at-company
title: Managing IT hardware and software at <COMPANY_NAME>
canonical_path: knowledge/assets/overview/managing-it-hardware-and-software-at-company.md
summary: Overview article linking core hardware and software management workflows.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Managing IT hardware and software at <COMPANY_NAME>
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-11-10'
updated: '2025-12-10'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
prerequisites:
- Confirm the device, asset record, and office or shipping context before taking action.
- Verify you have the required inventory, MDM, or ticketing access for the task.
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
- kb-assets-overview-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-overview-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Hardware lifecycle management
- [Asset Management Overview](../index.md)
- [Device Acquisition and Registration](../acquisition/device-acquisition-and-registration.md)
- [Asset Deployment](../deployment/asset-deployment.md)
- [Asset Decomissioning](../decommissioning/asset-decomissioning.md)

# Software lifecycle management
- [Software License Management](../../applications/access-and-license-management/software-license-management.md)
- [Managing <IDENTITY_PROVIDER> Access Requests & General App Requests](../../applications/access-and-license-management/managing-identity-provider-access-requests-general-app-requests.md)
- [Application Ownership & Access Audit Playbook](../../applications/access-and-license-management/application-ownership-access-audit-playbook.md)
