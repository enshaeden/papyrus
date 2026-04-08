---
id: kb-assets-deployment-windows-device-user-account-setup-internal
title: Windows Device User Account Setup (Internal)
canonical_path: knowledge/assets/deployment/windows-device-user-account-setup-internal.md
summary: note cf197999997c After implementing Windows Hello Project for all users, we will add the Device
  Attestation Users group, or any other relevant group, to this list. After implementing Windows Hello
  Project for all...
knowledge_object_type: runbook
legacy_article_type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Windows Device User Account Setup (Internal)
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
- <HR_SYSTEM>
tags:
- endpoint
- windows
- account
created: '2025-09-18'
updated: '2026-02-26'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
- Identity
prerequisites:
- Confirm the device, asset record, and office or shipping context before taking action.
- Verify you have the required inventory, MDM, or ticketing access for the task.
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
- kb-assets-deployment-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
- Identity
related_articles:
- kb-assets-deployment-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# Purpose

- This KBA outlines the process to prepare a windows user account for FTE after setting up the <IDENTITY_PROVIDER> account per <COMPANY_NAME> New User Account Setup Process.

# Objective

- **Scope of this KBA includes:**
  - Assign the required groups in <IDENTITY_PROVIDER>.
    - Assign the proper licenses to the account.
    - Assign the account into the right MDM groups.

---

## Step 1: <IDENTITY_PROVIDER> Account Setup

- Once account is imported and staged in <IDENTITY_PROVIDER> per [<COMPANY_NAME> New User Account Setup Process](<INTERNAL_URL>) , add user to these <IDENTITY_PROVIDER> groups
  - **<PRODUCTIVITY_PLATFORM>-<COLLABORATION_PLATFORM> Apps Group**
    - **<PRODUCTIVITY_PLATFORM>-<ENDPOINT_MANAGEMENT_PLATFORM>**

---

## Step 2: <PRODUCTIVITY_PLATFORM> Account Setup

- Go to [<PRODUCTIVITY_PLATFORM> Admin Portal](<INTERNAL_URL>)

- Search for the user’s name and select their profile from the results.

- Clicking on the pop-up will prompt a sidebar to open up. Make your way over to the **“Licenses”** section and provision them with **“Enterprise Mobility+Security standard tier" and“<COLLABORATION_PLATFORM> Apps for enterprise”** license. Make sure to save any changes that you have made.

> INFO: **<ENDPOINT_MANAGEMENT_PLATFORM> license** will soon be replaced with **Enterprise Mobility+Security standard tier license.**

- Under the **‘Account Tab’** Click on **Manage Groups**
- Click on **Assign Memberships** and **add user** to below groups

note cf197999997c After implementing **Windows Hello Project** for all users, we will add the **Device Attestation Users** group, or any other relevant group, to this list. After implementing **Windows Hello Project** for all users, we will add the **Device Attestation Users** group, or any other relevant group, to this list.

---

# Related Documentation

- [Day 1: Onboarding and Setup Overview of New User Account Setup](../../user-lifecycle/onboarding-new-hires/day-1-onboarding-and-setup.md)
- Step by Step Guide for New User Setup Step by Step Guide for New User Setup
- [Workstation Setup Guide - Windows](<INTERNAL_URL>)
