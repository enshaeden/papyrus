---
id: kb-troubleshooting-network-fixing-corp-wifi
title: Fixing Corp Wifi
canonical_path: knowledge/troubleshooting/network/fixing-corp-wifi.md
summary: "Users will attempt to connect to Corp Wifi and instead of it auto connecting, it will ask for\
  \ a certificate. It shouldn\u2019t already, but regardless, none will work."
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Fixing Corp Wifi
team: IT Operations
systems: []
tags:
- service-desk
created: '2025-10-27'
updated: '2025-10-27'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services: []
symptoms:
- "Users will attempt to connect to Corp Wifi and instead of it auto connecting, it will ask for a certificate.\
  \ It shouldn\u2019t already, but regardless, none will work."
scope: "Legacy source does not declare structured scope. Summary: Users will attempt to connect to Corp\
  \ Wifi and instead of it auto connecting, it will ask for a certificate. It shouldn\u2019t already,\
  \ but regardless, none will work."
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
- kb-troubleshooting-network-index
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
services: []
related_articles:
- kb-troubleshooting-network-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

Users will attempt to connect to Corp Wifi and instead of it auto-connecting, it will ask for a certificate. It shouldn’t already, but regardless, none will work.

# **Instructions**

### **Quick instructions:**

1. Add the user’s machine to **[Wifi Certificate Disabled]** group in <ENDPOINT_MANAGEMENT_PLATFORM>
2. Have user run a **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** in Self Service
3. Remove the user’s machine from that group
4. Have user run **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** again
5. Attempt to connect to WiFi

### **Full instructions:**

1. Locate user’s machine in <ENDPOINT_MANAGEMENT_PLATFORM> and note the name + serial number
2. In <ENDPOINT_MANAGEMENT_PLATFORM>, on the left column click: **Static Computer Groups**

1. In the list of groups select: **WiFi Certificate Disabled**

1. Click **Edit** in the bottom-right corner
2. Click the **Assignments** tab just below the name of the group at the top
3. Search for the users machine and click the check-box to the left of its name
4. Click **Save** at the bottom right
5. Have user open **Self Service** on their laptop and run **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** tile
6. Wait until you see the machine has updated in <ENDPOINT_MANAGEMENT_PLATFORM>
  1. **General** tab
    2. **Last Inventory Update** within last few minutes
7. Follow steps 1-7 above except UN check at step 6
8. Have user re-run **<ENDPOINT_MANAGEMENT_PLATFORM> Check-in** tile
9. After they do, have them confirm they can now connect to the **office Wi-Fi network** WLAN.
