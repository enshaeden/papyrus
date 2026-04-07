---
id: kb-helpdesk-policies-it-incident-escalation-response-security-and-legal-collaboration
title: IT Incident Escalation, Response & Security and Legal Collaboration
canonical_path: knowledge/helpdesk/policies/it-incident-escalation-response-security-and-legal-collaboration.md
summary: "The purpose of this SOP is to establish a clear framework for how <COMPANY_NAME>\u2019s IT and Security teams collaborate to respond to security incidents, implement security related changes, and manage legal escalations. This..."
type: policy
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: IT Incident Escalation, Response & Security and Legal Collaboration
team: Service Desk
systems:
- <TICKETING_SYSTEM>
services:
- Incident Management
tags:
- incident
- service-desk
created: '2025-10-28'
updated: '2026-02-18'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: service_desk
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
related_articles:
- kb-helpdesk-policies-index
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

# **Purpose**

The purpose of this SOP is to establish a clear framework for how <COMPANY_NAME>’s IT and Security teams collaborate to respond to security incidents, implement security-related changes, and manage legal escalations. This document ensures:

- Efficient Communication between IT, Security, and Legal teams through desig
- nated <MESSAGING_PLATFORM> channels and <TICKETING_SYSTEM> ticketing.
- Rapid Incident Response to mitigate security threats, data breaches, or device-related risks.
- Clear Change Management Processes for security-related IT system modifications.
- Legal Compliance & Escalation Procedures for handling legal requests that involve IT systems or employee data.
- Prioritization & Leadership Oversight to ensure security and legal matters take precedence over other IT tasks.

# **Scope**

This document applies to the Global IT Helpdesk team located in <OFFICE_SITE_C>, <OFFICE_SITE_A>, <REGION_D>, and <OFFICE_SITE_B>. Along with the Security and Legal team.

# **1. Definitions**

- **Incident** – Any unplanned event or security issue disrupting IT operations or posing a risk to data/systems.
- **Escalation** – Raising an issue to higher levels of authority for immediate attention.
- **Remediation** – Corrective actions to resolve a security or legal incident.
- **Security Incident** – An event that compromises or potentially compromises company data, systems, or user security (e.g., phishing, data breaches).
- **Phishing Simulation** – A controlled test by Security to assess employee response to fraudulent emails.
- **<ENDPOINT_MANAGEMENT_PLATFORM>** – A mobile device management tool for managing and securing approved company devices.
- **Security Enforcement Change** – Modifications to IT security settings or policies to enhance protection (e.g., stronger passwords, monitoring).

# **2. Communication & Collaboration Channels**

Effective communication is critical to ensuring smooth collaboration between IT, Security, and Legal teams when responding to security incidents and handling security-related IT requests. This section outlines the primary communication channels and how they should be used.

### **2.1 Security & IT Collaboration <MESSAGING_PLATFORM> Channel (security-it-collab)**

The **<QUEUE_NAME>** <MESSAGING_PLATFORM> channel serves as the primary forum for day-to-day collaboration between the IT and Security teams. This channel should be used for:

- General security-related discussions and questions.
- Awareness of ongoing security initiatives, such as phishing simulations.
- Low-priority security-related IT requests before a <TICKETING_SYSTEM> ticket is created.
- Sharing security best practices and updates.

### **2.2 Security Incident <MESSAGING_PLATFORM> Channels**

When a **security incident occurs** , the Security team will create a **private, dedicated <MESSAGING_PLATFORM> channel** for incident response. Members from both the Security and IT teams will be added as necessary. This channel should be used for:

- Real-time coordination between IT and Security during an active incident.
- Tracking incident updates and actions taken.
- Assigning responsibilities, such as IT locking a stolen laptop via <ENDPOINT_MANAGEMENT_PLATFORM>.
- Keeping all discussions contained in one place for documentation and review.

Once the incident is resolved, the channel may be archived, and a post-incident review can be conducted.

### **2.3 <TICKETING_SYSTEM> Ticketing System**

<TICKETING_SYSTEM> is the official system for tracking security-related IT requests and changes.

- **Security Requesting IT Changes** → The Security team must create a <TICKETING_SYSTEM> ticket in the **IT <TICKETING_SYSTEM> queue** for any system changes, such as:
  - Adjustments to <ENDPOINT_MANAGEMENT_PLATFORM> policies or enforcement.
    - Access control changes.
    - Security-related IT configurations.
- **IT Requesting Security Policy Changes** → If IT identifies a security concern that requires a change in Security policy, a <TICKETING_SYSTEM> ticket must be created in the **Security <TICKETING_SYSTEM> queue** .

All requests should follow the **defined prioritization and approval process** , with critical issues escalated as needed.

### **2.4 Legal Escalations**

For any IT-related legal concerns, the primary point of contact is <EMAIL_ADDRESS> .

- If IT has a legal concern, IT **Leadership must be consulted and looped in** before contacting Legal.
- If Legal requires IT support (e.g., data access on an employee’s laptop), they must submit a <TICKETING_SYSTEM> ticket in the **IT <TICKETING_SYSTEM> queue** .
- Any legal-related IT requests must be escalated to IT Leadership for oversight.

