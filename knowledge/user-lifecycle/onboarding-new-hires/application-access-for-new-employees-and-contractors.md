---
id: kb-user-lifecycle-onboarding-new-hires-application-access-for-new-employees-and-contractors
title: Application Access for New Employees and Contractors
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/application-access-for-new-employees-and-contractors.md
summary: "Most application access is provisioned automatically based on the user\u2019s role and department , covering both Full Time Employees (FTEs) and Contractors (Extended Users) ."
type: onboarding
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Application Access for New Employees and Contractors
team: Identity and Access
systems:
- <HR_SYSTEM>
services:
- Access Management
- Onboarding
tags:
- account
- onboarding
- access
created: '2026-02-25'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
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
related_articles:
- kb-user-lifecycle-onboarding-new-hires-index
replaced_by: null
retirement_reason: null
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

Most application access is provisioned **automatically** based on the user’s **role** and **department** , covering both **Full-Time Employees (FTEs)** and **Contractors (Extended Users)** .

# **Preparation Before Start Date**

To ensure a smooth Day 1 experience, IT should:

- **Review <IDENTITY_PROVIDER> for assignment issues** Confirm that applications have been correctly assigned—resolve any errors before the start date.
- **Verify license-based applications** Ensure that licenses for apps like **<VIDEO_CONFERENCING_PLATFORM>, <MESSAGING_PLATFORM>, and email** are available and properly assigned. This helps avoid last-minute delays and ensures full access on Day 1.

# **Requesting Additional Applications**

During IT onboarding, users are instructed to use the **<IDENTITY_PROVIDER> App Request** tile:

- If the needed application is listed, users can request access or a license directly.
- If the application is not listed, they can submit a request using the **General App Request** form within the same tile.

## For Contractors:

- Add the user to the [<COMPANY_NAME> All](<INTERNAL_URL>) group in <COLLABORATION_PLATFORM>.

> INFO: All users receive the all-hands meeting invite via this group.

- Key applications such as <MESSAGING_PLATFORM> and <VIDEO_CONFERENCING_PLATFORM> may need to be manually assigned. Other tools can be provisioned gradually after the start date, depending on role requirements.

[**Review - Contractor System Access Guide**](<INTERNAL_URL>)

## Special Cases: [Re-Hire Account Setup Process for IT Returning Contractors / Rehires](../employee-rehire/re-hire-account-setup-process-for-it.md)

- Review any previous app assignments and confirm they are still valid for the new contract.
- Do not rely on past configurations—some access may have expired or changed.
- Reassign or remove applications based on current role requirements.
