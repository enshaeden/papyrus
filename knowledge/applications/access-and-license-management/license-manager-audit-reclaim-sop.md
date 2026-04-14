---
id: kb-applications-access-and-license-management-license-manager-audit-reclaim-sop
title: "License Manager \u2014 Audit & Reclaim SOP"
canonical_path: knowledge/applications/access-and-license-management/license-manager-audit-reclaim-sop.md
summary: 'This document explains how IT runs license audits using the License Manager table in the Asset
  Tracker (<ASSET_MANAGEMENT_SYSTEM>). It covers: trigger conditions, how to select candidates, step by
  step audit workflows, automation...'
knowledge_object_type: runbook
legacy_article_type: SOP
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: "License Manager \u2014 Audit & Reclaim SOP"
team: IT Operations
systems:
- <ASSET_MANAGEMENT_SYSTEM>
tags:
- account
- access
created: '2026-02-18'
updated: '2026-03-06'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: it_ops
related_services:
- Access Management
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
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

## Purpose

This document explains how IT runs license audits using the **License Manager** table in the Asset Tracker (<ASSET_MANAGEMENT_SYSTEM>). It covers: trigger conditions, how to select candidates, step-by-step audit workflows, automation setup for <BUSINESS_APPLICATION_C> emails, reclaim execution, edge cases and reporting for leadership.

---

## When to run an audit

- At vendor renewal time for a specific software (preferred).
- When we are low on available licenses and want to avoid purchasing more.
- Ad-hoc: when the **License Available** <MESSAGING_PLATFORM> alert appears for a license where termination date = today.
- One license (software) at a time (e.g., <BUSINESS_APPLICATION_C>).

---

## Key fields & statuses (reference)

Use these field names exactly as your table currently contains (or map them if different):

- `Software` (single select)
- `Assignee` / `User` (linked to Employees)
- `Employee Status` (lookup)
- `Termination Date`
- `Status` — values: **Available** , **Assigned** , **Expired** , **Awaiting Reclaim Response**
- `Reclaim URL` (used by email button)
- `Ask To Reclaim` (button field — permanent)
- Audit checkbox fields (create if missing):
  - `Send <APPLICATION_NAME> Reclaim email` (checkbox)
    - `Send <APPLICATION_NAME> Chase email` (checkbox)
    - `Confirmed User Needs <APPLICATION_NAME>` (checkbox)
    - `Reclaimed Via Audit` (checkbox)

**Automation note:** There's a <MESSAGING_PLATFORM> automation that fires only when a termed user (termination date = today) still has a license assigned.

---

## Pre-Audit checks

1. Create a filtered view for the software you will audit (example view name: `Audit — <BUSINESS_APPLICATION_C>` ).
  - Filter: `Software = <BUSINESS_APPLICATION_C>`
    - Filter additional: `Status = Assigned` (if you want only assigned licenses), OR include `Employee Status = Deprovisioned` / `Termination Date not empty` depending on the focus.
2. Cross-check application administration portal: export or view user list in the application administration portal and confirm it matches License Manager records.
3. Ensure audit checkboxes exist (see Key fields). Add them if missing.
4. Create a copy of the view as a snapshot (or give it a date) so you can compare before/after.

---

## Step-by-step Audit Workflow

### 1. Identify candidates

- Open `Audit — <APPLICATION_NAME>` view.
- Confirm the listed users in <ASSET_MANAGEMENT_SYSTEM> match the application administration portal.
- Identify:
  - Termed users missed (Termination Date set, Employee Status = Deprovisioned).
    - Users who are assigned but inactive (if you have any usage logs).

### 2. Reclaim immediately for missed termed users

- For users with `Termination Date` present who should have been deprovisioned:
  1. Revoke/remove license in application administration portal (complete removal first).
    2. In <ASSET_MANAGEMENT_SYSTEM>, tick `Reclaimed Via Audit` .
    3. Update `Status` → **Available** .
- Rationale: always complete vendor removal first, then update <ASSET_MANAGEMENT_SYSTEM> so the system reflects reality.

