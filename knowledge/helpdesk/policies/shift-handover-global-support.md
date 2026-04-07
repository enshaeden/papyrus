---
id: kb-helpdesk-policies-shift-handover-global-support
title: Shift Handover & Global Support
canonical_path: knowledge/helpdesk/policies/shift-handover-global-support.md
summary: Ensures seamless IT support transitions across shifts in <REGION_A>, <REGION_D>, and the <REGION_C>, while maintaining visibility on critical issues and minimizing response delays.
type: policy
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Shift Handover & Global Support
team: Service Desk
systems:
- <TICKETING_SYSTEM>
services:
- Incident Management
tags:
- service-desk
created: '2025-10-28'
updated: '2025-12-12'
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

Ensures seamless IT support transitions across shifts in <REGION_A>, <REGION_D>, and the <REGION_C>, while maintaining visibility on critical issues and minimizing response delays.

# **<MESSAGING_PLATFORM> Channel Usage**

- **<QUEUE_NAME>** : Primary channel for all IT team communications, including emerging issues.
  - All team members must regularly monitor this channel during their shift.
    - Use this channel to flag emerging issues requiring global visibility.
- **<QUEUE_NAME>** : IT-only channel for global outages and time-sensitive incidents (e.g., SaaS downtime).
- **<QUEUE_NAME>** : HR+IT shared channel for urgent terminations only. Monitor this continuously.
- **<QUEUE_NAME>:** IT Helpdesk. For ticket handovers only.

# **Daily Shift Handoff Procedures**

## **<REGION_A> to <REGION_D>**

1. **Ticket Review & Assignment** :
  - Review all unresolved tickets in IT <QUEUE_NAME>.
    - Add internal notes for context where needed.
    - Assign or flag Europe-origin tickets for the <REGION_D> team.
2. **<MESSAGING_PLATFORM> Update** :
  - Post in <QUEUE_NAME> noting that <REGION_D> is taking over the queue.
    - Include any key context or urgent tickets.
    - Await ✅emoji acknowledgment in <MESSAGING_PLATFORM> from the receiving team member.
3. **Calendar Check** :
  - Ensure the Helpdesk Team Calendar reflects who is on shift and OOO status.

## **<REGION_D> to <REGION_C>**

(Repeat above steps, adjusted for <REGION_C> context)

1. Assign/flag <REGION_B> or <REGION_C>-origin tickets.
2. Handoff message in <QUEUE_NAME> with priority context.
3. Calendar verification.
4. Await ✅emoji acknowledgment from receiving <REGION_C> team member in <QUEUE_NAME>

## **<REGION_C> to <REGION_A>**

(Repeat for APAC shift)

1. Assign/flag <REGION_A>-region tickets.
2. <MESSAGING_PLATFORM> update in <QUEUE_NAME>
3. Calendar check for upcoming shift coverage.
4. Await ✅emoji acknowledgment from receiving <REGION_A> team member in <QUEUE_NAME>

# **Ticket Ownership & Internal Notes**

- Clearly document progress in IT <QUEUE_NAME> internal notes.
- Always assume the next shift lacks full context—write explicitly.
- Reassign tickets only after confirming the recipient.
- Use internal notes as the primary handoff reference.

# **Handling Urgent Tickets**

- Use **'HANDOVER'** prefix in <QUEUE_NAME> when posting urgent ticket transfers.
- Include:
  - Ticket number
    - Issue summary
    - Actions taken
    - Outstanding issues or next steps
- Tag the next shift's on-call technician directly.
- Await ✅ emoji acknowledgment in <MESSAGING_PLATFORM> before signing off.

# **Urgent Terminations**

- Monitor <QUEUE_NAME> throughout your shift.
- Immediately escalate any in-progress terminations at handover:
  - Tag next shift in <QUEUE_NAME>
    - Link related ticket or <MESSAGING_PLATFORM> thread

# **Global Outage Communications**

- Use <QUEUE_NAME> for global priority issues (e.g critical/global <VIDEO_CONFERENCING_PLATFORM>, <COLLABORATION_PLATFORM> outages).
- Tag all regions as needed to ensure rapid awareness.

# **National Holiday Coverage**

- Regional teams must:
  - Update the Helpdesk Calendar with upcoming holidays at least 1 week in advance.
    - Pre-review their queues and hand off anything urgent.
    - Notify <QUEUE_NAME> of expected coverage gaps.

**Best Practices:**

- Don't rely on passive messages—tag teammates for clarity.
- Keep internal ticket notes concise and complete.
- Update the Helpdesk Calendar daily with shift and OOO visibility.
- Monitor <QUEUE_NAME> throughout your shift to remain informed of issues and requests.

**Troubleshooting / FAQs:**

- *Q: No one acknowledges my handoff?* → Follow escalation procedures and tag team leads.
- *Q: Ticket lacks info at handoff?* → Ask for an internal note update before accepting.

**References / Additional Resources:**

- [IT Termination SOP] (internal link)
- <TICKETING_SYSTEM> IT <QUEUE_NAME> access guide
- <MESSAGING_PLATFORM> etiquette for critical issues
