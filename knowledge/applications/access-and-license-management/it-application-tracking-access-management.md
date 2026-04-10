---
id: kb-applications-access-and-license-management-it-application-tracking-access-management
title: IT Application Tracking & Access Management
canonical_path: knowledge/applications/access-and-license-management/it-application-tracking-access-management.md
summary: The purpose of the SOP is to outline how IT manages software access using the <APPLICATION_CATALOG>.
  Including guidance, procedures and app owners for each app.
knowledge_object_type: runbook
legacy_article_type: access
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: IT Application Tracking & Access Management
team: Identity and Access
systems: []
tags:
- account
- access
created: '2025-10-28'
updated: '2025-10-29'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Access Management
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
- kb-applications-access-and-license-management-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Access Management
related_articles:
- kb-applications-access-and-license-management-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Purpose**

The purpose of the SOP is to outline how IT manages software access using the Master Ticket Route. Including guidance, procedures and app owners for each app.

# **Scope**

This document applies to the Global IT Helpdesk team located in <OFFICE_SITE_C>, <OFFICE_SITE_A>, <REGION_D>, and <OFFICE_SITE_B>.

# **Definitions**

- **Master Ticket Route** – The <ASSET_MANAGEMENT_SYSTEM> table where all ticket routing information is stored, ensuring standardized processes for IT support requests.
- **Edit An IT Ticket** – A dedicated <ASSET_MANAGEMENT_SYSTEM> interface allowing app owners to search, view, and edit specific ticket details while tracking revision history.
- **Record Viewer** – An <ASSET_MANAGEMENT_SYSTEM> feature used in the interface to present relevant ticket fields for easy searching and editing.
- **<QUEUE_NAME> <MESSAGING_PLATFORM> Channel** – The <MESSAGING_PLATFORM> channel where automated alerts notify IT of any changes made to the Master Ticket Route.
- **App Owner** – A designated individual responsible for managing and maintaining software-related ticket processes, ensuring IT is informed of any updates.
- **Significant Change** – A major modification requiring IT intervention, such as creating a new <IDENTITY_PROVIDER> group or workflow, which must be reviewed and approved before updating the ticketing process.

# **Master Ticket Route**

The [**Master Ticket Route**](<INTERNAL_URL>) contains the most up-to-date guidance on all software issued within <COMPANY_NAME>. It is stored in the **IT Asset Tracker** in <ASSET_MANAGEMENT_SYSTEM>.

Each row includes:

- **Software Name** – The name of the application.
- **Request Type** – The type of request (e.g., access, <IDENTITY_PROVIDER> tile, troubleshooting).
- **Process** – Steps to issue or support the software.
- **Team** – The team that manages the request.
- **Manager Approval** – Whether manager approval is required.
- **Owner** – The designated owner of the software.
- **Ticket Link** – A direct URL to the correct ticket type.
- **User Notes** - A simple note to inform users of the process for their request

The **IT team** is responsible for keeping the Master Ticket Route up to date. Whenever a procedure changes, every IT team member must update existing entries or add new software with all relevant details.

Since some software is owned and managed by other teams (e.g., **RevStrat** and **EngEx** ), IT must maintain regular communication with their leadership to ensure the guidance remains accurate and up to date.

# **Adding New Software**

When a new process or software needs to be added to the Ticket Route, we can use the [Add New Ticket](<INTERNAL_URL>) form in <ASSET_MANAGEMENT_SYSTEM>.

The required fields ensure that all vital information is included in the new ticket guidance. This form is available for anyone on the **IT team** to use.

Once a ticket type is created, its fields can be manually updated within the **Ticket Route** view.

**Form Example**

# **IT Procedure for Users Requesting Access To Software**

When a user needs **access** or **troubleshooting** for software, they must first raise a ticket with the relevant team. When in doubt, they can raise a ticket with IT first.

- IT can use the **Master Ticket Route** to quickly locate the software and follow the correct process for issuing access or providing support.
- If the software is **not supported by IT** , the Ticket Route provides a **direct link** for users to request support from the appropriate team.

For software requiring **manager approval** :

- IT must add the user’s **line manager** to the ticket for approval.
- The [**User Lookup interface**](<INTERNAL_URL>) can be used to quickly find the correct line manager.
- Once approval is granted, IT can proceed with issuing access.

# **User View**

The **User View** is a filtered version of the **Master Ticket Route** , displaying only essential information:

- **Software Name**
- **User Notes**
- **Manager Approval Requirement**
- **Clickable Ticket Link** – Opens the correct ticket for the requested software.

For software requiring **direct contact** with an individual, the ticket link opens a **email compose window** pre-filled with the correct email address and subject line.

This **User View** is embedded within the [**IT Knowledgebase Spot**](<INTERNAL_URL>) in <COMPANY_NAME>. A link to this view is also integrated into the **<TICKETING_SYSTEM> ticket process** , allowing users to quickly find the correct ticket link for their software requests.

# **App Owner Ticket Editing**

To ensure that higher-level application owners can update ticket processes while keeping IT informed of any changes, a dedicated interface has been created in <ASSET_MANAGEMENT_SYSTEM>: "Edit An IT Ticket."

### **Interface Overview**

- The interface utilizes a Record Viewer view, allowing app owners to search for ticket records within the Master Ticket Route using a simple search bar.
- When a ticket is selected, only necessary fields are displayed for editing.
- A revision history panel on the right-hand side tracks all changes.

This interface is shared with higher-level app owners, enabling them to update IT on process changes efficiently.

### **Automated Change Alerts**

To maintain transparency, an automation runs whenever any field in the Master Ticket Route is updated.

- This automation sends an alert to the <QUEUE_NAME> <MESSAGING_PLATFORM> channel.
- The alert includes:
  - A clickable link naming the software that was changed.
    - The name of the person who made the change.
    - A reminder for IT to review the changes.

### **Responsibilities & Review Process**

- App Owners must use the Edit An IT Ticket interface to notify IT of any process changes.
- IT Team Members must review all updates following the <MESSAGING_PLATFORM> alert.
- If any change appears incorrect or requires clarification, IT must alert IT Leadership for review.

### **Handling Significant Changes**

If an app owner wishes to make a significant change (e.g., a new <IDENTITY_PROVIDER> group, workflow, or other system-wide impact), they must:

1. First, create a ticket with IT, detailing the required change.
2. IT will review and implement the necessary changes.
3. Once completed, the app owner or IT can update the Master Ticket Route accordingly.

By implementing this process, IT can maintain oversight of ticketing procedures while empowering app owners to keep process documentation up to date.
