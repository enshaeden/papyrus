---
id: kb-troubleshooting-network-onsite-network-outage-troubleshooting-sop
title: "Onsite Network Outage \u2013 Troubleshooting SOP"
canonical_path: knowledge/troubleshooting/network/onsite-network-outage-troubleshooting-sop.md
summary: To define the step by step troubleshooting and escalation process for IT support technicians
  during an onsite network outage, ensuring efficient troubleshooting, communication, and resolution from
  end user symptoms...
knowledge_object_type: known_error
legacy_article_type: troubleshooting
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: "Onsite Network Outage \u2013 Troubleshooting SOP"
team: IT Operations
systems: []
tags:
- service-desk
created: '2025-08-29'
updated: '2025-09-04'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services:
- Incident Management
symptoms:
- To define the step by step troubleshooting and escalation process for IT support technicians during
  an onsite network outage, ensuring efficient troubleshooting, communication, and resolution from end
  user symptoms...
scope: 'Legacy source does not declare structured scope. Summary: To define the step by step troubleshooting
  and escalation process for IT support technicians during an onsite network outage, ensuring efficient
  troubleshooting, communication, and resolution from end user symptoms...'
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
services:
- Incident Management
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

## **Purpose**

To define the step-by-step troubleshooting and escalation process for IT support technicians during an onsite network outage, ensuring efficient troubleshooting, communication, and resolution from end-user symptoms to core infrastructure problems.

## **Scope**

This SOP is intended for all IT support technicians addressing **onsite network outages** at any <COMPANY_NAME> physical office location. System architecture and configuration details are documented separately here (Need to add a hyperlink).

## **Prerequisites**

- A Laptop with admin rights
- Secure access to:
  - Network Device credentials (Not applicable for <REGION_A> taken care by ISP)
    - Network Vendor contact sheet (Applicable for <REGION_A>)
- The Architecture & Configuration document (Need to add a hyperlink)Mobile hotspot (for communication during outages)
- Access to network/server rooms

## **Roles and Responsibilities**

**IT Support Technician** : Lead on investigation/troubleshooting, isolate issue, document findings and resolution steps, and report it to the Higher management.

**IT Manager/Director** : Oversight, decision on escalations, co-ordination with vendors ( Region specific).

**ISP / Vendors** : Assist with issues outside <COMPANY_NAME> infrastructure.

# **Procedures**

## **Troubleshooting Workflow: Low-to-High Severity**

### **A. Initial Triage**

- **Acknowledge** alert from user report, ticket, or monitoring tool(not applicable for <REGION_A>).
- **Determine the scope** :
  - Entire site, floor, or individual endpoint?
    - Wired, wireless, or both?
    - Internet-only or internal resources too?
- If the scope affects 3 or more users of a common element (all the same office, interface, etc) post communications as per the [comms guidance](<INTERNAL_URL>) to notify the entire facility **immediately** .
- Notify the **Senior Associate/IT Manager/Vendor** for initiating an investigation.
- Create a master troubleshooting ticket in the <QUEUE_NAME> queue and link it to all related tickets and user reports.
- Create a <MESSAGING_PLATFORM> channel with the following convention: **<QUEUE_NAME>####<QUEUE_NAME><LOCATION_NAME>-<OUTAGE_TYPE>** (i.e <QUEUE_NAME>-<LOCATION_NAME>-<OUTAGE_TYPE>) and connect it to the <QUEUE_NAME> ticket.

**Note** :- ***Ensure to Invite all stakeholders and engineers to the channel and move any threaded conversations here.***

### **B. End-User Level Checks (Low Severity)**

- Can the user access other sites or services or is it a complete loss?
- Is the issue specific to a laptop/device or multiple users?
- Basic steps:
  - Reboot laptop/device and reconnect to network
    - Check if the user is on WiFi or LAN
    - Check for physical LAN cable damage if there any (not applicable for <REGION_A> as they only have wireless connectivity)
    - Check connectivity on an alternate wireless network like mobile hotspot,etc.

**Note:-** ***If limited to a single user or area, document locally and continue with device-level support.***

### **C. Network Edge Checks (Medium Severity)**

- **Hardware Inspection** :
  - Confirm power to modem, routers, switches, and APs
    - Check UPS for outages or errors (Not applicable for <REGION_A>)
    - Look for any disconnected/damaged cables in the Server Room as well as APs location .
- **Device Indicators** :
  - Inspect LEDs on switches, routers, APs, etc
    - Reboot unresponsive hardware (make sure to record time/date)
- **Connectivity Testing(Not applicable for <REGION_A>-Manged by Vendor)** :
  - Plug directly into switch/router
    - Run ***ping, traceroute*** , and ***DNS lookup***
    - Check local gateway and DHCP leases
