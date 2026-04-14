---
id: kb-applications-business-apps-intake-forms-business-application-c-identity-provider-app-onboarding-form
title: <BUSINESS_APPLICATION_C> <IDENTITY_PROVIDER> App Onboarding Form
canonical_path: knowledge/applications/business-apps/intake-forms/business-application-c-identity-provider-app-onboarding-form.md
summary: <BUSINESS_APPLICATION_C> is a sales engagement platform that helps revenue teams automate and
  optimize their customer interactions. It enables users to manage email sequences, calls, and tasks in
  one place
knowledge_object_type: service_record
legacy_article_type: reference
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: <BUSINESS_APPLICATION_C> <IDENTITY_PROVIDER> App Onboarding Form
team: IT Operations
systems:
- <HR_SYSTEM>
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
- onboarding
created: '2025-10-28'
updated: '2025-10-28'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: it_ops
service_name: <BUSINESS_APPLICATION_C> <IDENTITY_PROVIDER> App Onboarding Form
service_criticality: not_classified
dependencies:
- <HR_SYSTEM>
- <IDENTITY_PROVIDER>
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks: []
related_known_errors: []
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
- kb-applications-business-apps-intake-forms-index
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
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
- Onboarding
related_articles:
- kb-applications-business-apps-intake-forms-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

1. **Application Details for <IDENTITY_PROVIDER> Access Requests**
  1. **Application Name** (as it appears in <IDENTITY_PROVIDER>) - *<BUSINESS_APPLICATION_C>*
    2. **Description of the App** (end-user friendly explanation of what it does) -

*<BUSINESS_APPLICATION_C> is a sales engagement platform that helps revenue teams automate and optimize their customer interactions. It enables users to manage email sequences, calls, and tasks in one place*

1. **App Owner Contact** (for approval routing and escalation) - *Katherine Liu/Varghese Benady*
2. **App Category/Type** (e.g., Engineering, Finance, HR) - *Sales*
3. **Link to SSO and provisioning help documentation or FAQ -** [***<IDENTITY_PROVIDER> Automated User Provisioning Guide***](<INTERNAL_URL>)

---

1. **Authentication and Access**
  1. **SAML or OIDC Single Sign On integration** method and metadata exchange *- Please review docmentation*
    2. **Type of provisioning:** full **SCIM** or any other **non-SCIM** variation:
      1. SCIM: Role/License control defined in <IDENTITY_PROVIDER> or in the target app? *- For POC it’ll be by user for now. Please review documentation*
          2. SCIM: Assignment group(s) only or addition of Push group(s) as well? *For POC it’ll be by user for now. Please review docmentation*
          3. Do we need to create a dedicated assignment group(s)? Who will be the owner? *For POC it’ll be by user for now. Please review docmentation* . *Owner is Katherine Liu*
          4. Do we need to create a dedicated push group(s)? Who will be the owner? *For POC it’ll be by user for now. Please review docmentation* . *Owner is Katherine Liu*
          5. What group(s) of users require access on Day 1 without approval? *For POC it’ll be by user for now. Please review docmentation* . *Owner is Katherine Liu*
    3. **Non-SCIM: what user/group attribute(s) needed to be passed?** *- NA*

---

1. **Access Request Workflow Configuration**
  1. **Access Policy Conditions:**
      1. Requesters Scope: Who can request access? *- Sales, TBD*
            - Specific department, team, region, <IDENTITY_PROVIDER> groups? *- Sales, TBD*
                  - Do we need to define those groups? *TBD*
    2. **Access Duration**
      1. **Can access be time-bound?**
            - Temporary (e.g., 30/60/90 days) Consequences of revoked temp access (e.g. created docs revocation/deletion) *Trial is for 3 weeks - get for 2 months for now as there can be delays.*
                  - Permanent until reviewed/revoked - *2 months*
    3. **Approvals**
      1. **Does this app require approval before assignment?** *- NA for POC*
          2. **Approval Sequence:**
            - Manager approval only? *- NA for POC*
                  - App Owner/Security/Other approval required? *- NA for POC*
          3. **Backup Approvers:** in case of out-of-office or inactivity - *- NA for POC*
          4. **Expected SLA for approving new access requests** *- NA for POC*

---

1. **Review and Certification Settings**
  1. **Should this app be part of regular access reviews?** *- NA for POC*
      - Quarterly certification by managers/app owners? *- NA for POC*
    2. **Compliance requirement alignment (e.g., SOX, ISO 27001)?** *See documents - link above*

---
