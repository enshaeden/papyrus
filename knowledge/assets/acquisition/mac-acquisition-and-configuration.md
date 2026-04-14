---
id: kb-assets-acquisition-mac-acquisition-and-configuration
title: Mac Acquisition and Configuration
canonical_path: knowledge/assets/acquisition/mac-acquisition-and-configuration.md
summary: All Mac laptops are configured through the automated device enrollment. Once purchased from an
  approved device supplier, devices are added to <ENDPOINT_ENROLLMENT_PORTAL> (<ENDPOINT_ENROLLMENT_PORTAL>)
  and are automatically enrolled in our <ENDPOINT_MANAGEMENT_PLATFORM> environment during the... Deprecated duplicate; use the deployment guide instead.
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: deprecated
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Mac Acquisition and Configuration
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- macos
created: '2026-02-25'
updated: '2026-03-02'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
prerequisites:
- Review the deployment guide before acting on Mac provisioning work.
- Use this deprecated page only to discover the replacement procedure during migration.
steps:
- Open the replacement deployment article and follow that procedure for Mac setup.
- Update any bookmarks or references that still point to this duplicate acquisition title.
- Do not use this page as the active operational source.
verification:
- The deployment article is the only active Mac provisioning path exposed from collection indexes.
- Remaining references to this duplicate are tracked for cleanup.
rollback:
- Restore the previous body from version control if the replacement selection proves incorrect.
- Re-open the deduplication review if distinct acquisition guidance is later recovered.
citations:
- article_id: kb-assets-deployment-mac-laptop-deployment
  source_title: Mac laptop Deployment
  source_type: document
  source_ref: knowledge/assets/deployment/mac-laptop-deployment.md
  note: Active replacement for this duplicate Mac provisioning article.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-assets-acquisition-index
- kb-assets-deployment-mac-laptop-deployment
superseded_by: kb-assets-deployment-mac-laptop-deployment
replaced_by: kb-assets-deployment-mac-laptop-deployment
retirement_reason: Deprecated during canonical deduplication because this article duplicated the Mac deployment procedure.
services:
- Endpoint Provisioning
related_articles:
- kb-assets-acquisition-index
- kb-assets-deployment-mac-laptop-deployment
references:
- title: Mac laptop Deployment
  article_id: kb-assets-deployment-mac-laptop-deployment
  path: knowledge/assets/deployment/mac-laptop-deployment.md
  note: Active replacement for this duplicate Mac provisioning article.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
- date: '2026-04-07'
  summary: Deprecated as a duplicate of the Mac deployment procedure.
  author: codex
---

## Deprecation Notice

This imported title duplicated the active Mac provisioning workflow. Use [Mac laptop Deployment](../deployment/mac-laptop-deployment.md) for current operator guidance.
