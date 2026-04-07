---
id: kb-incidents-incident-response-template
title: Incident Response Template
canonical_path: knowledge/incidents/incident-response-template.md
summary: Template for coordinating the initial response to an IT service incident with clear ownership and verification checkpoints.
type: incident
status: active
owner: service_owner
source_type: native
source_system: repository
source_title: Incident Response Template
team: IT Operations
systems:
- <TICKETING_SYSTEM>
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
- Confirmed incident ticket or bridge room.
- Named incident commander.
- Initial symptom summary and blast radius estimate.
steps:
- Declare severity, assign an incident commander, and record the start time.
- Establish communications cadence and stakeholder audience.
- Capture observed symptoms, affected services, suspected scope, and immediate mitigations.
- Assign owners for investigation, remediation, communications, and timeline capture.
- Update the incident record until the service is restored and a postmortem owner is assigned.
verification:
- Incident record includes commander, severity, timeline, and active workstreams.
- Stakeholders know the next update time and communication channel.
- Service restoration is confirmed by a technical check and a user-impact check.
rollback:
- Document rollback criteria before introducing emergency changes whenever time allows.
- Revert emergency changes that worsen impact or fail verification.
related_articles:
- kb-postmortems-postmortem-template
replaced_by: null
retirement_reason: null
references:
- title: Postmortem template
  article_id: kb-postmortems-postmortem-template
  path: knowledge/postmortems/postmortem-template.md
  note: Use this after the incident is stabilized and ownership is assigned.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Suggested Timeline Fields

- Detection time
- Declaration time
- Stakeholder notification time
- Mitigation start time
- Service restored time
- Incident closed time
