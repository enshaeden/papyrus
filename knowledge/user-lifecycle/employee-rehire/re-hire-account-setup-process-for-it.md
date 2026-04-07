---
id: kb-user-lifecycle-employee-rehire-re-hire-account-setup-process-for-it
title: Re-Hire Account Setup Process for IT
canonical_path: knowledge/user-lifecycle/employee-rehire/re-hire-account-setup-process-for-it.md
summary: This document outlines the step by step process for the IT team to accurately complete the account setup for re hired employees. It ensures smooth account reactivation and avoids duplication or access conflicts...
type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Re-Hire Account Setup Process for IT
team: Identity and Access
systems:
- <HR_SYSTEM>
services:
- Identity
tags:
- account
created: '2025-12-05'
updated: '2025-12-05'
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
- kb-user-lifecycle-employee-rehire-index
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

# **1. Purpose**

This document outlines the step-by-step process for the IT team to accurately complete the account setup for re-hired employees. It ensures smooth account reactivation and avoids duplication or access conflicts across integrated systems.

# **2. Scope**

This process applies to:

- All Full-Time Employees (FTEs) and Contractors (<TEAM_NAME> users) being re-hired who have an existing account in <IDENTITY_PROVIDER> and <HR_SYSTEM>.
- The IT team responsible for user provisioning, account activation, and access management.

# **3. Re-Hire Workflow Overview (<ONBOARDING_WORKFLOW> → <HR_SYSTEM> → IT)**

The re-hire process begins in <ONBOARDING_WORKFLOW> (recruitment platform) and <HR_SYSTEM> (HR system) before transitioning to the IT onboarding workflow.

## **a. Candidate Hired in <ONBOARDING_WORKFLOW>**

When a recruiter moves a candidate to the "Hire" stage in <ONBOARDING_WORKFLOW>, the system automatically pushes the candidate’s details into <HR_SYSTEM>.

## **b. Candidate Accepted in <HR_SYSTEM>**

Once HR accepts the candidate in <HR_SYSTEM>, it triggers:

- Creation of the user profile in <HR_SYSTEM>.
- An automated Welcome Email sent to the new hire.

Sometimes, a conflict error may occur while importing users from <HR_SYSTEM> to <IDENTITY_PROVIDER>. To resolve this:

1. Activate the user account in <IDENTITY_PROVIDER> first.
2. Retry the import after activation to complete synchronization.

# **4. <TICKETING_SYSTEM> Ticket Creation**

- <HR_SYSTEM> automatically creates a <TICKETING_SYSTEM> ticket for the new hire.
- The ticket is routed to the <TICKETING_SYSTEM> New Hire Queue for IT visibility and tracking.

# **5. Account Activation (Joining Date)**

- On the joining date, the IT team will reactivate the existing user account in <IDENTITY_PROVIDER>.
- After reactivation, the user will automatically receive an email prompt to reset their <IDENTITY_PROVIDER> password and regain access to their account and assigned applications.

# **6. Responsibilities**

| **Team** | **Responsibility** |
| --- | --- |
| HR Team | Manages candidate hire and approval workflow in <ONBOARDING_WORKFLOW> and <HR_SYSTEM>. |
| IT Team | Handles account activation, rehire synchronization, and user access restoration in <IDENTITY_PROVIDER>. |
| Recruitment Team | Moves candidates to the "Hire" stage and ensures details are correctly synced to <HR_SYSTEM>. |