# **3. Security Incident Response Process**

When a security incident occurs, IT and Security must work together efficiently to mitigate risks and resolve the issue. This section outlines the process for identifying, responding to, and escalating security incidents.

### **3.1 Incident Identification & Reporting**

A security incident may be identified in several ways, including:

- **Security Monitoring Systems** – Alerts from <COMPANY_NAME>’s security tools.
- **IT Observations** – IT detecting unusual system activity or compromised accounts.
- **User Reports** – Employees reporting suspicious activity, phishing attempts, or lost/stolen devices.
- **Security Team Simulations** – Phishing tests and other security exercises.

If an IT team member identifies or is notified of a security incident, they must:

1. Report the incident immediately in **<QUEUE_NAME>** (unless the issue is highly sensitive, in which case IT Leadership should be contacted directly).
2. If necessary, escalate to the **Security team** to determine next steps.

### **3.2 Security Incident <MESSAGING_PLATFORM> Channel Creation & Participation**

For significant incidents, the **Security team will create a dedicated private <MESSAGING_PLATFORM> channel** and add relevant IT and Security team members. The channel should be used for:

- Coordinating response efforts in real time.
- Assigning tasks to IT and Security members.
- Providing status updates and tracking resolution progress.
- Keeping all communications centralized for documentation and post-incident review.

Once the incident is resolved, the channel will be archived, and the Security team may conduct a **post-incident review** .

### **3.3 IT’s Role in Security Incidents**

The IT team plays a crucial role in containing and mitigating security incidents. Common responsibilities include:

- **Locking or wiping stolen/lost devices** – Using **<ENDPOINT_MANAGEMENT_PLATFORM>** to remotely lock or erase compromised Mac laptops.
- **Disabling accounts** – Revoking access via **<IDENTITY_PROVIDER>** if an account is compromised.
- **Disabling devices** - Suspending or Deactivating managed devices in **<IDENTITY_PROVIDER>** if a machine or machine’s user’s account is compromised.
- **Investigating IT system logs** – Reviewing access and activity logs for signs of unauthorized access.
- **Assisting with network security** – Working with the Networking team to isolate affected systems if needed.

All actions taken must be documented in the incident <MESSAGING_PLATFORM> channel and updated in the <TICKETING_SYSTEM> tracking ticket if applicable.

### **3.4 Escalation to Legal**

Certain security incidents may require involvement from <COMPANY_NAME>’s **Legal team** , particularly those involving:

- **Data breaches or potential compliance violations.**
- **Legal holds on employee data or devices.**
- **Requests for IT action related to legal cases.**

In such cases, IT Leadership must be looped in, and Legal should be contacted via <EMAIL_ADDRESS> . Any legal requests for IT action must be formally submitted through a **<TICKETING_SYSTEM> ticket** for tracking.

# **4. IT Security Requests & Change Management**

To ensure security-related IT changes are properly tracked, documented, and implemented, all requests must go through the **<TICKETING_SYSTEM> ticketing system** . This section outlines how IT and Security collaborate on system changes and security policy updates.

### **4.1 Security Requesting IT Changes (IT <TICKETING_SYSTEM> Queue)**

If the **Security team requires changes to IT-managed systems** , they must submit a **<TICKETING_SYSTEM> ticket in the IT queue** . Examples of such requests include:

- **<ENDPOINT_MANAGEMENT_PLATFORM> profile or enforcement changes** (e.g., enabling stricter security policies).
- **Access control modifications** (e.g., restricting or modifying user access to systems).
- **Implementation of new security measures** (e.g., enforcing additional authentication layers).
- **Network or endpoint security enhancements** (e.g., firewall changes, new device monitoring configurations).

**Process:**

1. Security submits a **<TICKETING_SYSTEM> ticket in the IT queue** , detailing the request and rationale.
2. IT reviews the request, assesses the impact, and assigns it to the appropriate team member.
3. IT Leadership is consulted for approvals on major changes.
4. IT implements the change and updates the ticket with resolution details.
5. Security validates the change and confirms closure.

### **4.2 IT Requesting Security Policy Changes (Security <TICKETING_SYSTEM> Queue)**

If **IT identifies a security concern that requires a change in Security policy** , a **<TICKETING_SYSTEM> ticket must be submitted in the Security queue** . Examples include:

- **Requesting modifications to security monitoring tools** (e.g., adjusting alert thresholds).
- **Proposing changes to phishing or security awareness programs** (e.g., adding IT-specific training).
- **Recommending adjustments to endpoint security policies** (e.g., enforcing stricter software update policies).

**Process:**

1. IT submits a **<TICKETING_SYSTEM> ticket in the Security queue** , explaining the request and justification.
2. Security evaluates the request and discusses any required modifications.
3. If approved, Security implements the change.
4. IT is notified of the change and updates any necessary documentation.

### **4.3 Prioritization & Approval Process**

- **Security & legal-related IT requests take priority** over routine IT tasks.
- **High-impact changes** (e.g., major security policy adjustments) require IT Leadership approval.
- **Emergency security changes** (e.g., responding to an active threat) should be escalated immediately through <MESSAGING_PLATFORM> and followed up with a <TICKETING_SYSTEM> ticket.

