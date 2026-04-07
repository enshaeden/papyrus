---
id: kb-troubleshooting-device-mac-granting-users-administrative-permissions-on-their-mac-laptops
title: Granting users administrative permissions on their Mac laptops
canonical_path: knowledge/troubleshooting/device/mac/granting-users-administrative-permissions-on-their-mac-laptops.md
summary: "When setting up their machines for the first time, some users may find they are not local admins. Here\u2019s how to fix this."
type: troubleshooting
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Granting users administrative permissions on their Mac laptops
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
services:
- Endpoint Provisioning
tags:
- endpoint
- macos
- service-desk
created: '2025-10-27'
updated: '2025-10-27'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
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
- kb-troubleshooting-device-mac-index
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

When setting up their machines for the first time, some users may find they are not local admins. Here’s how to fix this. # **Instructions** ### **Quick instructions:** 1. In <ENDPOINT_MANAGEMENT_PLATFORM>, add users machine to policy: **Grant user local admin membership** scope
2. Have user run **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** tile in Self Service
3. Have user run **Grant admin user** tile in Self Service
4. Have user run **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** again
5. Have user log out/in or reboot then they should be an admin ### **Full instructions:** 1. Locate users machine in <ENDPOINT_MANAGEMENT_PLATFORM> and note the name + serial number: <SERIAL_NUMBER>
3. In the list of policies select: **Grant user local admin membership**
4. Click **Scope** tab near the top underneath the policy name
5. Click **Edit** in the bottom-right
6. Click **Add** at the right
7. With the **Computers** tab select, search in the ‘filter’ box for the serial number: <SERIAL_NUMBER>
8. When the computer is located, click **Add** again but this one is to the far right of the machine
9. Click **Save** at the bottom right
10. Have user open **Self Service** on their laptop and run **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** tile
11. When that has completed, have them close and reopen **Self Service**
12. Have them locate and run the **Grant admin user** tile
13. Have them re-run the **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** tile again from step <QUEUE_NAME>
14. When they have time, have them either log out then back in, or do a full reboot
15. Confirm they have admin permissions
16. Follow steps <QUEUE_NAME> but after clicking ‘Edit’, locate their computer and this time select **Remove** to remove that tile from their laptop
