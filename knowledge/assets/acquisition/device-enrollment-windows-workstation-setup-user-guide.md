---
id: kb-assets-acquisition-device-enrollment-windows-workstation-setup-user-guide
title: device enrollment - Windows Workstation Setup - User Guide
canonical_path: knowledge/assets/acquisition/device-enrollment-windows-workstation-setup-user-guide.md
summary: "This guide walks you through the account setup process for your Windows device preconfigured\
  \ with Windows device enrollment Profile . Your device is registered and prepared \u2014 just sign in\
  \ and follow a few steps."
knowledge_object_type: runbook
legacy_article_type: asset
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: device enrollment - Windows Workstation Setup - User Guide
team: Systems Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
tags:
- endpoint
- windows
created: '2025-09-18'
updated: '2025-11-09'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Endpoint Provisioning
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
  source_ref: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-assets-acquisition-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Endpoint Provisioning
related_articles:
- kb-assets-acquisition-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

> INFO: To be migrated to End User space

# Overview

This guide walks you through the **account setup process** for your Windows device preconfigured with [**Windows device enrollment Profile** .](<INTERNAL_URL>) Your device is registered and prepared — just sign in and follow a few steps.

# Before You Begin

Make sure you have:

- A stable **Wi-Fi or Ethernet** connection.
- Your **work or school account** credentials (email and password).
- Access to **<MFA_APPLICATION>(on phone)**

# Step-by-Step Setup

## 1. Sign In with Your Work or School Account

- After turning on device, Enter your **<COMPANY_NAME> email address** (e.g., <EMAIL_ADDRESS> ).
- Type your **password** , then approve <MFA_APPLICATION> MFA request (text, app approval, etc.).
- You may be asked to login again after this step

## 2. Account Setup

Once you’ve signed in, Windows will automatically begin the **Account Setup** process. During this step, your device connects to <PRODUCTIVITY_PLATFORM> <ENDPOINT_MANAGEMENT_PLATFORM> and starts downloading:

- Company apps
- Security configurations
- Compliance policies If setup takes longer than expected or gives an error, you can click on **“Continue anyway”** button.

🔵 You can start working while the rest of your setup finishes quietly in the background.

### Quick Tip

If you ever see **“Continue anyway,”** it’s completely fine to proceed. Your device will **keep setting up in the background** and apply everything automatically — no extra steps needed.

## 3. Windows Hello Setup

After completing account setup, you will see the Windows Hello setup page where you can set up the fingerprint and PIN.

### 1. Fingerprint Setup

- Click on **“Yes, Set up”**
- Tap the fingerprint scanner until it fills with blue
- Once complete, click on **‘Next’**

### 2. Create a PIN

- Click **Next** on the Create a PIN page
- Sign in to your account when prompted
- Set your PIN and press **OK**

## 4. Welcome to Windows

Once setup completes, you’ll be taken to your **Windows desktop/Login Page** . Your device is now ready to use with:

- Company apps (e.g., **<MFA_APPLICATION>, <COLLABORATION_PLATFORM> browser, <VIDEO_CONFERENCING_PLATFORM>, <MESSAGING_PLATFORM>** )
- Security protections (e.g., BitLocker, antivirus, device compliance)
- Access to company cloud resources

## 5. <MFA_APPLICATION> Setup

[<MFA_APPLICATION> Setup Guide (Windows)](<INTERNAL_URL>)
