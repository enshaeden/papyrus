---
id: kb-troubleshooting-vpn-connectivity
title: VPN Troubleshooting
canonical_path: knowledge/troubleshooting/vpn-connectivity.md
summary: Diagnose common remote access failures affecting the managed VPN client and identity-based sign-in
  flow.
knowledge_object_type: known_error
legacy_article_type: troubleshooting
status: active
owner: service_owner
source_type: native
source_system: repository
source_title: VPN Troubleshooting
team: IT Operations
systems:
- <IDENTITY_PROVIDER>
- <TICKETING_SYSTEM>
- <VPN_SERVICE>
tags:
- vpn
- authentication
- service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: service_desk
related_services:
- Remote Access
- Identity
symptoms:
- Diagnose common remote access failures affecting the managed VPN client and identity-based sign-in flow.
scope: 'Legacy source does not declare structured scope. Summary: Diagnose common remote access failures
  affecting the managed VPN client and identity-based sign-in flow.'
cause: Legacy source does not declare a structured cause field.
diagnostic_checks:
- Determine whether the failure occurs before authentication, during MFA, or after the tunnel attempts
  to connect.
- Confirm the local network is reachable by asking the user to open a public website without the VPN.
- Review the identity provider status and recent lockout events before changing the VPN profile.
- Have the user restart the VPN client and remove stale cached credentials only if the profile is managed
  and can be re-pushed safely.
- Compare the client timestamp and device clock with the VPN gateway requirement because clock drift commonly
  breaks certificate and SSO flows.
- Escalate to Network Operations if the gateway is healthy and multiple users report the same error.
mitigations:
- Restore the managed VPN profile if local troubleshooting replaced or removed it.
- Re-enable any temporarily disabled MFA or conditional access control that was changed for testing.
permanent_fix_status: unknown
citations:
- article_id: kb-access-password-reset-account-lockout
  source_title: Password reset and account lockout response
  source_type: document
  source_ref: knowledge/access/password-reset-account-lockout.md
  note: Use this article when the root cause is an identity failure rather than a network failure.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-access-password-reset-account-lockout
prerequisites:
- Active ticket with user location, device type, and exact error text.
- Confirmed internet connectivity outside the VPN tunnel.
- Managed VPN client installed on the device.
steps:
- Determine whether the failure occurs before authentication, during MFA, or after the tunnel attempts
  to connect.
- Confirm the local network is reachable by asking the user to open a public website without the VPN.
- Review the identity provider status and recent lockout events before changing the VPN profile.
- Have the user restart the VPN client and remove stale cached credentials only if the profile is managed
  and can be re-pushed safely.
- Compare the client timestamp and device clock with the VPN gateway requirement because clock drift commonly
  breaks certificate and SSO flows.
- Escalate to Network Operations if the gateway is healthy and multiple users report the same error.
verification:
- User can complete authentication and establish the tunnel.
- The user can reach an internal resource that requires VPN access.
- Ticket notes identify the failing stage and the corrective action taken.
rollback:
- Restore the managed VPN profile if local troubleshooting replaced or removed it.
- Re-enable any temporarily disabled MFA or conditional access control that was changed for testing.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Remote Access
- Identity
related_articles:
- kb-access-password-reset-account-lockout
references:
- title: Password reset and account lockout response
  article_id: kb-access-password-reset-account-lockout
  path: knowledge/access/password-reset-account-lockout.md
  note: Use this article when the root cause is an identity failure rather than a network failure.
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Escalation Threshold

Escalate immediately if more than one user reports the same gateway or certificate error within the same hour. That pattern usually indicates a service issue rather than an endpoint issue.
