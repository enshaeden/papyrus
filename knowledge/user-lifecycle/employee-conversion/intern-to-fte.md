---
id: kb-user-lifecycle-employee-conversion-intern-to-fte
title: Intern to FTE
canonical_path: knowledge/user-lifecycle/employee-conversion/intern-to-fte.md
summary: Overview
knowledge_object_type: runbook
legacy_article_type: runbook
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Intern to FTE
team: Identity and Access
systems:
- <HR_SYSTEM>
tags:
- account
created: '2025-11-03'
updated: '2025-11-14'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
related_services: []
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
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-user-lifecycle-employee-conversion-index
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-user-lifecycle-employee-conversion-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

**Overview**

This SOP outlines the steps the IT team must follow when an employee from **Full-Time Employee - Intern (FTC-Intern)** to a **Full-Time Employee (FTE)** .

## Instructions

1. **Offer Acceptance**

- An Intern accepts the offer to become a full-time employee.
- The hiring manager of the Intern contacts the HR team via <MESSAGING_PLATFORM> to individual team members regarding the conversion date.
- The HR team inputs the Intern’s end date and pushes that information to the record in <HR_SYSTEM>.
- The Recruiting team initiates the offer and hire in <ONBOARDING_WORKFLOW>, and then <TEAM_NAME> initiates the hire and onboarding in <HR_SYSTEM> with same details as earlier.
- People ops team is responsible to manually update the details like first name, last name and email address of the intern as it was earlier.

1. **<HR_SYSTEM> Processing and <TICKETING_SYSTEM> Ticket Creation**

- IT should receive an Employe conversion i.,e Job change ticket at least 1 week before the conversion. We should also receive the Intern termination ticket and FTE New hire ticket of the user.
- IT should link all those <TICKETING_SYSTEM> tickets and work on them.
- The intern’s existing **<HR_SYSTEM> profile** is scheduled to be updated on the **conversion date** by the people ops team.

1. **<HR_SYSTEM> Profile Update on Conversion Day**

- On the effective date of employment:
  - The intern’s **existing <HR_SYSTEM> profile** is updated to reflect their new status as an FTE.
    - No changes in details like first name, last name and email address
    - But other relevant attributes (job title, department, employment type)should be updated accordingly.
    - **Important:** If <HR_SYSTEM> processes this as a termination and rehire instead of an in-place update, the user’s <IDENTITY_PROVIDER> profile could be deactivated. Coordinate with HR to ensure the profile remains active 1 day prior to the conversation date.

1. **Automatic Sync to <IDENTITY_PROVIDER> and <COLLABORATION_PLATFORM> Admin**

- Once the profile update is complete in <HR_SYSTEM>:
  - **<IDENTITY_PROVIDER>** and **<COLLABORATION_PLATFORM> Admin** automatically sync and reflect the same email but different user attributes.
    - The email and other system logins will remain un-affected.

IT should verify that the sync completes without errors and that both <IDENTITY_PROVIDER> and <COLLABORATION_PLATFORM> show the updated details and correct them if an discrepancy.

1. **Manual Review and Updates in <IDENTITY_PROVIDER>**

- Confirm all <IDENTITY_PROVIDER>-assigned application access
  - Note: Make sure to change the assignment back to group to avoid stale accounts. Also users might be a member of multiple assignment groups, so ideally assignment group value should be noted prior to assignment conversion to individual.

1. **IT-Managed and other Applications access**

IT Managed and others apps access will be un-affected with this change but if user might need additional which must be reviewed and processed.

1. **Confirm with User and Close Ticket**

- Confirm access to all systems
- Update and close <TICKETING_SYSTEM> ticket

Thank you for following this SOP. If you have any feedback or notice process gaps, please inform the IT leadership team so the document can be improved.

## Related articles

[Day 1: Onboarding and Setup Overview of New User Account Setup](../onboarding-new-hires/day-1-onboarding-and-setup.md)
