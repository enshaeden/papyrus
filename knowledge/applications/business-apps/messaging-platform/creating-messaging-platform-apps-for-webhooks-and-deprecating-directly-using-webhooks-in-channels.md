---
id: kb-applications-business-apps-messaging-platform-creating-messaging-platform-apps-for-webhooks-and-deprecating-directly-using-webhooks-in-channels
title: Creating <MESSAGING_PLATFORM> Apps For integration endpoints (and deprecating directly using integration
  endpoints in channels)
canonical_path: knowledge/applications/business-apps/messaging-platform/creating-messaging-platform-apps-for-webhooks-and-deprecating-directly-using-webhooks-in-channels.md
summary: 'You can always return to the main page of your App(s) here: <INTERNAL_URL>'
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Creating <MESSAGING_PLATFORM> Apps For integration endpoints (and deprecating directly using
  integration endpoints in channels)
team: IT Operations
systems: []
tags: []
created: '2025-10-22'
updated: '2025-10-22'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: it_ops
related_services:
- Collaboration
prerequisites:
- Verify the request, identity details, and required approvals before changing access or account state.
- Confirm the target system and business context match the scope of this article.
steps:
- Review the imported procedure body below and confirm the documented scope matches the task at hand.
- Execute the documented steps in order and record the outcome in the relevant ticket or audit trail.
- Stop and escalate if approvals, prerequisites, or expected checkpoints do not match the live request.
verification:
- The expected outcome described in the procedure is confirmed in the target system or ticket record.
- Completion notes, exceptions, and evidence are recorded in the relevant audit or support workflow.
rollback:
- Revert any reversible change described in the procedure if verification fails.
- Pause the workflow and escalate when the documented rollback path is unclear or incomplete.
citations:
- article_id: null
  source_title: <KNOWLEDGE_PORTAL> seed import manifest
  source_type: document
  source_ref: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-applications-business-apps-messaging-platform-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
related_articles:
- kb-applications-business-apps-messaging-platform-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Instructions**

### **Creating new <MESSAGING_PLATFORM> Apps**

1. Go to this site: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click the large green “Create new App” in the top-right
3. Select “From scratch”
  1. Give your App a name
    2. Select **<COMPANY_NAME>** as a workspace
    3. Click “Create App”
4. You’ll now be at the main screen for your app where you can customize nearly everything
5. Select **Incoming Webhooks**
6. Move the slider so it’s **On**
7. At the bottom of the page there’s now an option to **Add New Webhook to Workspace**
8. On the next page select a Channel to add your app to
  1. Click **Allow**
9. At the bottom of the page you’ll now see and be able to copy your Webhook URL

You can always return to the main page of your App(s) here: [<INTERNAL_URL>](<INTERNAL_URL>)