### 3. <BUSINESS_APPLICATION_C> for active users (audit <BUSINESS_APPLICATION_C>)

- Use the `Send <APPLICATION_NAME> Reclaim email` checkbox to trigger an automation (see Automation section).
  - For initial <BUSINESS_APPLICATION_C>: tick `Send <BUSINESS_APPLICATION_C> Reclaim email` .
    - Wait for responses (responses go to `<EMAIL_ADDRESS>` to generate a ticket).
    - For each reply:
      - If user confirms they need it → tick `Confirmed User Needs <BUSINESS_APPLICATION_C>` .
          - If they confirm they do not need it / do not reply by deadline → reclaim license via vendor first, then tick `Reclaimed Via Audit` .
- After initial batch, disable the automation (prevent accidental re-sends).

### 4. Chase email

- For everyone not in `Confirmed User Needs` or `Reclaimed Via Audit` , send chase:
  - Tick `Send <BUSINESS_APPLICATION_C> Chase email` to trigger the follow-up automation.
    - Chase message should include a firm reply deadline (e.g., 7 days from chase send).
    - After deadline, proceed to reclaim for non-responders (leadership may decide in specific cases).

### 5. Finalise & report

- Keep daily updates for leadership during the audit cycle (see Reporting).
- Use the SUM / percentage summary in the view to show counts: `Confirmed` , `Reclaimed` , `Pending` .
- When audit is complete: ensure all vendor changes and <ASSET_MANAGEMENT_SYSTEM> updates are consistent.

---

## Email templates

### A. “Ask To Reclaim” — email button template (existing)

(Your permanent email template; used when you manually press `Ask To Reclaim` .)

Subject: License allocation — <APPLICATION_NAME>

Body:

> Dear {Name}, I hope you're doing well. I am reaching out regarding your license for <APPLICATION_NAME>, which we have noticed has not been used for some time. As this license is both costly and in limited supply, we would like to inquire whether you still require it. In accordance with our Software License Management Policy, we aim to reclaim licenses that have remained unused for more than 90 days to ensure efficient allocation. If you still require access, please let us know within the next seven days. Otherwise, we may proceed with reassigning the license to another user who has requested it. Please feel free to reach out if you have any questions or concerns. Best regards

---

### B. Audit initial email — automation

Subject: License Update: <APPLICATION_NAME> License

Body:

> Hi {Name}, We’re currently auditing our <APPLICATION_NAME> licenses ahead of the upcoming renewal. To make sure we’re using our licenses effectively, could you please reply to this email or raise a ticket via <EMAIL_ADDRESS> to confirm whether you still need access to <APPLICATION_NAME>, or if your license can be reclaimed and reassigned to another user? If we don’t hear back, we may assume the license is no longer required. Thanks for your help! Kind regards, IT @ <COMPANY_NAME>

**Reply-to:** <EMAIL_ADDRESS>

---

### C. Audit chase email — automation (7 days later)

Subject: Reminder — confirm whether you need <APPLICATION_NAME>

Body:

> Dear {Name}, A week ago we reached out regarding your <APPLICATION_NAME> licence. To remind you, please confirm by **{deadline date}** whether you still require access. If we do not receive a reply, we may reclaim the licence and reassign it to another user. If you need more time, please reply and we’ll note that. Otherwise, reply to this message or raise a ticket at <EMAIL_ADDRESS> . Thanks, IT @ <COMPANY_NAME>

---

## Automation setup (<ASSET_MANAGEMENT_SYSTEM>) — practical details

**Automation <QUEUE_NAME> — Initial audit email**

- **Trigger:** When record updated → `Send <BUSINESS_APPLICATION_C> Reclaim email` is ticked.
- **Conditions:** `Status = Assigned` AND `Confirmed User Needs <BUSINESS_APPLICATION_C>` is unchecked AND `Reclaimed Via Audit` is unchecked.
- **Action:** Send email (From IT email or via email integration), Reply-to: <EMAIL_ADDRESS> , include record values. Optionally log automation run in an Audit Notes field.
- **Post-action:** (Optional) set a `Last Audit Email Sent` date field.

