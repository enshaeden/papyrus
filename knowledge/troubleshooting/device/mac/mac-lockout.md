---
id: kb-troubleshooting-device-mac-mac-lockout
title: Mac Lockout
canonical_path: knowledge/troubleshooting/device/mac/mac-lockout.md
summary: This document defines the standard IT response when a user reports being locked out of their
  Mac or their password no longer works. The guidance applies to full-disk encrypted Macs with device
  sign-in agent including both...
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Mac Lockout
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- macos
- service-desk
created: '2025-10-15'
updated: '2025-10-15'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
symptoms:
- This document defines the standard IT response when a user reports being locked out of their Mac or
  their password no longer works. The guidance applies to full-disk encrypted Macs with device sign-in
  agent including both...
scope: 'Legacy source does not declare structured scope. Summary: This document defines the standard IT
  response when a user reports being locked out of their Mac or their password no longer works. The guidance
  applies to full-disk encrypted Macs with device sign-in agent including both...'
cause: Legacy source does not declare a structured cause field.
diagnostic_checks:
- Review the imported procedure body below and confirm the documented symptoms match the live issue.
- Work through the diagnostic and remediation steps in order, recording any deviations in the ticket.
- Escalate when the documented checks fail or the issue exceeds the article scope.
mitigations:
- Undo any reversible change documented in the procedure if validation fails.
- Escalate to the owning team with the captured symptom and actions already taken.
permanent_fix_status: unknown
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
- kb-troubleshooting-device-mac-index
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
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-troubleshooting-device-mac-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

### **Purpose**

This document defines the standard IT response when a user reports being locked out of their Mac or their password no longer works. The guidance applies to full-disk-encrypted Macs with device sign-in agent including both x86 and ARM-based Mac hardware.

**Reasons for Mac Lockout**

- **Password Desync:** Occurs when the user changes their <IDENTITY_PROVIDER> password while offline, causing their local Mac password (used for full-disk encryption unlock) to fall out of sync. The fix is to unlock with the device recovery key and re-sync via device sign-in agent.
- **User Forgot Password:** Happens when the user simply forgets their <IDENTITY_PROVIDER> and local Mac password. The resolution is to reset the <IDENTITY_PROVIDER> password through the <IDENTITY_PROVIDER> self-service or IT portal, then unlock the Mac using the device recovery key and log in with the new password.

### Finding Recovery Key in <ENDPOINT_MANAGEMENT_PLATFORM>

1. Confirm user name and Mac serial number (from ticket and <ASSET_MANAGEMENT_SYSTEM> inventory).
2. In <ENDPOINT_MANAGEMENT_PLATFORM>: **Computers → Search → [Device] → Inventory → Disk Encryption**
3. Make sure Disk Encryption status is 'Encrypted'
4. Click “View Recovery Key” and copy the 24-character recovery key (e.g. `XXXX-XXXX-XXXX-XXXX-XXXX-XXXX` ).
5. Share the key securely to the user like <MESSAGING_PLATFORM> DM with expiry.

### User Unlock Instructions

#### For Intel Macs

- At the full-disk encryption unlock screen, click the ? next to the password field.
- Choose “ **Enter Recovery Key** ” and enter the key (with dashes).
- Then select your profile and click on ' **forget all passwords** '
- Click on reset password and set the same password as your <IDENTITY_PROVIDER>.
- Then restart the mac and login with your new password.

#### For ARM-based Mac devices

- Power off the Mac completely.
- Press and hold the **power button** until “Loading startup options” appears.
- Select **Options → Continue** to enter **macOS Recovery** .
- Choose **“Forgot all passwords?” → “Enter Recovery Key.”**
- Enter the device recovery key.
- Click on reset password and set the same password as your <IDENTITY_PROVIDER>.
- Then restart the mac and login with your new password.

### Re-Sync Local Password with <IDENTITY_PROVIDER> using device sign-in agent

Once logged in to mac

1. Connect to Wi-Fi
2. Open **device sign-in agent app** and login with your <IDENTITY_PROVIDER> credentials.
3. As currently your <IDENTITY_PROVIDER> and mac password are same, it will directly login you which means your passwords are in sync.
4. If your passwords are different, it will ask you to enter your mac login password and then it will sync your mac password with your <IDENTITY_PROVIDER> password.
