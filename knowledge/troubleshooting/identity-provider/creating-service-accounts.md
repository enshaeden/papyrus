---
id: kb-troubleshooting-identity-provider-creating-service-accounts
title: Creating Service Accounts
canonical_path: knowledge/troubleshooting/identity-provider/creating-service-accounts.md
summary: Create a service account in the identity provider with managed credentials and documented recovery details.
type: troubleshooting
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Creating Service Accounts
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
- <PASSWORD_MANAGER>
services:
- Identity
- Access Management
tags:
- account
- authentication
- service-desk
created: '2025-10-27'
updated: '2026-04-07'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
prerequisites:
- Capture the exact symptom, affected scope, and recent changes before troubleshooting.
- Confirm you have the required system access or escalation path before making changes.
steps:
- Review the imported procedure body below and confirm the documented symptoms match the live issue.
- Work through the diagnostic and remediation steps in order, recording any deviations in the ticket.
- Escalate when the documented checks fail or the issue exceeds the article scope.
verification:
- The reported symptom no longer reproduces after the documented steps are completed.
- The ticket or case record contains the troubleshooting outcome and any follow-up actions.
rollback:
- Undo any reversible change documented in the procedure if validation fails.
- Escalate to the owning team with the captured symptom and actions already taken.
related_articles:
- kb-troubleshooting-identity-provider-index
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

## Overview

Use this procedure to create a service account in `<IDENTITY_PROVIDER>` and store the credential material in `<PASSWORD_MANAGER>`.

## Create The Identity Record

1. Open the add-user flow in `<IDENTITY_PROVIDER>`.
2. Set the account type to a standard service-account profile approved by the identity team.
3. Populate the display name, username, and primary email using the approved service-account naming convention.
4. Leave optional personal fields blank unless a documented integration requires them.
5. Set the password to administrator-managed so the initial secret can be generated and stored safely.

## Store Credentials Securely

1. Create a new login item in `<PASSWORD_MANAGER>` for the service account.
2. Generate a strong password in `<PASSWORD_MANAGER>`.
3. Copy the generated password into the pending `<IDENTITY_PROVIDER>` account record.
4. Save the identity record only after the credential has been captured in the password manager entry.

## Complete First Login And MFA

1. Sign in as the service account in a private browser session.
2. Complete the required first-login prompts.
3. If MFA is required, enroll the approved authenticator method and store any recovery details in the secure notes field of the `<PASSWORD_MANAGER>` item.
4. If security questions are required, store the question-and-answer set in the same secure record.

## Validation

1. Confirm the account can sign in successfully.
2. Confirm the credential item exists in the correct vault or ownership location.
3. Record the requesting system, owner, and recovery location in the ticket or audit trail.
