---
id: kb-runbooks-laptop-provisioning
title: Laptop Provisioning
canonical_path: knowledge/runbooks/laptop-provisioning.md
summary: Prepare a standard laptop build and confirm the handoff is ready.
knowledge_object_type: runbook
legacy_article_type: null
object_lifecycle_state: active
owner: endpoint_ops
source_type: native
source_system: source_workspace_fixture
source_title: Laptop Provisioning
team: IT Operations
systems:
- <ENDPOINT_ENROLLMENT_PORTAL>
tags:
- endpoint
- checklist
created: 2026-04-08
updated: 2026-04-08
last_reviewed: 2026-04-08
review_cadence: quarterly
audience: service_desk
related_services:
- Endpoint Provisioning
prerequisites:
- Confirm the device is recorded in inventory.
steps:
- Enroll the laptop and apply the standard provisioning policy.
verification:
- Confirm the assigned user can sign in and launch the standard toolset.
rollback:
- Reimage the device and reopen the provisioning checklist.
citations:
- source_title: Write playbook
  source_type: document
  source_ref: knowledge/write.md
  note: Evidence must be revalidated after the next provisioning policy update.
  claim_anchor: provisioning
  excerpt: null
  captured_at: 2026-04-08T09:00:00+00:00
  validity_status: unverified
  integrity_hash: 6a4a534b8bed95da
related_object_ids: []
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
references:
- title: Write playbook
  path: knowledge/write.md
  note: Evidence must be revalidated after the next provisioning policy update.
related_articles: []
change_log:
- date: 2026-04-08
  summary: Fixture workspace baseline.
  author: tests
---

## Use When

Use this when a new or reassigned laptop needs the standard provisioning path.

## Boundaries And Escalation

Escalate when the enrollment workflow or inventory record does not match the
assigned user and the standard device path no longer applies.
