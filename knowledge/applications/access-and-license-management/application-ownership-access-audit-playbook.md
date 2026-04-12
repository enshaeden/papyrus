---
id: kb-applications-access-and-license-management-application-ownership-access-audit-playbook
title: Application Ownership & Access Audit Playbook
canonical_path: knowledge/applications/access-and-license-management/application-ownership-access-audit-playbook.md
summary: This article centralizes <BUSINESS_APPLICATION_C> emails, the <ASSET_MANAGEMENT_SYSTEM> mapping,
  and a plug and play <KNOWLEDGE_PORTAL> article template to use after owner confirmation.
knowledge_object_type: runbook
legacy_article_type: SOP
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Application Ownership & Access Audit Playbook
team: Identity and Access
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- account
- access
created: '2025-11-17'
updated: '2025-11-28'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Access Management
prerequisites:
- Review the scope, approvals, and dependencies described in this article before starting.
- Confirm you have the required systems access and escalation path before proceeding.
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
- kb-applications-access-and-license-management-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-access-and-license-management-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Overview

This article centralizes <BUSINESS_APPLICATION_C> emails, the <ASSET_MANAGEMENT_SYSTEM> mapping, and a plug-and-play <KNOWLEDGE_PORTAL> article template to use after owner confirmation.

## 1. Quick Steps

1. Send the **Initial Email** to the app owner (below) and ask for a reply by **[DATE] within 5 business days** .
2. When they confirm/update, create/update a **<KNOWLEDGE_PORTAL> article** with the **Software Article Template** (Section 3).
3. Set **Status** to **Verified** (or **Pending** if partial info). Add **Last Verified** date in both <APPLICATION_CATALOG> ticket routing and <KNOWLEDGE_PORTAL>.

---

## 2. Workflow at a Glance

1. Identify row(s) in <ASSET_MANAGEMENT_SYSTEM> for <BUSINESS_APPLICATION_C>.
2. Send **Initial <BUSINESS_APPLICATION_C>** email to Owner (below).
3. If no response, send **Reminder** ; then **Manager Escalation** if needed.
4. Once confirmed, **create the <KNOWLEDGE_PORTAL> Software article** using the template in Section 5.
5. Apply labels and set a verification status.
6. The article auto‑rolls up into the **Audit Dashboard** (Section 6) via metadata rollup table.

**SLA suggestions**

- Owner response target: 5 business days
- Reminder: 2–3 business days before deadline
- Escalation: next business day after deadline

---

## 3. <ASSET_MANAGEMENT_SYSTEM> → <KNOWLEDGE_PORTAL> Field Mapping

Create a **metadata table** table with the following keys and values (see Section 5 template).

| <ASSET_MANAGEMENT_SYSTEM> Column | <KNOWLEDGE_PORTAL> Field (Key) | Type / Allowed Values | Example |
| --- | --- | --- | --- |
| Software | Software | Text | <BUSINESS_APPLICATION_A> |
| Manager Approval Required- Yes/No | Manager Approval Required | **Yes / No** | Yes |
| Support Team | Support Team | Team/Group name | IT Apps |
| Owner | Owner | Name & email | <PERSON_NAME> ( <EMAIL_ADDRESS> ) |
| Process | Process | Short text or link | Submit request via <IDENTITY_PROVIDER> App Request→ Manager approves |
| User notes | User Notes | Free text | Use SSO; license is limited |
| Available for Contractors - Yes/No/With Approval | Available for Contractors | **Yes / No / With Approval** | With Approval (director) |

**Additional recommended fields**

- Verification Status (Status block): Verified / Unverified / Pending
- Last Verified (Date)
- Source Ticket(s) (link/ID)
- Change Log (Table)

---

## 4. Owner Confirmation Emails (Copy‑ready)

> Paste into your email client and fill bracketed fields. Keep the subject line consistent for threading.

### 4.1 Initial <BUSINESS_APPLICATION_C> (to Owner)

**Subject:** Action required: Verify details for **[Software]**

Hi [First Name],

We’re auditing application records that were previously tracked in tickets. Before we create the <KNOWLEDGE_PORTAL> article for **[Software]** , please review what we have and **reply by [DATE]** with either “Confirmed—no changes” or edits using the template below.

**What we have on file**

- **Software:** [Software]
- **Manager Approval Required:** [Yes/No]
- **Support Team:** [Team/Group or “N/A”]
- **Owner:** [Name, email]
- **Process:** [Brief steps or link to request/approval process]
- **User Notes:** [Free text]
- **Available for Contractors:** [Yes/No/With Approval]

If you’re **not the right owner** , please reply with the correct owner’s name & email.