**Automation <QUEUE_NAME> — Chase email**

- **Trigger:** When record updated → `Send <BUSINESS_APPLICATION_C> Chase email` is ticked.
- **Conditions:** `Confirmed User Needs <BUSINESS_APPLICATION_C>` unchecked AND `Reclaimed Via Audit` unchecked AND `Last Audit Email Sent` older than 7 days (if tracking).
- **Action:** Send chase email with deadline.

**Important process rule:** After launching the first automation batch, **turn the automation off** to avoid accidental retriggers. Only re-enable it when you have a new batch to send.

---

## Reclaim execution steps (detailed)

1. Confirm non-response or confirmation to reclaim.
2. Remove license in application administration portal (do this first).
3. Update <ASSET_MANAGEMENT_SYSTEM>:
  - `Reclaimed Via Audit` = tick
    - `Status` = **Available**
    - Add a short note in `Audit Notes` explaining vendor action & date.
4. If license should trigger <MESSAGING_PLATFORM> automation, confirm your <MESSAGING_PLATFORM> rules (current <MESSAGING_PLATFORM> alert only fires for termed users with license assigned; reclamations by audit do not trigger <MESSAGING_PLATFORM>).

---

## Edge cases & escalation

- **User ignores emails** : escalate to director for final decision if ownership is contested. Leadership decides whether to forcibly reclaim.
- **User says “might need later”** : reply that they are welcome to raise a ticket later; you may reclaim now but will re-issue license if available.
- **Manager blocks reclaim** : honor manager’s request — do not reclaim.
- **Shared or email-tied licenses** : N/A (currently none).
- **If mismatch vendor <> <ASSET_MANAGEMENT_SYSTEM>** : prioritize vendor data; correct <ASSET_MANAGEMENT_SYSTEM> to match vendor after investigation.

---

## Tracking & reporting for leadership

Track & share daily updates while the audit is active. Useful metrics:

- Total Assigned (for the software)
- Reclaimed via audit (count)
- Confirmed Need (count)
- Awaiting response (count)
- % reclaimed = `Reclaimed via audit / Total Assigned * 100`

**Suggested <ASSET_MANAGEMENT_SYSTEM> formula example** (adapt fields names to your base):

- `Percent_Reclaimed` formula:

[CDATA[IF({Total_Assigned}=0, "0%", ROUND({Reclaimed_Count}/{Total_Assigned}*100,1) & "%") ]]

(Replace `{Total_Assigned}` and `{Reclaimed_Count}` with the actual rollup/summarised field names.)

**Reporting cadence** :

- Daily summary while audit is active.
- Final report with: total reclaimed, number confirmed, number escalated, estimated cost saved.

---

## Audit checklist (quick)

- Create `Audit — <APPLICATION_NAME> <date>` view and filter
- Cross-check application administration portal users
- Ensure checkboxes and automation fields exist
- Tick `Send ... Reclaim email` for initial batch
- Disable automation after sending
- Track replies in tickets ( <EMAIL_ADDRESS> )
- Chase non-responders with `Send ... Chase email`
- Reclaim in application administration portal → tick `Reclaimed Via Audit` in <ASSET_MANAGEMENT_SYSTEM>
- Daily update to leadership
- Close the audit with final report

---

## Example run (<BUSINESS_APPLICATION_C>)

1. Create view `Audit — <BUSINESS_APPLICATION_C>` .
2. Confirm vendor list match.
3. Tick `Send <BUSINESS_APPLICATION_C> Reclaim email` for all non-confirmed accounts.
4. Turn automation off.
5. Monitor `<QUEUE_NAME>` tickets; update `Confirmed User Needs <BUSINESS_APPLICATION_C>` as replies arrive.
6. After 7 days, tick `Send <BUSINESS_APPLICATION_C> Chase email` for remaining non-responders.
7. Reclaim and update <ASSET_MANAGEMENT_SYSTEM> for non-responders.
8. Publish final numbers to leadership daily, and final report at close.
