---
id: kb-helpdesk-configuration-and-automation-sla-policy-and-definitions
title: SLA Policy and Definitions
canonical_path: knowledge/helpdesk/configuration-and-automation/sla-policy-and-definitions.md
summary: 'Timezone: <TICKETING_SYSTEM> default (GMT 08:00) Los Angeles.'
knowledge_object_type: service_record
legacy_article_type: policy
object_lifecycle_state: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: SLA Policy and Definitions
team: Service Desk
systems:
- <TICKETING_SYSTEM>
tags:
- service-desk
created: '2026-02-19'
updated: '2026-03-04'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: service_desk
service_name: SLA Policy and Definitions
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
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-helpdesk-configuration-and-automation-index
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
- kb-helpdesk-configuration-and-automation-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Service calendar ("IT SLA 2026")

Timezone: <TICKETING_SYSTEM> default (GMT-08:00) Los Angeles.

## Working hours

Represents total hours between IST, LON, and PST, in PST timezoning

| Column 1 | Column 2 |
| --- | --- |
| Day | Hours (Los Angeles time) |
| Monday | 00:00-17:00; 20:30-24:00 |
| Tuesday | 00:00-17:00; 20:30-24:00 |
| Wednesday | 00:00-17:00; 20:30-24:00 |
| Thursday | 00:00-17:00; 20:30-24:00 |
| Friday | 00:00-17:00 |
| Sunday | 20:30-24:00 |

SLA timers count only during the above working hours, excluding configured [holidays](<INTERNAL_URL>)) .

# SLA metrics

## Time to first response

Measures the elapsed SLA time from ticket creation until a first-response stopping condition is met (see Section 4.1).

## Time to resolution

Measures the elapsed SLA time from ticket creation (and resolution cleared) until a resolution stopping condition is met (see Section 4.2).

# Targets (time goals)

## Time to first response targets

Work items are checked against the following goals in order (top to bottom). The first matching JQL applies.

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Goal filter (JQL) | Calendar | Target |
| assignee in membersOf("IT Team - All Support") (all priorities) | IT SLA 2026 | 30m |
| issuetype = Incident (all priorities) | IT SLA 2026 | 30m |
| issuetype = Change (all priorities) | <QUEUE_NAME> SLA Calendar 24-25 | 40h |
| issuetype in ("Service Request", "Service Request with Approvals", "Software or Hardware") (all priorities) | IT SLA 2026 | 30m |
| All remaining work items | IT SLA 2026 | No target |

## Time to resolution targets

Work items are checked against the following goals in order (top to bottom). The first matching JQL applies.

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Goal filter (JQL) | Calendar | Target |
| issuetype = Incident (all priorities) | IT SLA 2026 | 24h |
| issuetype = Change (all priorities) | IT SLA 2026 | 160h |
| "Request Type" = "<COMPANY_NAME> Operator Role (<QUEUE_NAME>)" (all priorities) | <QUEUE_NAME> SLA Calendar 24-25 | 160h |
| issuetype in ("Service Request", "Service Request with Approvals", "Software or Hardware") (all priorities) | IT SLA 2026 | 40h |
| All remaining work items | <QUEUE_NAME> SLA Calendar 24-25 | No target |

# Reference

## Holidays (one-time entries in 2026)

| Column 1 | Column 2 |
| --- | --- |
| Holiday | Date |
| New Year's Day | 1 Jan 2026 |
| (IN) Makara Sankranti | 14 Jan 2026 |
| (<REGION_C>) MLK | 19 Jan 2026 |
| (IN) Republic Day | 26 Jan 2026 |
| (<REGION_C>) President's Day | 16 Feb 2026 |
| (CA) Family Day | 16 Feb 2026 |
| (IN) Maha Shivaratri | 16 Feb 2026 |
| (IN) Holi | 4 Mar 2026 |
| (IN) Id-ul-Fitr | 21 Mar 2026 |
| (CA, <REGION_D>, IN) Good Friday | 3 Apr 2026 |
| (<REGION_D>) Easter Monday | 6 Apr 2026 |
| (IN) May Day | 1 May 2026 |
| (<REGION_D>) Early May Day | 4 May 2026 |
| (CA) Victoria Day | 18 May 2026 |
| (<REGION_C>) Memorial Day | 25 May 2026 |
| (<REGION_D>) Spring Bank Holiday | 25 May 2026 |
| (IN) Regional public holiday | 2 Jun 2026 |
| (<REGION_C>) Juneteenth | 19 Jun 2026 |
| (CA) <REGION_B> Day | 1 Jul 2026 |
| (<REGION_C>) Independence Day | 3 Jul 2026 |
| (CA) BC/Civic/Hertiage Day | 3 Aug 2026 |
| (IN) Independence Day | 15 Aug 2026 |
| (<REGION_D>) August Bank Holiday | 31 Aug 2026 |
| (<REGION_C> & CA) Labor Day | 7 Sep 2026 |
| (IN) Ganesh Chaturthi | 14 Sep 2026 |
| (CA) National Day of Truth & Reconciliation | 30 Sep 2026 |
| (IN) Ganhi Jayanti | 2 Oct 2026 |
| (CA) Thanksgiving | 12 Oct 2026 |
| (IN) Dussehra / Vijayadasham | 20 Oct 2026 |
| (IN) Diwali | 9 Nov 2026 |
| (CA) Remembrance Day | 11 Nov 2026 |
| (<REGION_C>) Thanksgiving | 26 Nov 2026 |
| (<REGION_C>) Day after Thanksgiving | 27 Nov 2026 |
| Holiday Week | 25 Dec 2026 |
| Holiday Week | 26 Dec 2026 |
| Holiday Week | 27 Dec 2026 |
| Holiday Week | 28 Dec 2026 |
| Holiday Week | 29 Dec 2026 |
| Holiday Week | 30 Dec 2026 |
| Holiday Week | 31 Dec 2026 |

## SLA measurement rules (as configured)

### Time to first response - start, pause, stop conditions

Start counting time when: Issue Created.

Pause counting time during: No conditions configured.

Finish counting time when any of the following occurs:

- Comment: For Customers
- Entered Status: Cancelled
- Entered Status: Closed
- Entered Status: Escalated
- Entered Status: In Progress
- Entered Status: Pending
- Entered Status: Under review
- Entered Status: Waiting for approval
- Entered Status: Waiting for customer
- Entered Status: Won't Do
- Entered Status: Work in progress
- Resolution: Set

### Time to resolution - start, pause, stop conditions

Start counting time when:

- Issue Created
- Resolution: Cleared

Pause counting time during:

- Status: Pending
- Status: Verify in 1 month
- Status: Verify in 1 week
- Status: Waiting for approval
- Status: Waiting for customer

Finish counting time when any of the following occurs:

- Entered Status: Cancelled
- Entered Status: Closed
- Entered Status: Completed
- Entered Status: Declined
- Entered Status: Resolved
- Entered Status: Won't Do
- Resolution: Set
