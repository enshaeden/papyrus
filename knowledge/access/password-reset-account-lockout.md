---
id: kb-access-password-reset-account-lockout
title: Password Reset and Account Lockout Response
canonical_path: knowledge/access/password-reset-account-lockout.md
summary: Restore user access when the account password is unknown or repeated sign-in failures have triggered an account lockout.
type: access
status: active
owner: Identity Operations
source_type: native
team: Identity and Access
systems:
  - Okta
  - Google Workspace
  - Microsoft 365
  - Ticketing Queue
services:
  - Identity
  - Access Management
tags:
  - account
  - authentication
  - access
  - service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: service_desk
prerequisites:
  - Verified requester identity using the approved verification script.
  - Open ticket referencing the affected user account.
  - Access to the identity provider admin console or approved reset workflow.
steps:
  - Confirm whether the issue is a forgotten password, MFA problem, or lockout caused by repeated failures.
  - Verify the user identity using manager confirmation or the approved two-factor service desk verification procedure.
  - Reset the password or unlock the account in Okta according to the least-privilege workflow.
  - Revoke active sessions only if the user reports suspicious activity or the security team requests it.
  - Instruct the user to complete sign-in, MFA verification, and application access checks while the ticket remains open.
verification:
  - User can sign in successfully through the primary identity portal.
  - The user can access at least one dependent service such as Google Workspace or Microsoft 365.
  - The ticket documents the verification method and the exact action taken.
rollback:
  - If the reset was performed on the wrong account, immediately expire the issued password and escalate to Identity Operations.
  - If access remains blocked after the unlock, revert any temporary bypasses and escalate with screenshots or error text.
related_articles:
  - kb-access-software-access-request
  - kb-troubleshooting-vpn-connectivity
replaced_by: null
retirement_reason: null
references:
  - title: Software and access request workflow
    article_id: kb-access-software-access-request
    path: knowledge/access/software-access-request.md
    note: Use the request workflow if the issue is missing entitlement rather than authentication failure.
change_log:
  - date: 2026-04-07
    summary: Initial seed article.
    author: Repository bootstrap
---

## Notes

If the user reports unexpected MFA prompts, treat the event as potentially suspicious and engage Security Operations before issuing a long-lived bypass.
