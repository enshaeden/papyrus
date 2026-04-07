---
id: kb-user-lifecycle-onboarding-new-hires-hr-system-to-identity-provider-new-hire-account-staging-and-confirmation-process
title: '<HR_SYSTEM> to <IDENTITY_PROVIDER>: New Hire Account Staging and Confirmation Process'
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/hr-system-to-identity-provider-new-hire-account-staging-and-confirmation-process.md
summary: 'New Hire Workflow Overview: <ONBOARDING_WORKFLOW> < <HR_SYSTEM> < <TICKETING_SYSTEM> Ticket (<QUEUE_NAME>) Management New Hire Workflow Overview: <ONBOARDING_WORKFLOW> < <HR_SYSTEM> < <TICKETING_SYSTEM> Ticket (<QUEUE_NAME>) Management'
type: onboarding
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: '<HR_SYSTEM> to <IDENTITY_PROVIDER>: New Hire Account Staging and Confirmation Process'
team: Identity and Access
systems:
- <HR_SYSTEM>
- <IDENTITY_PROVIDER>
services:
- Identity
- Onboarding
tags:
- account
- authentication
- onboarding
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

New Hire Workflow Overview: <ONBOARDING_WORKFLOW> <> <HR_SYSTEM> <> <TICKETING_SYSTEM> Ticket (<QUEUE_NAME>) Management New Hire Workflow Overview: <ONBOARDING_WORKFLOW> <> <HR_SYSTEM> <> <TICKETING_SYSTEM> Ticket (<QUEUE_NAME>) Management

Once HR enters a new hire into <HR_SYSTEM> (WD), their account will automatically appear in <IDENTITY_PROVIDER> through the <HR_SYSTEM> integration.

## **Confirming New Hire Accounts in <IDENTITY_PROVIDER>**

note 3865d59a-0607-408e-ada1-046b959b8a3f ( [*video reference link*](<INTERNAL_URL>) , *skip to 2:55 timestamp* ) ( [*video reference link*](<INTERNAL_URL>) , *skip to 2:55 timestamp* )

1. Log in to **<IDENTITY_PROVIDER> Admin.**
2. In the Admin Dashboard, search for the **<HR_SYSTEM>** application.
3. Click the **“Import”** tab.
4. Use **Search** to locate the new hire accounts for the upcoming week **for your region only.**
5. **Check the box** next to each new hire’s name on the right side and Click **“Confirm Assignments.”**

1. Once assignment is confirmed user account status changes to **Staged** .

> INFO: Accounts should remain in Staged status after confirmation. This is the expected state until automation proceeds.

### **Platform-Specific Notes**

- **Mac User-** No Manual steps are required for FTE mac users.
- **Windows User:** If user will be assigned Windows Machine follow this guide to complete the account setup [**Workstation Setup Guide - Windows**](<INTERNAL_URL>)

### **Key Reminders**

> NOTE: **Do NOT manually activate accounts.**

Allow the automation to run as intended to ensure proper provisioning.

- Three days before the onboarding date, the status will automatically change to **"Pending User Action"** , indicating that:
  - <IDENTITY_PROVIDER> has sent activation instructions to the new hire.
    - Instructions include setting up their password and MFA token.
- The user’s personal email address must be entered as the Secondary Email in <IDENTITY_PROVIDER>
  - This is critical to ensure they receive activation instructions.

**For Rescinded Users**

In case of a rescinded new hire, please follow the Termination Process for that account, deactivate the user account and retrieve hardware if applicable (if an asset has been shipped).
