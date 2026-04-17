---
id: {{id}}
title: {{title}}
canonical_path: {{canonical_path}}
summary: Replace with a concise operational summary.
knowledge_object_type: runbook
object_lifecycle_state: {{object_lifecycle_state}}
owner: {{owner}}
source_type: native
source_system: repository
source_title: {{title}}
team: {{team}}
{{systems_field}}
{{tags_field}}
created: {{today}}
updated: {{today}}
last_reviewed: {{today}}
review_cadence: quarterly
audience: {{audience}}
{{related_services_field}}
prerequisites:
- Document required access, tooling, approvals, and timing dependencies.
steps:
- Replace this step with the first operator action.
verification:
- Document how to verify the expected outcome.
rollback:
- Document rollback or recovery actions.
{{related_object_ids_field}}
superseded_by: null
retirement_reason: null
citations:
- source_title: Replace with a supporting document, local path, or canonical knowledge-object reference.
  source_type: document
  source_ref: Replace with a canonical path, URL placeholder, or system reference.
  claim_anchor: null
  note: Explain why this citation supports the runbook.
  captured_at: null
  integrity_hash: null
services: {{related_services_inline}}
references:
- title: Replace with a supporting document, local path, or canonical knowledge-object reference.
  object_id: null
change_log:
- date: {{today}}
  summary: Initial object scaffold.
  author: new_object.py
---

## Use When

Explain the trigger condition, expected operator outcome, and which environments or requests this runbook covers.

## Boundaries And Escalation

State exclusions, escalation boundaries, approval thresholds, or handoff points.

## Related Knowledge Notes

- Note the prerequisite, follow-on, fallback, or sibling procedures that should also be linked in `related_object_ids` or `references`.
- Replace `captured_at: null` and `integrity_hash: null` when you have real evidence capture details. Leaving them null keeps the citation in weak-evidence posture.
