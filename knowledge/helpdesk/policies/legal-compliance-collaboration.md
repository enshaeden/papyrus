---
id: kb-helpdesk-policies-legal-compliance-collaboration
title: Legal & Compliance Collaboration
canonical_path: knowledge/helpdesk/policies/legal-compliance-collaboration.md
summary: The purpose of this Standard Operating Procedure (SOP) is to define the processes and responsibilities
  for IT collaboration with the Legal and Compliance teams at <COMPANY_NAME>. This document ensures that
  IT plays a...
knowledge_object_type: service_record
legacy_article_type: policy
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Legal & Compliance Collaboration
team: Service Desk
systems:
- <TICKETING_SYSTEM>
tags:
- service-desk
created: '2025-10-28'
updated: '2025-10-31'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: service_desk
service_name: Legal & Compliance Collaboration
service_criticality: not_classified
dependencies:
- <TICKETING_SYSTEM>
support_entrypoints:
- Legacy source does not declare structured support entrypoints.
common_failure_modes:
- Legacy source does not declare structured common failure modes.
related_runbooks: []
related_known_errors: []
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
- kb-helpdesk-policies-index
prerequisites:
- Review the scope, approvals, and dependencies described in this article before starting.
- Confirm you have the required systems access and escalation path before proceeding.
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
superseded_by: null
replaced_by: null
retirement_reason: null
services: []
related_articles:
- kb-helpdesk-policies-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **1.1 Purpose**

The purpose of this Standard Operating Procedure (SOP) is to define the processes and responsibilities for IT collaboration with the Legal and Compliance teams at <COMPANY_NAME>. This document ensures that IT plays a proactive role in supporting legal holds, data retention policies, and audit requirements while maintaining compliance with legal and regulatory obligations.

By following these procedures, IT can:

- Ensure the proper handling and secure storage of devices subject to legal holds.
- Maintain compliance with data retention policies and ensure secure data access, storage, and deletion practices.
- Efficiently support legal and compliance audits by leveraging the <ASSET_MANAGEMENT_SYSTEM> Asset Tracker and other IT documentation tools.

This SOP establishes a clear framework for IT's role in legal and compliance matters, ensuring transparency, accountability, and adherence to <COMPANY_NAME>’s policies and industry regulations.

# **1.2 Scope**

This document applies to the Global IT Helpdesk team located in <OFFICE_SITE_C>, <OFFICE_SITE_A>, <REGION_D>, and <OFFICE_SITE_B>.

# **1.3 Definitions**

- **Legal Hold** : A directive to preserve specific data, including IT assets, for legal or investigative purposes.
- **Data Retention** : Policies that define how long data should be stored and when it should be securely deleted.
- **Audit** : A formal review process to ensure compliance with legal, security, and company policies.
- **<ASSET_MANAGEMENT_SYSTEM> Asset Tracker** : A system used by IT to manage and track company assets, including legal hold statuses.
- **Secure Storage** : Measures taken to protect data and devices from unauthorized access while under legal hold.
- **Compliance** : Adhering to legal, regulatory, and company policies regarding data and asset management.
- **Access Controls** : Security measures ensuring that only authorized personnel can access specific data or systems.

# **2. Handling Legal Holds**

### **2.1 What is a Legal Hold?**

A legal hold is a directive issued by the Legal team to preserve relevant devices, data, or user accounts in anticipation of litigation, investigation, or regulatory inquiry. This ensures that no modifications, deletions, or unauthorized access occur during the hold period.

At <COMPANY_NAME>, legal holds primarily apply to employee devices. When Legal requests a legal hold, IT updates the device’s status in the <ASSET_MANAGEMENT_SYSTEM> asset tracker to **Legal Hold** , preventing reassignment or disposal. In some cases, Legal may also request access to device data or a user’s email, which IT can provide upon request following approval protocols.

### **2.2 IT's Role in Legal Holds**

IT is responsible for ensuring that all requested devices and relevant data are preserved in accordance with legal hold directives. This includes:

- Updating the device status in the <ASSET_MANAGEMENT_SYSTEM> asset tracker to **Legal Hold** to prevent unauthorized use or reassignment.
- Ensuring the device remains secured and is not erased, reconfigured, or recycled.
- Providing Legal with requested access to device data or user emails, following proper approval processes.
- Coordinating with Legal and IT Leadership to ensure compliance with legal requirements.
- **Do I need to do anything in <ENDPOINT_MANAGEMENT_PLATFORM>’s Device management section?** No. No changes needed unless Legal specifically requests it.

