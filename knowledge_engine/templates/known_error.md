---
id: {{id}}
title: {{title}}
canonical_path: {{canonical_path}}
summary: Replace with a concise statement of the failure pattern and impact.
knowledge_object_type: known_error
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
symptoms:
- Describe the primary observable symptom.
scope: Describe the affected population, workflow, or component.
cause: If known, describe the confirmed cause. If unknown, state that it is not yet verified.
diagnostic_checks:
- Describe the first diagnostic check.
mitigations:
- Describe the first mitigation or containment action.
permanent_fix_status: unknown
citations:
- source_title: Replace with a supporting document, local path, or canonical knowledge-object reference.
  source_type: document
  source_ref: Replace with a canonical path, URL placeholder, or system reference.
  claim_anchor: null
  note: Explain why this citation supports the known error record.
  captured_at: null
  integrity_hash: null
{{related_object_ids_field}}
superseded_by: null
retirement_reason: null
services: {{related_services_inline}}
references:
- title: Replace with a supporting document, local path, or canonical knowledge-object reference.
  object_id: null
change_log:
- date: {{today}}
  summary: Initial object scaffold.
  author: new_object.py
---

## Detection Notes

State how operators recognize this issue and how to distinguish it from adjacent failure patterns.

## Escalation Threshold

State when the documented mitigations are exhausted and which team should take over.

## Evidence Notes

- Replace `captured_at: null` and `integrity_hash: null` when you have real evidence capture details. Leaving them null keeps the citation in weak-evidence posture.
