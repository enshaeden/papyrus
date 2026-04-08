---
id: kb-assets-loaners-loaner-laptop-policy-region-a
title: Loaner Laptop Policy- <REGION_A>
canonical_path: knowledge/assets/loaners/loaner-laptop-policy-region-a.md
summary: Deprecated <REGION_A>-specific policy variant. Use the shared loaner policy plus the <REGION_A> access page.
knowledge_object_type: runbook
legacy_article_type: asset
status: deprecated
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Loaner Laptop Policy- <REGION_A>
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- endpoint
created: '2025-12-11'
updated: '2025-12-11'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
prerequisites:
- Review the shared loaner-device policy before acting on any new request.
- Use this deprecated page only to discover the maintained <REGION_A> workflow.
steps:
- Open the shared loaner-device policy for eligibility, inventory-state, and ticketing rules.
- Open the <REGION_A> location and access page for local pickup and approval details.
- Update references that still point to this duplicate regional policy title.
verification:
- Operators can reach the shared policy and the <REGION_A> access page without relying on this duplicate.
- The active workflow is expressed as shared policy plus regional access page rather than a copied regional policy.
rollback:
- Restore the previous body from version control if the shared policy and regional access page no longer cover this workflow.
- Re-open the variant-model review if a distinct <REGION_A>-only procedure is recovered later.
citations:
- article_id: kb-assets-loaners-loaner-laptops
  source_title: Loaner Laptops
  source_type: document
  source_ref: knowledge/assets/loaners/loaner-laptops.md
  note: Shared replacement for the regional policy copy.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
- article_id: kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
  source_title: <REGION_A> Loaner Location and Access for Remote Support
  source_type: document
  source_ref: knowledge/assets/loaners/region-a-loaner-location-and-access-for-remote-support.md
  note: Regional pickup and access page paired with the shared policy.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-assets-loaners-index
- kb-assets-loaners-loaner-laptops
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
superseded_by: kb-assets-loaners-loaner-laptops
replaced_by: kb-assets-loaners-loaner-laptops
retirement_reason: Deprecated during loaner-family normalization because <REGION_A>-specific differences now live in the regional access page instead of a copied policy body.
services:
- Endpoint Provisioning
related_articles:
- kb-assets-loaners-index
- kb-assets-loaners-loaner-laptops
- kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
references:
- title: Loaner Laptops
  article_id: kb-assets-loaners-loaner-laptops
  path: knowledge/assets/loaners/loaner-laptops.md
  note: Shared loaner-device policy replacing this duplicate.
- title: <REGION_A> Loaner Location and Access for Remote Support
  article_id: kb-assets-loaners-region-a-loaner-location-and-access-for-remote-support
  path: knowledge/assets/loaners/region-a-loaner-location-and-access-for-remote-support.md
  note: Regional access page paired with the shared policy.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
- date: '2026-04-07'
  summary: Deprecated this regional duplicate in favor of the shared loaner policy plus the regional access page.
  author: codex
---

## Deprecation Notice

This regional copy is no longer the maintained source. Use [Loaner Laptops](loaner-laptops.md) for the shared policy and [<REGION_A> Loaner Location and Access for Remote Support](region-a-loaner-location-and-access-for-remote-support.md) for the local pickup and approval flow.