### **2.4 Secure Storage and Access Controls**

To maintain compliance and protect the integrity of legal hold data:

- Devices placed under legal hold must be securely stored and labeled accordingly.
- IT must restrict access to legal hold devices, ensuring only authorized personnel from IT and Legal can handle them.
- Requests for data access (device files, emails, or system logs) must be documented and processed only with approval from IT Leadership and Legal.

### **2.5 Release of Legal Holds**

When Legal determines that a legal hold is no longer necessary, IT is responsible for:

- Updating the device status in the <ASSET_MANAGEMENT_SYSTEM> asset tracker to reflect its new disposition (e.g., **In Stock** , **Decommissioned** , or **Recycled** ).
- Restoring normal access and retention policies to affected accounts or data if applicable.
- Documenting the release process to ensure compliance with legal requirements.
- Verifying that any automated deletion or archival processes resume as appropriate.

# **3. Data Retention**

### **3.1 Data Retention Policies**

Data retention at <COMPANY_NAME> is governed by compliance, legal, and business requirements. IT is responsible for ensuring that company data is retained or deleted in accordance with these policies. The retention policies cover:

- Employee emails and communication records
- System and application logs
- Device and hardware data
- Cloud storage and document repositories

Retention periods vary based on data type and regulatory requirements. Legal may mandate extended retention for specific cases or investigations.

### **3.2 IT's Responsibilities in Data Retention**

IT plays a key role in executing data retention policies by:

- Ensuring data storage systems comply with retention requirements.
- Implementing automated retention and deletion processes where applicable.
- Coordinating with Legal to enforce retention policies on employee accounts and company assets.
- Assisting Legal with data access and preservation requests.

### **3.3 Secure Storage and Deletion Procedures**

To maintain compliance and security:

- Data that requires retention must be stored in secure, access-controlled environments.
- When data reaches the end of its retention period, IT ensures secure deletion using industry-standard methods.
- Devices undergoing disposal must have their data erased in compliance with <COMPANY_NAME>’s security policies.
- IT must document all deletion and archival activities for audit purposes.

### **3.4 Handling Data Retention Requests from Legal**

Legal may request specific data retention actions, such as:

- Extending the retention period for an employee’s data due to ongoing investigations.
- Recovering archived emails or system logs.
- Placing a hold on automatic deletion processes.

All such requests must be documented and approved by IT Leadership before action is taken. IT ensures compliance while maintaining data integrity and security.

# **4. Audits**

### **4.1 Types of Audits**

<COMPANY_NAME> may be subject to various audits, including:

- **Internal Audits** – Conducted by <COMPANY_NAME>’s internal teams to ensure compliance with policies and procedures.
- **External Audits** – Conducted by regulatory bodies or third-party auditors to verify compliance with legal and security requirements.
- **Asset Audits** – Focused on IT assets, ensuring accurate tracking, proper assignment, and policy adherence.

### **4.2 IT's Role in Audits**

IT is responsible for providing accurate and timely data during audits. This includes:

- Ensuring all IT assets are properly logged and tracked in the **<ASSET_MANAGEMENT_SYSTEM> Asset Tracker** .
- Collaborating with Legal and Compliance teams to address audit findings.

### **4.3 Documentation and Compliance Requirements**

To maintain audit readiness, IT must:

- Regularly update and verify records in the **<ASSET_MANAGEMENT_SYSTEM> Asset Tracker** .
- Maintain documentation of asset assignments, status changes, and disposal records.
- Ensure that all compliance-related configurations in IT systems (e.g., <ENDPOINT_MANAGEMENT_PLATFORM>, <IDENTITY_PROVIDER>) are properly documented.
- Follow proper procedures for data retention and deletion, ensuring logs and records are retained per legal and regulatory requirements.

### **4.4 Responding to Legal & Compliance Audit Requests**

When an audit request is received, IT should:

1. Identify the scope of the audit and the required information.
2. Utilize the **Fixed Assets** interface in **<ASSET_MANAGEMENT_SYSTEM>** to provide an up-to-date view of IT assets, including device ownership, status, and historical changes.
3. Work with Legal to provide any additional data needed while maintaining security and compliance protocols.
4. Document all provided information and ensure follow-up actions, if any, are completed.

By leveraging the **<ASSET_MANAGEMENT_SYSTEM> Asset Tracker** and maintaining strong documentation practices, IT can efficiently support audit processes and ensure compliance with <COMPANY_NAME>’s legal and regulatory obligations.
