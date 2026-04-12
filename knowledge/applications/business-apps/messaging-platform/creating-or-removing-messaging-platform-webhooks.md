---
id: kb-applications-business-apps-messaging-platform-creating-or-removing-messaging-platform-webhooks
title: Creating or Removing <MESSAGING_PLATFORM> integration endpoints
canonical_path: knowledge/applications/business-apps/messaging-platform/creating-or-removing-messaging-platform-webhooks.md
summary: "Users will occasionally ask for <MESSAGING_PLATFORM> integration endpoints to be created so\
  \ they can automate notifications to their channels. Here\u2019s how."
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Creating or Removing <MESSAGING_PLATFORM> integration endpoints
team: Identity and Access
systems: []
tags: []
created: '2025-10-27'
updated: '2025-10-27'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
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

Users will occasionally ask for <MESSAGING_PLATFORM> webHooks to be created so they can automate notifications to their channels. Here’s how.

# **Instructions**

### **Adding new WebHooks to channels**

1. Make note of the channel(s) the user would like the WebHook in, they’ll ask for it in the ticket
2. Log into the <MESSAGING_PLATFORM> WebHook configuration site: [<INTERNAL_URL>](<INTERNAL_URL>)
3. Click the big green “ **Add to <MESSAGING_PLATFORM>** ” button underneath the WebHook icon
4. Under the section for ‘Post to Channel’, click the ‘Choose a channel…’ drop-down box and search for the requested channel from the ticket.
5. Click “ **Add Incoming WebHooks integration** ”
6. That will take you to a page telling you the integration was successful, scroll down to the ‘WebHook URL’ and copy that url string and post it in your reply to the user.

### **Disabling or removing Webhooks from channels:**

1. Head to the WebHook configuration site: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click the “ **Configuration** ” tab

1. Scroll down until you find the WebHook you’d like to disable or remove (they are sorted by Date Added). You may need to click to the Next page
2. Click the “ **Edit Configuration** ” pencil icon to the right of the WebHook
3. At the top-right of the page you can now disable it or remove it entirely
