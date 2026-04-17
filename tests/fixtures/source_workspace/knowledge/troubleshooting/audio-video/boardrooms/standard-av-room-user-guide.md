---
id: kb-troubleshooting-audio-video-boardrooms-standard-av-room-user-guide
title: Standard AV Room User Guide
canonical_path: knowledge/troubleshooting/audio-video/boardrooms/standard-av-room-user-guide.md
summary: Recover a standard meeting-room issue without inventing a local workaround.
knowledge_object_type: runbook
legacy_article_type: null
object_lifecycle_state: active
owner: collaboration_ops
source_type: native
source_system: source_workspace_fixture
source_title: Standard AV Room User Guide
team: IT Operations
systems:
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
created: 2026-04-08
updated: 2026-04-08
last_reviewed: 2026-04-08
review_cadence: quarterly
audience: service_desk
related_services:
- Collaboration
prerequisites:
- Confirm the room hardware is powered and reserved.
steps:
- Check the controller state, cable routing, and default audio path.
verification:
- Confirm the room can start and join a test call.
rollback:
- Revert the local room change and hand off to workplace engineering.
citations:
- source_title: Operator web UI reference
  source_type: document
  source_ref: knowledge/operator-web-ui.md
  note: Imported note still needs direct room validation.
  claim_anchor: av-room
  excerpt: null
  captured_at: 2026-04-08T09:00:00+00:00
  validity_status: unverified
  integrity_hash: 0e818349b6af22de
related_object_ids: []
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
references:
- title: Operator web UI reference
  path: knowledge/operator-web-ui.md
  note: Imported note still needs direct room validation.
related_articles: []
change_log:
- date: 2026-04-08
  summary: Fixture workspace baseline.
  author: tests
---

## Use When

Use this when a standard conference room has a reproducible AV issue and the
operator needs a consistent first response.

## Boundaries And Escalation

Escalate when the room hardware, controller firmware, or local cabling no
longer matches the standard room profile.