- **Local Logs/Tools(Not applicable for <REGION_A>-Manged by Vendor)** :
  - Review switch/firewall/AP controller logs
    - Access locally if cloud tools are down

**Note:-** ***If failure is hardware or internal routing-related, escalate the issue per section below.***

### **D. Enterprise Infrastructure (High Severity)(Not applicable for <REGION_A>-Manged by Vendor)**

- Confirm WAN connectivity – does the firewall/router show a live WAN link?
- Check for:
  - Internal DNS failures
    - Firewall routing issues
    - Upstream switch outage

**Note:-** ***If the issue is confirmed beyond LAN scope or internal services, move to the escalation matrix per section below.***

## **Escalation Matrix**

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| **Name** | **Designation** | **Scope/Level** | **Contact** |
| <ROLE_NAME> | Regional support leads | Level 1 | <EMAIL_ADDRESS> |
| <ROLE_NAME> | Regional IT manager and network engineering lead | Level 2 | <EMAIL_ADDRESS> |
| External provider | regional network provider | Anything outside of <COMPANY_NAME> scope | <EMAIL_ADDRESS> [Support matrix](<INTERNAL_URL>) |
| <ROLE_NAME> | IT leadership | Level 3 | <EMAIL_ADDRESS> |

## **Troubleshooting Workflow Table**

| Column 1 | Column 2 | Column 3 | Column 4 |
| --- | --- | --- | --- |
| **Severity** | **Focus** | **Key Checks** | **Actions** |
| **Initial Triage** | Scope & comms | Source of alert? Scope = site, floor, or user? Wired/wireless? Internet vs internal? | If ≥3 users, send comms. Notify IT Manager/Vendor. Create master <QUEUE_NAME> ticket + <MESSAGING_PLATFORM> channel (<QUEUE_NAME>####<QUEUE_NAME>) |
| **Low (End-User)** | Individual devices | Other sites/services accessible? Single device vs many? WiFi or LAN? Hotspot test? | Reboot device, reconnect, check WiFi/cables (LAN not for <REGION_A>). If isolated, document & continue device-level support. |
| **Medium (Network Edge)** | Local network gear | Power to modem/router/APs? LED status? Cables connected? | Reboot hardware if needed (log time). Vendor manages <REGION_A> edge testing. Escalate if hardware/routing fault. |
| **High (Enterprise Infra)** | WAN / core services | WAN link live? DNS/firewall/routing? Upstream switch? | If confirmed beyond LAN, escalate per matrix. (Vendor-managed for <REGION_A>). |

# **Communication Protocol**

*****Once the outage priority has been determined, the IT Support Technician should (for Mid and High Tier Outages) promptly inform IT leadership and relevant stakeholders by posting an update in the designated <MESSAGING_PLATFORM> channels to ensure timely awareness and coordination.*****

**For <REGION_A> :** [**<QUEUE_NAME>**](<INTERNAL_URL>)

**For <REGION_C> :** [**<QUEUE_NAME>**](<INTERNAL_URL>)

**For CA :** [**<QUEUE_NAME>**](<INTERNAL_URL>)

**For <REGION_D> & ANZ : <QUEUE_NAME>**

# **Escalation Guidelines**

**Escalate to IT Manager and Vendor if** **:**

- Confirmed hardware failure (dead switch, AP, etc.)
- ISP issues are suspected (no WAN IP, modem offline)
- The outage lasts over 30 minutes(TBD) with no root cause found

**Ensure to Log the following:**

- Time and type of escalation
- Person/contact escalated to (IT Manager, Vendor)
- Troubleshooting steps completed so far along with issue summary

# **Resolution & Verification**

**Once the issue is resolved:**

- Test wired and wireless access from multiple spots or APs
- **Verify** :
  - Internet access
    - Intranet, VoIP, printer, and shared drive access
- **Update** :
  - End users/stakeholders
    - <TICKETING_SYSTEM> ticketing system
    - IT Leadership for the Mid & High Tier issues

# **Post-Outage Tasks**

- Submit incident report and RCA draft
- Update the **Troubleshooting SOP** and **Architecture doc** if changes occurred
- Close support ticket with:
  - Root cause analysis (RCA)
    - Steps taken to mitigate the issue
    - Downtime duration
- Raise follow-up tasks if long-term fixes are needed

# **Reference and Supporting Docs**

**Note** :- *There is a need to collaborate with **all other local IT Support Technician/Network engineer** to complete the separate **System Architecture & Configuration document** which should include the following* :

**Building architecture and configuration details as in**

- Network diagrams (Floor layouts)
- Hardware configuration standards
- Cabling and patch panel layouts for Switches, Routers and AP's
- Any other Chats/Layouts/Diagrams that might be helpful
