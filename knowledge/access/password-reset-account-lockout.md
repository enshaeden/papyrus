---
id: kb-access-password-reset-account-lockout
title: Password Reset and Account Lockout Response
canonical_path: knowledge/access/password-reset-account-lockout.md
summary: Restore user access when the account password is unknown or repeated sign-in failures have triggered
  an account lockout.
knowledge_object_type: runbook
legacy_article_type: access
status: active
owner: service_owner
source_type: native
source_system: repository
source_title: Password Reset and Account Lockout Response
team: Identity and Access
systems:
- <COLLABORATION_PLATFORM>
- <IDENTITY_PROVIDER>
- <TICKETING_SYSTEM>
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
related_services:
- Identity
- Access Management
prerequisites:
- Verified requester identity using the approved verification script.
- Open ticket referencing the affected user account.
- Access to the identity provider admin portal or approved reset workflow.
steps:
- Confirm whether the issue is a forgotten password, MFA problem, or lockout caused by repeated failures.
- Verify the user identity using manager confirmation or the approved two-factor service desk verification
  procedure.
- Reset the password or unlock the account in <IDENTITY_PROVIDER> according to the least-privilege workflow.
- Revoke active sessions only if the user reports suspicious activity or the security team requests it.
- Instruct the user to complete sign-in, MFA verification, and application access checks while the ticket
  remains open.
verification:
- User can sign in successfully through the primary identity portal.
- The user can access at least one dependent service such as <COLLABORATION_PLATFORM>.
- The ticket documents the verification method and the exact action taken.
rollback:
- If the reset was performed on the wrong account, immediately expire the issued password and escalate
  to Identity Operations.
- If access remains blocked after the unlock, revert any temporary bypasses and escalate with screenshots
  or error text.
citations:
- article_id: kb-access-software-access-request
  source_title: Software and access request workflow
  source_type: document
  source_ref: knowledge/access/software-access-request.md
  note: Use the request workflow if the issue is missing entitlement rather than authentication failure.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-access-software-access-request
- kb-troubleshooting-vpn-connectivity
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
- Access Management
related_articles:
- kb-access-software-access-request
- kb-troubleshooting-vpn-connectivity
references:
- title: Software and access request workflow
  article_id: kb-access-software-access-request
  path: knowledge/access/software-access-request.md
  note: Use the request workflow if the issue is missing entitlement rather than authentication failure.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Notes

If the user reports unexpected MFA prompts, treat the event as potentially suspicious and engage Security Operations before issuing a long-lived bypass.
