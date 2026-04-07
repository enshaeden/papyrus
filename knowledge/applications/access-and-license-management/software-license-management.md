---
id: kb-applications-access-and-license-management-software-license-management
title: Software License Management
canonical_path: knowledge/applications/access-and-license-management/software-license-management.md
summary: "Design and implement a standardized, end to end software license management process within <COMPANY_NAME>\u2019s IT department\u2014covering procurement, deployment, inventory tracking, renewal coordination, de provisioning, and..."
type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Software License Management
team: Identity and Access
systems: []
services:
- Access Management
tags:
- account
- access
created: '2025-08-29'
updated: '2025-09-10'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
prerequisites:
- Verify the request, identity details, and required approvals before changing access or account state.
- Confirm the target system and business context match the scope of this article.
steps:
- Review the imported procedure body below and confirm the documented scope matches the task at hand.
- Execute the documented steps in order and record the outcome in the relevant ticket or audit trail.
- Stop and escalate if approvals, prerequisites, or expected checkpoints do not match the live request.
verification:
- The expected outcome described in the procedure is confirmed in the target system or ticket record.
- Completion notes, exceptions, and evidence are recorded in the relevant audit or support workflow.
rollback:
- Revert any reversible change described in the procedure if verification fails.
- Pause the workflow and escalate when the documented rollback path is unclear or incomplete.
related_articles:
- kb-applications-access-and-license-management-index
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

# **Objective**

Design and implement a standardized, end-to-end software license management process within <COMPANY_NAME>’s IT department—covering procurement, deployment, inventory tracking, renewal coordination, de-provisioning, and compliance—to ensure regulatory and vendor alignment, minimize legal and financial risk, and optimize software costs.

# **Procedures**

## **Software Acquisition**

- **Request Process:** All software requests must be submitted via <TICKETING_SYSTEM> and include:
  - Requester/Department
    - Software name
    - Justification
    - Number of licenses needed
    - For multiple users, include a list with <COMPANY_NAME> email addresses.
- **Approval Process:** If the software requires approval (as per [**Master Ticket Route**](<INTERNAL_URL>) ), it must go through *manager/owner approval* with proper justification.
  - *Director-level and above* licenses can be provisioned directly if justification is provided.
- **Procurement:** *IT or the app owner* will purchase licenses as needed.
  - All purchase records must be retained and secured.
- **License Key/Activation Code Management:** *IT or application owners* will manage licenses via the <IDENTITY_PROVIDER> dashboard, app admin portal, and/or [**<ASSET_MANAGEMENT_SYSTEM>**](<INTERNAL_URL>) . ***Access must be restricted to authorized personnel only.***
- **Software Installation:** Once a license is assigned (for locally installed software like <PRODUCTIVITY_PLATFORM> Office), users must install it via *Self Service/Software Center* , or contact IT for support.
  - Web-based apps can be accessed directly via browser.
    - Some exceptions of the software installation that are allowed which can be done via official websites(e.g., Snagit) and more are yet to be listed.

## **License Tracking**

- **Centralized Inventory:** Maintain a *centralized inventory* of software licenses that are manually managed by IT. For now, for the licenses that we are managing manually we are using the [**License Manager Table**](<INTERNAL_URL>) in <ASSET_MANAGEMENT_SYSTEM> for the specific softwares.

Note : The [**License Manager Table**](<INTERNAL_URL>) in <ASSET_MANAGEMENT_SYSTEM> will track only software licenses that are not auto-provisioned and require manual management by IT.

The table helps IT maintain visibility into license allocation, reclaim unused licenses, and ensure accurate record-keeping for manually managed licenses.

- **Fields & Functionality :**

**License ID** – Unique name or identifier for the license.

**Status** – Dropdown with values: *Available, Assigned, Expired, Awaiting Reclaim Response* .

**Software** – Name of the software linked to the license.

**Assignee** – Linked to the *Employees & Offboarding* table; shows who the license is assigned to.

**Employee Status** – Lookup indicating if the user is *Active* or *Deprovisioned* .

**Termination Date** – Lookup showing the user’s *termination date* , if applicable.

**Arranged Reclaim Date** – Date when a temporarily assigned license is scheduled to be reclaimed.

**Ask To Reclaim button** – Opens a pre-filled email draft asking the employee to confirm if they still need the license.

- **Interface Usage :**

The [**License Manager Interface**](<INTERNAL_URL>) in <ASSET_MANAGEMENT_SYSTEM> provides a clear view of all license records, with key fields like *License ID and Software* locked to prevent any accidental edits. IT team members can:

- View license status and assignments
- Update assignees
- Click the *Ask To Reclaim* button
- Log reclaim details and dates

This interface streamlines daily license management while safeguarding critical data.

- **License Management Tool:** The IT team will use [**<ASSET_MANAGEMENT_SYSTEM>**](<INTERNAL_URL>) to manage most of the licenses owned or managed by IT.

