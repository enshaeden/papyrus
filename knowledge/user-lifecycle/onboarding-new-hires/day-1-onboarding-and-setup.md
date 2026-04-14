---
id: kb-user-lifecycle-onboarding-new-hires-day-1-onboarding-and-setup
title: 'Day 1: Onboarding and Setup'
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/day-1-onboarding-and-setup.md
summary: New hire onboarding sessions are typically held on Mondays or on the designated start date set
  by HR .
knowledge_object_type: runbook
legacy_article_type: onboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: 'Day 1: Onboarding and Setup'
team: IT Operations
systems:
- <HR_SYSTEM>
tags:
- account
- onboarding
created: '2025-07-25'
updated: '2026-02-27'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services:
- Onboarding
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
- kb-user-lifecycle-onboarding-new-hires-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Onboarding
related_articles:
- kb-user-lifecycle-onboarding-new-hires-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

---

# Day 1: IT Onboarding

New hire onboarding sessions are typically held on **Mondays** or on the designated **start date** set by **HR** .

It is recommended that the onboarding team review the [Master New Hire Report: Access, Export, and Post-Onboarding Cleanup Guide](master-new-hire-report-access-export-and-post-onboarding-cleanup-guide.md) on the Friday prior to the next onboarding to confirm starting users for the next week.

### **Office Laptop Pickups:**

- **Local new hires** picking up laptops from the office are asked by **HR** to arrive at **9:00 AM** on Day 1.
- During this time, they will receive their laptop and complete setup with on-site IT support as needed.

### **Virtual IT Onboarding:**

- After laptop pickup (for local hires), or directly for **remote hires** , all new team members join a **<VIDEO_CONFERENCING_PLATFORM> session at 9:30 AM (local time)** .
  - The **HR team sends calendar invites** for this session in advance.
- The session covers:
  - An overview of **essential systems and tools**
    - **Live IT support** to address questions and assist with any setup issues
- At the start of the session, the IT team member will need to remove the new hires from the “New Hires Not Started” group in <IDENTITY_PROVIDER>.

This combined in-person and virtual approach ensures a smooth and consistent onboarding experience for all new hires, regardless of location.

> WARNING: If a new hire fails to show up for onboarding, follow the steps outlined in [Rescinded or Delayed onboarding Rescinded or Delayed onboarding](rescinded-or-delayed-onboarding.md)

---

> NOTE: **New Hire Onboarding Presentation**
>
> Please ensure you are familiar with the [**New Hire Onboarding Presentation**](<INTERNAL_URL>) , which is delivered weekly during IT onboarding sessions.
>
> #### **Presentation Delivery:**
>
> - A **member of the IT Help Desk** will present the onboarding slides each week.
> - Additional IT support may be scheduled if the onboarding class size is larger than usual.
>
> #### **Audience:**
>
> - The session is open to **FTEs** , **contractors** , and **interns** .
> - All participants are encouraged to submit any follow-up requests via the **Service Desk Portal** tile in **<IDENTITY_PROVIDER>** .
>
> All members of the IT team are expected to understand this process thoroughly in order to:
>
> - Step in and **substitute for the regular onboarding presenter** , if needed.
> - **Support users** during or after the session with any questions related to setup or access