Once you confirm, we’ll create the <KNOWLEDGE_PORTAL> article with these details.

Thanks,

**Reply template (edit inline and send back):**

`Software: [Software]`

`Manager Approval Required: Yes / No`

`Support Team: [Team/Group or “N/A”]`

`Owner: [Name, email]`

`Process: [Brief steps; if approval needed, include who approves]`

`User Notes: [Any notes users should know]`

`Available for Contractors: Yes / No / With Approval`

`I am the current owner: Yes / No (if No, provide correct owner)`

`Other changes or context:`

### 4.2 Reminder (2–5 business days before deadline)

**Subject:** Reminder: Verify **[Software]** details by **[DATE]**

Hi [First Name],

Quick nudge to confirm **[Software]** details by **[DATE]** so we can create the <KNOWLEDGE_PORTAL> article. You can simply reply “Confirmed—no changes” or paste the template from my last email with edits.

If you’re not the right owner, please share the correct contact.

Thanks! [Your Name]

### 4.3 Manager Escalation (no response)

**Subject:** Escalation: Ownership & access confirmation needed for **[Software]**

Hi [Manager Name],

We’re finalizing the audit for **[Software]** and haven’t received a response from **[Owner Name]** . Could you help confirm the correct owner and any updates by **[DATE]** ? We will create the <KNOWLEDGE_PORTAL> article after confirmation.

Fields to confirm:

- Manager Approval Required (Yes/No)
- Support Team
- Owner
- Process (how to request / approval path)
- User Notes
- Available for Contractors (Yes/No/With Approval)

Thank you, [Your Name]

### 4.4 Close‑out (after confirmation)

**Subject:** Confirmed: Creating <KNOWLEDGE_PORTAL> record for **[Software]**

Hi [First Name],

Thanks for confirming. We’ll create the <KNOWLEDGE_PORTAL> article using the details you provided. If anything changes later, reply to this thread and we’ll update the record.

Best, [Your Name]

---

## 5. **Software Article Template** (create/update after owner confirms)

> Create/Update one article per application using the structure below. **Wrap the first table in a metadata table block** (Insert → View More → *metadata table* ), so it rolls up to the dashboard.

**Recommended title format:** `Software: [Software]`

**Apply labels:**

**Status (insert block):** Verification Status = **Verified / Pending / Unverified**

**Last Verified:** [YYYY‑MM‑DD]

**Source Ticket(s):** Link or ID

**metadata table (wrap this entire table in the block)**

| Column 1 | Column 2 |
| --- | --- |
| Key | Value |
| Software | [Software] |
| Manager Approval Required | [Yes/No] |
| Support Team | [Team/Group or “N/A”] |
| Owner | [Name, email] |
| Process | [Short steps or link to detailed process] |
| User Notes | [Free text] |
| Available for Contractors | [Yes / No / With Approval] |

**Change Log**

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Date | Change | By |
| YYYY‑MM‑DD | Initial creation based on owner confirmation | [Your Name] |

**Details & References**

- Request/Approval workflow: [Link]
- Additional docs: [Links]

---

## 6. Audit Dashboard (Parent Article) Setup

Create a parent article titled **“Application Audit Dashboard (2025)”** and insert a **metadata rollup table** block configured as follows:

- **Labels:** `software-record`
- **Spaces:** [this knowledge collection]
- **Columns to show (matching keys):** Software, Owner, Manager Approval Required, Support Team, Available for Contractors
- **Additional columns:** Verification Status, Last Verified (add as “related content” columns if your instance supports it, or keep them outside the block at top of each article)
- **Sort by:** Software (A → Z) or Last Verified (newest first)

Optional filters:

- **Verification Status = Unverified** (for follow‑up queue)
- **Available for Contractors = Yes/With Approval** (for additional review)

**Tip:** Keep each Software article a child of the dashboard for easier navigation and permissions.

---

## 7. Quality Checks

- **Owner identity:** Confirm name *and* email; if redirected, update immediately.
- **Manager Approval Required:** If “Yes” or “With Approval,” ensure **Process** clearly states who approves and where.
- **Contractors:** If allowed, validate the request path includes additional oversight (e.g., director approval).
- **Support Team:** Use the official team name used in your directory/ITSM.
- **Last Verified:** Update the date any time the article changes.

---

## 8. Definitions

- **Process:** How a user requests access and how it is approved (system, approver, any SLAs).
- **User Notes:** Anything the end user should know (e.g., SSO required, license limits, device requirements).
- **Available for Contractors:** Whether non‑employees can be granted access; if **With Approval** , specify who must approve.
