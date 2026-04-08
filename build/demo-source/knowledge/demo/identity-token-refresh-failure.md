---
id: kb-demo-identity-token-known-error
title: Identity Token Refresh Failure
canonical_path: knowledge/demo/identity-token-refresh-failure.md
summary: Demo scenario object for identity token refresh failure
knowledge_object_type: known_error
legacy_article_type: null
status: active
owner: identity_ops
source_type: native
source_system: repository
source_title: Identity Token Refresh Failure
team: IT Operations
systems:
- <IDENTITY_PROVIDER>
tags:
- demo
- known-error
created: '2026-04-07'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: service_desk
related_services:
- Identity
symptoms:
- Users cannot refresh tokens after the upstream change.
scope: Identity workflows backed by cached refresh tokens.
cause: Upstream identity policy changed before downstream runbooks were reviewed.
diagnostic_checks:
- Confirm the identity policy revision applied.
mitigations:
- Force a fresh sign-in and route high-impact users to fallback support.
permanent_fix_status: planned
citations:
- captured_at: '2026-04-07T09:00:00+00:00'
  claim_anchor: operator-claim
  excerpt: null
  integrity_hash: 14f06b367e54bd63
  note: Demo evidence.
  source_ref: docs/reference/operator-web-ui.md
  source_title: Identity change record
  source_type: document
  validity_status: verified
related_object_ids:
- kb-demo-identity-service-record
- kb-demo-identity-fallback-runbook
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
references:
- note: Demo evidence.
  path: docs/reference/operator-web-ui.md
  title: Identity change record
related_articles:
- kb-demo-identity-service-record
- kb-demo-identity-fallback-runbook
change_log:
- author: papyrus-demo
  date: '2026-04-07'
  summary: Scenario seed revision.
---

## Demo Narrative

Approved known error before dependency drift.
