---
id: kb-user-lifecycle-onboarding-new-hires-day-1-preparing-accounts-and-devices
title: 'Day -1: Preparing Accounts and Devices'
canonical_path: knowledge/user-lifecycle/onboarding-new-hires/day-1-preparing-accounts-and-devices.md
summary: 'Tickets for new hires are generated per the New Hire Workflow Overview: <ONBOARDING_WORKFLOW>
  < <HR_SYSTEM> < <TICKETING_SYSTEM> Ticket (<QUEUE_NAME>) Management New Hire Workflow Overview: <ONBOARDING_WORKFLOW>
  < <HR_SYSTEM> < <TICKETING_SYSTEM> Ticket (<QUEUE_NAME>) Management'
knowledge_object_type: runbook
legacy_article_type: onboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: 'Day -1: Preparing Accounts and Devices'
team: IT Operations
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <HR_SYSTEM>
tags:
- endpoint
- account
- onboarding
created: '2026-02-25'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services:
- Endpoint Provisioning
- Identity
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
- Endpoint Provisioning
- Identity
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

> INFO: Review the current onboarding training reference before executing this procedure.

# <TICKETING_SYSTEM> Ticket Checklist

Tickets for new hires are generated through the approved onboarding workflow that routes worker data from `<HR_SYSTEM>` into `<TICKETING_SYSTEM>`.

# **Initial Steps**

1. **Acknowledge the ticket** promptly upon receiving it.
2. **Assign** the ticket to the appropriate regional technician based on the new hire’s location.
3. The assignee should **review the role and hardware requirements** , check available inventory, and plan the setup accordingly.

# **Actioning the ticket**

As you progress through each step make sure to include the following details.

## Setting up the accounts

### [<HR_SYSTEM> to <IDENTITY_PROVIDER>: New Hire Account Staging and Confirmation Process](hr-system-to-identity-provider-new-hire-account-staging-and-confirmation-process.md)

1. Record the date the user’s account was moved to **Staged status in <IDENTITY_PROVIDER>** .

### [Application Access for New Employees and Contractors **Application Assignments**](application-access-for-new-employees-and-contractors.md)

1. Confirm all required applications are assigned.
  - Check for **assignment errors** in <IDENTITY_PROVIDER>. Note that apps may not appear immediately—review again **before the start date** to ensure accuracy.

## Provisioning devices

### Step by Step Guide for New User Setup **Device Selection & Setup**

Follow the steps for device provisioning as outlined in [Asset Deployment Asset Deployment](../../assets/deployment/asset-deployment.md)

> INFO: **Update the <TICKETING_SYSTEM> ticket** for the new hire with asset assignment information for tracking and audit purposes.

### [Shipping Instructions and Best Practices **Shipping Details**](../../assets/shipping/shipping-instructions-and-best-practices.md) **(if applicable)**

1. Include shipping info and **tracking number** in the ticket.
  - Attach the **label** if available and relevant.

## **<IDENTITY_PROVIDER> Activation date**

This step should be automated and occurs 3 days prior to their start date (usually Friday of the week before)

> WARNING: **Do not close the ticket** until the new hire has started and successfully logged in.
>
> If a **duplicate ticket** is created, **link it to the main ticket** to maintain proper ticket hygiene.
