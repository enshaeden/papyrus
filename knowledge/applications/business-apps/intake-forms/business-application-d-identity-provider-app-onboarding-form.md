---
id: kb-applications-business-apps-intake-forms-business-application-d-identity-provider-app-onboarding-form
title: <BUSINESS_APPLICATION_D> <IDENTITY_PROVIDER> App Onboarding Form
canonical_path: knowledge/applications/business-apps/intake-forms/business-application-d-identity-provider-app-onboarding-form.md
summary: Canonical article for <BUSINESS_APPLICATION_D> <IDENTITY_PROVIDER> App Onboarding Form imported from <KNOWLEDGE_PORTAL>.
type: reference
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: <BUSINESS_APPLICATION_D> <IDENTITY_PROVIDER> App Onboarding Form
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
created: '2025-10-27'
updated: '2025-10-27'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
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
related_articles:
- kb-applications-business-apps-intake-forms-index
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

1. **Application Details for <IDENTITY_PROVIDER> Access Requests**
  1. **Application Name** (as it appears in <IDENTITY_PROVIDER>) <BUSINESS_APPLICATION_D>
    2. **Description of the App** (end-user friendly explanation of what it does) Live captioning for Spark ‘25 sessions
    3. **App Owner Contact** (for approval routing and escalation) <EMAIL_ADDRESS>
    4. **App Category/Type** (e.g., Engineering, Finance, HR) Marketing/Events
    5. **Link to SSO and provisioning help documentation or FAQ**

---

1. **Authentication and Access**
  1. **SAML or OIDC Single Sign On integration** method and metadata exchange
    2. **Type of provisioning:** full **SCIM** or any other **non-SCIM** variation:
      1. SCIM: Role/License control defined in <IDENTITY_PROVIDER> or in the target app?
          2. SCIM: Assignment group(s) only or addition of Push group(s) as well?
          3. Do we need to create a dedicated assignment group(s)? Who will be the owner?
          4. Do we need to create a dedicated push group(s)? Who will be the owner?
          5. What group(s) of users require access on Day 1 without approval?
    3. **Non-SCIM: what user/group attribute(s) needed to be passed?**

---

1. **Access Request Workflow Configuration**
  1. **Access Policy Conditions:**
      1. Requesters Scope: Who can request access?
            - Specific department, team, region, <IDENTITY_PROVIDER> groups?
                  - Do we need to define those groups?
    2. **Access Duration**
      1. **Can access be time-bound?**
