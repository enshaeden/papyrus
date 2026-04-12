---
id: kb-applications-business-apps-developer-tool-suite-adding-new-developer-tool-suite-licenses
title: Adding new <DEVELOPER_TOOL_SUITE> licenses
canonical_path: knowledge/applications/business-apps/developer-tool-suite/adding-new-developer-tool-suite-licenses.md
summary: We have moved to a new process for adding <DEVELOPER_TOOL_SUITE> licenses to our account and
  giving them to users.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Adding new <DEVELOPER_TOOL_SUITE> licenses
team: Identity and Access
systems: []
tags:
- access
created: '2025-10-28'
updated: '2025-10-28'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
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
- kb-applications-business-apps-developer-tool-suite-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-business-apps-developer-tool-suite-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

We have moved to a new process for adding <DEVELOPER_TOOL_SUITE> licenses to our account and giving them to users.

# **Instructions**

### **Prepare the ticket**

1. Confirm manager’s approval for license
2. Add users manager and <EMAIL_ADDRESS> to watchers of the ticket
  1. Send internal note to Brittney a new license(s) is on the way

### **Adding new licenses to our account**

1. Log into [<INTERNAL_URL>](<INTERNAL_URL>)
2. First check that we don’t already have a spare license to deploy to the requesting user. If so, grant that and you’re done!

1. If we need an additional license:
  1. Click the “ **Buy new License** ” icon

1. Find the requested product, select the checkbox, and (if necessary) select the amount needed

1. Once you’ve selected the products you’d like, click the “ **Get Quote** ” button at bottom of the page
2. On the quote page, select the Team drop-down and use: **<COMPANY_NAME>**
3. The **Subscription Pack** will autofill to our annual subscription

1. Click **Submit Request** (this will send you an email with a formal pdf quote)

### **Create PO for the products purchased**

1. Head to <IDENTITY_PROVIDER> > Coupa
2. Click the button to “ **Order Software** ”

1. Click “ **Create a Purchase Request** ”
2. Fill in the fields with the requested information from the quote in step **3-D** above and click “ **Submit** ”
  1. Note: Do NOT include tax in this order. Use the subtotal only.

### **Grant the new license(s) to user(s)**

1. Once the request has been approved, head back to the purchase order and scroll down near the price and select **Supplier Print View**

1. Save that PDF and email it to <EMAIL_ADDRESS>
  1. In the email, be sure to say, ”Tax for this order will be paid upon receipt of the invoice.”
2. They will respond with an invoice and grant a license to your <DEVELOPER_TOOL_SUITE> admin site
3. Click on **Active subscriptions** under the product requested (there should now be a “1 unused” next to the name)

1. At the top of the list will be an unassigned license. At the right click **Assign**

1. Type in the email address for the user
  1. If the First and Last name don’t autofill via the email, add those as well
2. Click **Assign**
