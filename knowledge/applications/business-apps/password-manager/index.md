---
id: kb-applications-business-apps-password-manager-index
title: Applications / Business Apps / <PASSWORD_MANAGER>
canonical_path: knowledge/applications/business-apps/password-manager/index.md
summary: Collection index for curated seed content under Applications / Business Apps / <PASSWORD_MANAGER>.
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: derived
source_system: knowledge_portal
source_title: Applications / Business Apps / <PASSWORD_MANAGER>
team: IT Operations
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
created: '2026-04-07'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: it_ops
service_name: Identity
service_criticality: not_classified
dependencies:
- <IDENTITY_PROVIDER>
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks:
- kb-applications-business-apps-password-manager-password-manager-invitation
- kb-applications-business-apps-password-manager-account-recovery
- kb-applications-business-apps-password-manager-vault-owner-in-password-manager
- kb-applications-business-apps-password-manager-vault-access-in-password-manager
- kb-applications-business-apps-password-manager-vault-creation
related_known_errors: []
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: docs/migration/seed-migration-rationale.md
  note: Collection Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-applications-business-apps-password-manager-password-manager-invitation
- kb-applications-business-apps-password-manager-account-recovery
- kb-applications-business-apps-password-manager-vault-owner-in-password-manager
- kb-applications-business-apps-password-manager-vault-access-in-password-manager
- kb-applications-business-apps-password-manager-vault-creation
prerequisites:
- Review the collection summary and choose the child article that matches the task before acting.
- Confirm the target region, platform, or lifecycle path aligns with the selected child article.
steps:
- Read the collection overview to identify the correct workflow or region-specific article.
- Open the relevant child article and follow its procedure exactly rather than acting from the collection
  summary alone.
- Record exceptions or missing migration details for follow-up in the migration manifest or rationale
  doc.
verification:
- The selected child article clearly matches the task, region, and system in scope.
- Operators can navigate from this collection page to the required child articles without ambiguity.
rollback:
- Use the child article rollback guidance for any operational change; this collection page is navigation-only
  context.
- Escalate to the owning team if none of the child articles match the task safely.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
related_articles:
- kb-applications-business-apps-password-manager-password-manager-invitation
- kb-applications-business-apps-password-manager-account-recovery
- kb-applications-business-apps-password-manager-vault-owner-in-password-manager
- kb-applications-business-apps-password-manager-vault-access-in-password-manager
- kb-applications-business-apps-password-manager-vault-creation
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Collection Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Created as synthetic collection index during <KNOWLEDGE_PORTAL> seed migration.
  author: seed_sanitization
---

## Scope
This collection page was created during the <KNOWLEDGE_PORTAL> seed migration to organize password manager procedures under the curated KMDB structure.

## Articles
- [<PASSWORD_MANAGER> Invitation](password-manager-invitation.md)
- [Account recovery](account-recovery.md)
- [Vault Owner in <PASSWORD_MANAGER>](vault-owner-in-password-manager.md)
- [Vault access in <PASSWORD_MANAGER>](vault-access-in-password-manager.md)
- [Vault creation](vault-creation.md)

## Migration Notes
- This page is a collection index. Use the linked child articles for actionable procedures.
