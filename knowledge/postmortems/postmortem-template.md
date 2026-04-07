---
id: kb-postmortem-template
title: Postmortem Template
canonical_path: knowledge/postmortems/postmortem-template.md
summary: Template for documenting incident impact, root cause, corrective actions, and owners after service restoration.
type: postmortem
status: active
owner: Service Owner
source_type: native
team: IT Operations
systems:
  - Ticketing Queue
services:
  - Incident Management
tags:
  - incident
  - template
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: after_change
audience: it_ops
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
related_articles:
  - kb-incident-response-template
replaced_by: null
retirement_reason: null
references:
  - title: Incident response template
    article_id: kb-incident-response-template
    path: knowledge/incidents/incident-response-template.md
    note: Use the incident record timeline as the base input for the postmortem.
change_log:
  - date: 2026-04-07
    summary: Initial seed article.
    author: Repository bootstrap
---

## Suggested Sections

- Incident summary
- Customer impact
- Root cause
- Contributing factors
- Detection and response
- Corrective actions
- Follow-up review date
