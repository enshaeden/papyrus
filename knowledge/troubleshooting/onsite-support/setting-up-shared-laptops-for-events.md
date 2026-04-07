---
id: kb-troubleshooting-onsite-support-setting-up-shared-laptops-for-events
title: Setting Up Shared Laptops for Events
canonical_path: knowledge/troubleshooting/onsite-support/setting-up-shared-laptops-for-events.md
summary: 'You can create a single group in <ENDPOINT_MANAGEMENT_PLATFORM> then add that group to these policies, or do the machines as one offs:'
type: troubleshooting
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Setting Up Shared Laptops for Events
team: Service Desk
systems:
- <ASSET_MANAGEMENT_SYSTEM>
services:
- Endpoint Provisioning
tags:
- endpoint
- service-desk
created: '2025-10-29'
updated: '2025-10-29'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: service_desk
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
- kb-troubleshooting-onsite-support-index
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

# **Instructions**

### **Setting up the laptop**

1. Setup laptop with your user account. Fully upgrade to latest OS (or just use device preparation utility to prime laptop on latest OS)
2. Create a new local user in System Settings:
  1. username: **<USERNAME>**
    2. password: **<PASSWORD>**
    3. add that user to full-disk encryption login so it appears at boot/login window
      1. `In terminal: sudo fdesetup add -usertoadd <USERNAME>`
          2. `<USERNAME>`
          3. `<PASSWORD>`
          4. **<PASSWORD>**
3. In new user profile:
  1. delete apps via Applications folder:
    2. <MESSAGING_PLATFORM>
    3. <PASSWORD_MANAGER>
    4. <COLLABORATION_PLATFORM> Drive
    5. Sheets
    6. Docs
    7. Slides
4. Remove everything from the dock EXCEPT:
  1. Finder
    2. app launcher
    3. Calendar
    4. System Settings
    5. browser
      1. (Open app, on dock: Right click icon > Keep in dock)
    6. Downloads
    7. Trash
5. Test login all the way from complete shutdown to logged in and using a browser

### **Add to policies (Scope > Exclude) in <ENDPOINT_MANAGEMENT_PLATFORM>:**

You can create a single group in <ENDPOINT_MANAGEMENT_PLATFORM> then add that group to these policies, or do the machines as one-offs:

Scope > EXCLUDE

1. Policies:
  1. *device sign-in agent (X.X.X) Force install*
    2. *device sign-in agent (X.X.X) Auto install (Phase 4 ALL COMPANY)*
2. Configuration Profiles:
  1. *<COMPANY_NAME> Default: Full-Disk Encryption/Firewall/Login Window*

Scope > INCLUDE

1. Policies:
  1. *device sign-in agent UNinstall*
    2. *device sign-in agent: Disable login screen*
2. Configuration Profiles:
  1. *<COMPANY_NAME> Default: Full-Disk Encryption/Firewall (Standard Login Window)*
