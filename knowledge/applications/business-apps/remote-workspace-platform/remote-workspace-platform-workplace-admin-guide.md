---
id: kb-applications-business-apps-remote-workspace-platform-remote-workspace-platform-workplace-admin-guide
title: <REMOTE_WORKSPACE_PLATFORM>/Administration Guide
canonical_path: knowledge/applications/business-apps/remote-workspace-platform/remote-workspace-platform-workplace-admin-guide.md
summary: This guide will focus on how to provision, support, and administrate <REMOTE_WORKSPACE_PLATFORM>/Workplace for <COMPANY_NAME>. <REMOTE_WORKSPACE_PLATFORM> Workplace Blue Border(BB) are all used interchangeably for this system. It is designed for contractors that DO...
type: reference
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: <REMOTE_WORKSPACE_PLATFORM>/Administration Guide
team: Identity and Access
systems: []
services: []
tags: []
created: '2025-10-27'
updated: '2025-10-30'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
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
- kb-applications-business-apps-remote-workspace-platform-index
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

This guide will focus on how to provision, support, and administrate <REMOTE_WORKSPACE_PLATFORM>/Workplace for <COMPANY_NAME>. <REMOTE_WORKSPACE_PLATFORM> - Workplace - Blue Border(BB) are all used interchangeably for this system. It is designed for contractors that **DO NOT** have a <COMPANY_NAME> managed computer. Computers using <REMOTE_WORKSPACE_PLATFORM> may be a personally owned device or a corporate device provided by their contracting agency.

- <REMOTE_WORKSPACE_PLATFORM> is the name of the company and the <IDENTITY_PROVIDER> tile
- Workplace is the name of the app installed on the computer
- Blue Border(BB) is a reference to the digital blue border the app places around programs that are managed by Workplace.

<REMOTE_WORKSPACE_PLATFORM> has an immense library of support documents, videos, and guides that are linked here.

[General <REMOTE_WORKSPACE_PLATFORM> Info](<INTERNAL_URL>)

---

## **How to Assign <REMOTE_WORKSPACE_PLATFORM>**

<REMOTE_WORKSPACE_PLATFORM> access should only be granted to contractors that are approved to have access . Our initial roll out has already determined this and new contractors will be assigned access by onboarding requests for <REMOTE_WORKSPACE_PLATFORM>.

1. In <IDENTITY_PROVIDER>, add user to ASSIGN - <REMOTE_WORKSPACE_PLATFORM> - Users group.
  1. This adds the tile to their <IDENTITY_PROVIDER> and automatically invites them to <REMOTE_WORKSPACE_PLATFORM>
    2. Accepting invite automatically provisions them

## **How to access <REMOTE_WORKSPACE_PLATFORM> Admin**

<REMOTE_WORKSPACE_PLATFORM> admin requires you to be an active user invited to <REMOTE_WORKSPACE_PLATFORM>. You can access admin by downloading the Workplace App and then clicking <REMOTE_WORKSPACE_PLATFORM> in <IDENTITY_PROVIDER> or through their browser extension “the workspace browser extension. Admin requires compliance checks just like any user accessing Workplace. If you encounter compliance issues, you can be added to an exclusion group (covered later).

1. Direct <REMOTE_WORKSPACE_PLATFORM> Admin link is [<INTERNAL_URL>](<INTERNAL_URL>)
  1. If this link does not work, follow the steps below to access.
2. Click on <REMOTE_WORKSPACE_PLATFORM> tile in <IDENTITY_PROVIDER>
3. Compliance checks run and then redirect you to screen below

1. Do **NOT** click checkbox to “Always allow…”
2. Click Cancel and then on screen behind, click “continue to webapp”.
3. Then click “Company admin” at top of screen.

## **Compliance Policies** [**<REMOTE_WORKSPACE_PLATFORM> Security Controls**](<INTERNAL_URL>)

Below are the globally enforced policies. These may change from vendor to vendor if we need to make exclusions for conflicts but there currently aren’t any.

## **<REMOTE_WORKSPACE_PLATFORM> and <IDENTITY_PROVIDER> Conditional Access**

<REMOTE_WORKSPACE_PLATFORM> is now the exclusive way to access <COMPANY_NAME> systems if the user is part of Assign - <REMOTE_WORKSPACE_PLATFORM> - Users. Meaning if they have <REMOTE_WORKSPACE_PLATFORM> access, the only way to access anything in <IDENTITY_PROVIDER> is if they are connected through <REMOTE_WORKSPACE_PLATFORM>.

Access to [<COMPANY_NAME>.<IDENTITY_PROVIDER>.com](<INTERNAL_URL>) hone page is still allowed outside of <REMOTE_WORKSPACE_PLATFORM> but clicking on a tile is met with a message that “You do not have permissions…”. This is expected behavior to prevent access outside of <REMOTE_WORKSPACE_PLATFORM>.

When connected to <REMOTE_WORKSPACE_PLATFORM>, tiles/access work as expected.

## **Associated Documents**

[<REMOTE_WORKSPACE_PLATFORM> Security Controls](<INTERNAL_URL>)

[<REMOTE_WORKSPACE_PLATFORM> Contractor Onboarding Process – Internal Guide](<INTERNAL_URL>)

[Supplier Comms re: <REMOTE_WORKSPACE_PLATFORM>](<INTERNAL_URL>)

[Contractor Comms re: <REMOTE_WORKSPACE_PLATFORM>](<INTERNAL_URL>)

[<COMPANY_NAME>/<REMOTE_WORKSPACE_PLATFORM> Readiness Runbook for Contractors (Windows & macOS)](<INTERNAL_URL>)

[<REMOTE_WORKSPACE_PLATFORM> Install - How-to Guide](<INTERNAL_URL>)

[<REMOTE_WORKSPACE_PLATFORM> Implementation - Contractor Device Needs and Reach Out Plan.xlsx](<INTERNAL_URL>)