**Note** : Licenses for applications not managed by IT must be maintained by the respective application owners as described in the [Ticket routing sheet](<INTERNAL_URL>) .

- **Regular Audits:** IT and application owners are responsible for conducting regular software usage audits (monthly, quarterly, or annually—TBD) to ensure compliance with company policies.
- **Usage Monitoring:** IT and application owners must conduct regular audits to assess software usage and effectiveness. If no usage is detected for 30/60/90 days (TBD), licenses may be revoked with or without prior notice, based on the user's account status (active/inactive).

***We have an automation in place which will help to achieve this, further details of the automation are as follows :***

- **Automation: License Available**

When an **employee’s account status changes to** *Deprovisioned* , the License Available automation sends a <MESSAGING_PLATFORM> message to [<QUEUE_NAME>](<INTERNAL_URL>) with the following format :

***LICENSE AVAILABLE* <APPLICATION_CATALOG> record reference that is assigned to <PERSON_NAME> is now available due to termination.**

Attached below the screenshot of a sample alert that we get in <MESSAGING_PLATFORM>

***This allows the team to quickly reclaim and reassign valuable licenses without manual monitoring.***

## **Compliance Management**

- **Compliance Checks:** Regularly compare software usage with license inventory to identify cases of [**under-licensing**](<INTERNAL_URL>) or [**over-licensing**](<INTERNAL_URL>) .
- **Compliance Reporting:** Generate reports on software license usage compliance.
- **Remediation:** IT or Application owners must maintain a minimum license inventory for all software and ensure unauthorized software is not used by enforcing policies through compliance tools like **endpoint compliance tooling** or **device monitoring tooling** .
- **Software Updates/Patches:** It is the shared responsibility of the IT team and employees to ensure all software is kept up to date per company compliance.
  - IT & application owners are responsible for regular patching to maintain security and compliance.

## **Renewal Management**

- **Renewal Notifications:** IT and application owners are responsible for tracking license renewal dates using internal notifications or vendor email reminders.
- **Renewal Review:** IT and application owners must review the renewal process by assessing usage, evaluating the need for continued use, and negotiating pricing for upcoming license or agreement renewals.
- **Renewal Approval:** IT and application owners must obtain appropriate leadership approvals before renewing any licenses or agreements.
- **Renewal Execution:** IT and application owners must follow the organization’s defined processes and procedures for all license or agreement renewals.

## **Decommissioning Software**

- **Software Removal:** IT and application owners are responsible for evaluating software usage and deciding whether to renew the agreement or decommission unused software.
- **License Reclamation:** IT and application owners must conduct regular audits. If a license is unused for 30/60/90 days (TBD as of June 2025), it will be automatically revoked and reassigned to the next requester.
- **Automation: License Available**

When an **employee’s account status changes to** Deprovisioned, the License Available automation sends a <MESSAGING_PLATFORM> message to <QUEUE_NAME> with the following format :

***LICENSE AVAILABLE* <APPLICATION_CATALOG> record reference that is assigned to <PERSON_NAME> is now available due to termination.**

***This allows the team to quickly reclaim and reassign valuable licenses without manual monitoring*** .

- **Process for Reclaiming Licenses**

**Manual Review:** Periodically review the License Manager table for users who are no longer active or suspected of not using their assigned license.

**Use Ask To Reclaim Button :** Click the Ask To Reclaim button to open a pre-written email draft. This message prompts the user to confirm whether they still need the license within 7 days.

**Track Status:** If you’re awaiting a response, update the **Status** to **Awaiting Reclaim Response** to avoid duplicate <BUSINESS_APPLICATION_C> or confusion.

**Follow Up:** If the user confirms they no longer need the license — or doesn’t respond in 7 days — update the record:

- Clear the **Assignee**
- Change the **Status** to **Available**
- Add any relevant **notes**
- **Inventory Update:** IT and application owners must keep the software license inventory updated to reflect current available, assigned, and decommissioned licenses.

## **Roles and Responsibilities:**

- **License Manager:** IT and application owners are responsible for managing license inventory, conducting audits, and handling renewals.
- **IT Support:** Providing user support for installation, patch management, and software troubleshooting.
- **Procurement:** IT and application owners are responsible for purchasing software licenses and renewing existing agreements.
- **Department Heads:** Managers and directors are responsible for approving software requests where applicable and ensuring compliance within their departments.

1. **Exceptions:** Any exceptions to this *SOP* must be documented and approved by the IT team or application owner, with business justification and leadership approval.
2. **Review and Continuous improvements:** This *SOP* will be reviewed and updated periodically to reflect changes in software licensing practices or organizational requirements.

### **List of software licenses managed by IT**

This includes *high-value* or *limited-license software* , as defined in the associated <ASSET_MANAGEMENT_SYSTEM> tracking list [**Software License Manager**](<INTERNAL_URL>) **.**
