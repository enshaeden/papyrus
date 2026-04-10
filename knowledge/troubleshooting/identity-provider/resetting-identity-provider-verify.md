---
id: kb-troubleshooting-identity-provider-resetting-identity-provider-verify
title: Resetting <MFA_APPLICATION>
canonical_path: knowledge/troubleshooting/identity-provider/resetting-identity-provider-verify.md
summary: "If a user breaks or loses their phone (or cannot otherwise access it), we will need to reset\
  \ their <MFA_APPLICATION> token so they may set it up on a new phone. Before we do we will need to confirm\
  \ it\u2019s necessary we take..."
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Resetting <MFA_APPLICATION>
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
- service-desk
created: '2025-10-22'
updated: '2025-10-22'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
related_services:
- Identity
symptoms:
- "If a user breaks or loses their phone (or cannot otherwise access it), we will need to reset their\
  \ <MFA_APPLICATION> token so they may set it up on a new phone. Before we do we will need to confirm\
  \ it\u2019s necessary we take..."
scope: "Legacy source does not declare structured scope. Summary: If a user breaks or loses their phone\
  \ (or cannot otherwise access it), we will need to reset their <MFA_APPLICATION> token so they may set\
  \ it up on a new phone. Before we do we will need to confirm it\u2019s necessary we take..."
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
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-troubleshooting-identity-provider-index
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
- Identity
related_articles:
- kb-troubleshooting-identity-provider-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

If a user breaks or loses their phone (or cannot otherwise access it), we will need to reset their <MFA_APPLICATION> token so they may set it up on a new phone. Before we do we will need to confirm it’s necessary we take action and the security steps in doing so

# **Instructions (following ticket from user)**

### **Confirm our action is necessary: we only need to take action if a user has lost or broken their phone**

1. If the user states they still have their current phone, all they’ll need is to do is:
  1. Log into <IDENTITY_PROVIDER> > Settings
    2. Remove <MFA_APPLICATION>
    3. Re-enable <MFA_APPLICATION> - this time with their new phone
    4. Walkthrough to send them is here: [<INTERNAL_URL>](<INTERNAL_URL>)

**If the user does NOT have access to their old phone**

1. Head to <IDENTITY_PROVIDER> Admin dashboard ( [<INTERNAL_URL>](<INTERNAL_URL>) )
2. Search for the user
3. Under the username click the **More Actions** drop-down and select **Clear User Sessions**
  1. This will remove the user from any current logins so they are forced to re-type their password into <IDENTITY_PROVIDER>

1. Click the **View Logs** button to the right of the ‘More Actions’ button

1. Search for a log indicating the user has typed their password since requesting the ticket **It’s important we have confirmed they have successfully typed their password**

The log event will be named ‘User login to <IDENTITY_PROVIDER> - success’ then ‘Verify user identity - success’

1. If the log entries are found since requesting the ticket you may proceed to step 9
2. If the log entries are NOT found, please request the user type their username and password into <IDENTITY_PROVIDER> so we can confirm
  1. After they are done, confirm via the logs in Step 6

**Remove the <MFA_APPLICATION> token from the users account:**

1. Click the **More Actions** drop-down again, and this time select **Reset Multifactor**

1. In the new window, select the box next to **<MFA_APPLICATION>** and click **Reset Selected Factors**

1. (<IDENTITY_PROVIDER> verify is now removed will now no longer work on the old phone)
2. Tell the user to attempt to re-sign into [<COMPANY_NAME>.<IDENTITY_PROVIDER>.com](<INTERNAL_URL>) with their new phone nearby. It will automatically walk them through the process of setting up <MFA_APPLICATION> - this time on their new phone.
