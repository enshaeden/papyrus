---
id: kb-applications-access-and-license-management-add-productivity-platform-licenses
title: Add productivity platform licenses
canonical_path: knowledge/applications/access-and-license-management/add-productivity-platform-licenses.md
summary: Legacy imported licensing workflow for <PRODUCTIVITY_PLATFORM> access requests.
knowledge_object_type: runbook
object_lifecycle_state: active
owner: licensing_ops
source_type: imported
source_system: knowledge_portal_export
source_title: Add productivity platform licenses
team: IT Operations
systems:
- <PRODUCTIVITY_PLATFORM>
- <APPLICATION_CATALOG>
- <DIRECTORY_SERVICE>
- <TICKETING_SYSTEM>
tags:
- access
created: 2026-04-08
updated: 2026-04-08
last_reviewed: 2026-04-08
review_cadence: quarterly
audience: service_desk
related_services:
- Access Management
prerequisites:
- Confirm the request contains the right manager approval.
steps:
- Validate the request against the current <APPLICATION_CATALOG> route.
- Apply the <PRODUCTIVITY_PLATFORM> license change and record the change in <TICKETING_SYSTEM>.
verification:
- Confirm the user can open <PRODUCTIVITY_PLATFORM> after the group update.
rollback:
- Remove the temporary assignment and escalate if the request scope changed.
citations:
- source_title: System model
  source_type: document
  source_ref: knowledge/system-model.md
  note: Imported licensing note still needs structured cleanup.
  claim_anchor: productivity-licenses
  excerpt: null
  captured_at: 2026-04-08T09:00:00+00:00
  validity_status: verified
  integrity_hash: 70b6eb35c8a15d8a
related_object_ids: []
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
references:
- title: System model
  path: knowledge/system-model.md
  note: Imported licensing note still needs structured cleanup.
related_object_ids: []
change_log:
- date: 2026-04-08
  summary: Imported legacy fixture retained for coverage.
  author: tests
---

## Overview

Use this when <APPLICATION_CATALOG> routes a request for
<PRODUCTIVITY_PLATFORM> access and the migrated guidance still needs structured
cleanup before the final blueprint pass.

## Effective-Date Actions

1. Confirm the <DIRECTORY_SERVICE> membership target.
2. Record the licensing action in <TICKETING_SYSTEM>.
3. Escalate if the request scope or approval trail no longer matches the
   migrated workflow.