# **5. Escalation Process**

Security and legal incidents must be escalated appropriately to ensure they are addressed with the necessary urgency and oversight. This section outlines the escalation procedures for different scenarios, ensuring clear lines of communication and accountability.

### **5.1 Security Incident Escalation**

If an IT security incident is identified, the following escalation steps must be followed:

1. **Initial Detection & Reporting**
  - The incident is reported in **<QUEUE_NAME>** (unless sensitive, in which case IT Leadership should be contacted directly).
    - Security assesses the severity and determines if a dedicated **incident <MESSAGING_PLATFORM> channel** is needed.
2. **Escalation to IT Leadership**
  - If the incident involves **compromised employee accounts, widespread system impact, or high-risk data exposure** , IT Leadership must be notified.
    - IT Leadership will determine if additional resources or external support (e.g., security vendors) are required.
3. **Critical Incidents & Executive Notification**
  - If the incident is **business-critical** (e.g., major data breach, system-wide compromise), IT and Security must escalate to **Executive Leadership** for awareness and decision-making.
    - Security will determine if external reporting (e.g., regulatory compliance notifications) is required.

### **5.2 Legal Escalation Process**

For legal matters requiring IT support, escalation follows these steps:

1. **Legal Request Initiation**
  - Legal contacts IT via <EMAIL_ADDRESS> or submits a **<TICKETING_SYSTEM> ticket** in the IT queue.
    - If an IT team member receives a legal request directly, they must **loop in IT Leadership before taking any action** .
2. **IT Leadership Review & Approval**
  - IT Leadership reviews the request and consults with Legal as needed.
    - If the request involves **data access, retention, or device retrieval** , IT ensures proper documentation and compliance with company policies.
3. **High-Priority Legal Requests**
  - Any legal matter involving **litigation, regulatory investigations, or executive-level involvement** must be **immediately escalated to IT Leadership and Security** .
    - IT must prioritize legal-related tasks over all other projects until resolution.

### **5.3 When & How to Escalate**

- **Urgent security incidents** → Notify **Security & IT Leadership immediately** via <MESSAGING_PLATFORM>.
- **Major IT system breaches** → Escalate to **Executive Leadership** for visibility.
- **Legal requests** → Always **loop in IT Leadership** before taking action.
- **Confidential or high-risk matters** → Avoid public channels; escalate directly to the appropriate stakeholders.

# **6. Communication & Documentation**

Clear and structured communication is essential for effective incident response and collaboration between IT, Security, and Legal teams. This section outlines the key communication channels, documentation requirements, and best practices for tracking security and legal-related incidents.

### **6.1 Primary Communication Channels**

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| **Channel** | **Purpose** | **Access** |
| **<QUEUE_NAME> (<MESSAGING_PLATFORM>)** | General collaboration between IT and Security | IT & Security teams |
| **Incident-specific <MESSAGING_PLATFORM> channel** | Created for active security incidents | IT, Security, and relevant stakeholders |
| **<TICKETING_SYSTEM> (IT Queue)** | Security requests for IT-related changes | IT & Security teams |
| **<TICKETING_SYSTEM> (Security Queue)** | IT requests for security policy changes | IT & Security teams |
| **Legal Email (** <EMAIL_ADDRESS> **)** | Primary contact for legal-related matters | IT Leadership & Legal Team |
| **IT Leadership Direct Contact** | Used for high-priority or sensitive incidents | IT Leadership & Senior Security Staff |

- **Sensitive discussions** should be kept within **private <MESSAGING_PLATFORM> channels** or **direct IT Leadership communication** .
- **Major security or legal incidents** should be escalated quickly using the appropriate channel (see **Section 5: Escalation Process** ).

### **6.2 Incident Documentation**

All security and legal-related incidents must be **properly documented** in <TICKETING_SYSTEM> to ensure accountability and compliance.

#### **Security Incidents**

- **<TICKETING_SYSTEM> Ticket** : All security incidents must have a corresponding <TICKETING_SYSTEM> ticket for tracking.
- **Incident <MESSAGING_PLATFORM> Channel** : If created, key decisions and actions must be logged for reference.
- **Resolution Summary** : After resolution, Security will document the root cause, mitigation steps, and lessons learned.

#### **Legal Requests**

- **<TICKETING_SYSTEM> Ticket** : All legal-related IT tasks must have a <TICKETING_SYSTEM> ticket with approval from IT Leadership.
- **Email Documentation** : Any email correspondence with Legal must be logged within the <TICKETING_SYSTEM> ticket.
- **Data Access Requests** : Legal must provide formal written approval before IT grants access to any employee data or devices.

### **6.3 Best Practices for Communication**

- **Use clear, concise language** when reporting incidents to avoid misinterpretation.
- **Keep <TICKETING_SYSTEM> tickets up to date** with status changes, resolutions, and key decisions.
- **Follow up on open incidents** regularly to ensure timely resolution.
- **Escalate high-priority matters** immediately instead of waiting for regular ticket processing.
