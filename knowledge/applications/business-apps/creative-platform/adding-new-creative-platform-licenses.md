---
id: kb-applications-business-apps-creative-platform-adding-new-creative-platform-licenses
title: Adding new <CREATIVE_PLATFORM> licenses
canonical_path: knowledge/applications/business-apps/creative-platform/adding-new-creative-platform-licenses.md
summary: We have moved to purchasing new <CREATIVE_PLATFORM> licenses from CDW. This will be a quick walkthrough
  on how to do that.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Adding new <CREATIVE_PLATFORM> licenses
team: IT Operations
systems: []
tags:
- access
created: '2025-10-27'
updated: '2025-10-27'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: it_ops
related_services:
- Access Management
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
- kb-applications-business-apps-creative-platform-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-business-apps-creative-platform-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

We have moved to purchasing new <CREATIVE_PLATFORM> licenses from CDW. This will be a quick walkthrough on how to do that.

# **Instructions**

### **Prepare the ticket**

1. Confirm manager’s approval for license
2. Add users manager and <EMAIL_ADDRESS> to watchers of the ticket
  1. Send internal note in the ticket to Brittney a new license(s) is on the way

### **Requesting new licenses**

1. Log into [<INTERNAL_URL>](<INTERNAL_URL>)
2. First check that we don’t already have a spare license to deploy to the requesting user. If so, grant that and you’re done! (Please semi-regularly make sure there are no users with licenses that are no longer at the company. Free up those licenses too)
3. If we need an additional license:
  1. Head to Coupa > CDW
    2. In CDW, search for the specific CDW part number from the grid based on the purchase month and the product requested GRID: [<INTERNAL_URL>](<INTERNAL_URL>)
      1. Please ask Helpdesk if you do not have access to the price grid. It also updates yearly
          2. The month you are using at the top is the month it currently is. ex: If it’s currently July when the user requested Acrobat Pro, use the July column
    3. When you’ve found the specific item, click **Add to Cart**
    4. Click **Checkout**
    5. Click **Transfer Shopping Cart**
    6. Complete the fields in the Coupa request
    7. Click **Submit for Approval**
    8. After approvals, the license will be added to your <CREATIVE_PLATFORM> admin portal

**Granting the new license to the user**

1. Log into [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click the product you’ve added in the bottom-left
3. Click **Add User** and enter the email address of the user requesting the program
4. Back in the ticket, respond the user by letting them know to check their email for the license and walk-through on installing the program
