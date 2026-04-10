---
id: kb-postmortems-postmortem-template
title: Postmortem Template
canonical_path: knowledge/postmortems/postmortem-template.md
summary: Template for documenting incident impact, root cause, corrective actions, and owners after service
  restoration.
knowledge_object_type: known_error
legacy_article_type: postmortem
object_lifecycle_state: active
owner: service_owner
source_type: native
source_system: repository
source_title: Postmortem Template
team: IT Operations
systems:
- <TICKETING_SYSTEM>
tags:
- incident
- template
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: after_change
audience: it_ops
related_services:
- Incident Management
symptoms:
- Template for documenting incident impact, root cause, corrective actions, and owners after service restoration.
scope: 'Legacy source does not declare structured scope. Summary: Template for documenting incident impact,
  root cause, corrective actions, and owners after service restoration.'
cause: Legacy source does not declare a structured cause field.
diagnostic_checks:
- Summarize customer impact, duration, and affected services.
- Document the root cause, contributing factors, and detection gap.
- Record what worked, what failed, and what remains unknown.
- Create corrective actions with owners and target dates.
- Publish the final postmortem and link it to the originating incident record.
mitigations:
- If corrective actions are later reversed, document the reason and replacement action in the change log.
permanent_fix_status: unknown
citations:
- article_id: kb-incidents-incident-response-template
  source_title: Incident response template
  source_type: document
  source_ref: knowledge/incidents/incident-response-template.md
  note: Use the incident record timeline as the base input for the postmortem.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-incidents-incident-response-template
prerequisites:
- Closed or stabilized incident with an agreed incident timeline.
- Named facilitator and service owner.
steps:
- Summarize customer impact, duration, and affected services.
- Document the root cause, contributing factors, and detection gap.
- Record what worked, what failed, and what remains unknown.
- Create corrective actions with owners and target dates.
- Publish the final postmortem and link it to the originating incident record.
verification:
- Root cause and impact statements are specific and evidence-based.
- Every corrective action has an owner and target date.
- The originating incident record references the completed postmortem.
rollback:
- If corrective actions are later reversed, document the reason and replacement action in the change log.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Incident Management
related_articles:
- kb-incidents-incident-response-template
references:
- title: Incident response template
  article_id: kb-incidents-incident-response-template
  path: knowledge/incidents/incident-response-template.md
  note: Use the incident record timeline as the base input for the postmortem.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Suggested Sections

- Incident summary
- Customer impact
- Root cause
- Contributing factors
- Detection and response
- Corrective actions
- Follow-up review date
