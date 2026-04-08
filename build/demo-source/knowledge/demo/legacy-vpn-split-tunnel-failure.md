---
id: kb-demo-evidence-gap-known-error
title: Legacy VPN Split-Tunnel Failure
canonical_path: knowledge/demo/legacy-vpn-split-tunnel-failure.md
summary: Demo scenario object for legacy vpn split-tunnel failure
knowledge_object_type: known_error
legacy_article_type: null
status: active
owner: remote_access_ops
source_type: native
source_system: repository
source_title: Legacy VPN Split-Tunnel Failure
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
- Remote Access
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
  note: Imported note not yet re-verified.
  source_ref: docs/reference/operator-web-ui.md
  source_title: Legacy split-tunnel notes
  source_type: document
  validity_status: unverified
related_object_ids:
- kb-demo-remote-access-service-record
- kb-demo-vpn-recovery-runbook
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Remote Access
references:
- note: Imported note not yet re-verified.
  path: docs/reference/operator-web-ui.md
  title: Legacy split-tunnel notes
related_articles:
- kb-demo-remote-access-service-record
- kb-demo-vpn-recovery-runbook
change_log:
- author: papyrus-demo
  date: '2026-04-07'
  summary: Scenario seed revision.
---

## Demo Narrative

Known error preserved with weak evidence for demo.
