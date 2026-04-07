---
id: kb-assets-acquisition-adding-mobile-devices-to-endpoint-enrollment-portal
title: Adding tablet devices/mobile devices to <ENDPOINT_ENROLLMENT_PORTAL>
canonical_path: knowledge/assets/acquisition/adding-mobile-devices-to-endpoint-enrollment-portal.md
summary: If we have standalone, or separately purchased, tablet devices or mobile devices, this is the manual way to add them into our <ENDPOINT_ENROLLMENT_PORTAL> so they get picked up by <ENDPOINT_MANAGEMENT_PLATFORM>
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Adding tablet devices/mobile devices to <ENDPOINT_ENROLLMENT_PORTAL>
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <ENDPOINT_MANAGEMENT_PLATFORM>
services:
- Endpoint Provisioning
tags:
- endpoint
created: '2025-10-22'
updated: '2025-10-22'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
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
related_articles:
- kb-assets-acquisition-index
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

If we have standalone, or separately purchased, tablet devices or mobile devices, this is the manual way to add them into our <ENDPOINT_ENROLLMENT_PORTAL> so they get picked up by <ENDPOINT_MANAGEMENT_PLATFORM>

# **Instructions**

### **Enrolling in <ENDPOINT_ENROLLMENT_PORTAL>**

1. Download **device preparation utility** to your Mac laptop if you haven’t yet
2. Via USB, connect the device to your laptop
3. Select the device in device preparation utility
4. In the toolbar, click **Prepare** .
5. Select **Manual Configuration** from the drop-down menu.
6. Check *Add to automated device enrollment service or <ENDPOINT_ENROLLMENT_PORTAL>* .
7. Un check *Activate and Complete Enrollment* and click **Next** .
8. In the *MDM Server* drop-down menu, choose **New Server** . Click **Next** .
9. In the *Name* field, enter *<ENDPOINT_ENROLLMENT_PORTAL>* . Leave the *MDM Server URL* as-is . Click **Next** .
10. You’ll receive an "Unable to verify the server's enrollment URL” message. Click **Next.**
11. Don’t add a certificate. Just click **Next** .
12. Select *New Organization* . Click **Next** .
13. Input <ENDPOINT_ENROLLMENT_PORTAL> managed enrollment account (i.e. the enrollment account you log into <ENDPOINT_ENROLLMENT_PORTAL> with). Click **Next** .
  1. To proceed, the associated ID must have an Administrator or Device Enrollment Manager role.
14. Click **Continue** to sign in.
15. Select *Generate a new supervision identity* .
16. In the Setup Assistant, select which panes you want to include. Click **Next** .
17. Ignore the Network Profile and click **Next** .
18. Enter your macOS administrator credentials. Click **Update Settings** .
19. If prompted, unlock and/or erase the device. Complete the enrollment in the Setup Assistant.

**The tablet device will wipe/reinstall itself**

1. In <ENDPOINT_ENROLLMENT_PORTAL>, in the Devices section, go to the group labeled *Devices added by manual enrollment* . Assign the device to the <ENDPOINT_MANAGEMENT_PLATFORM> MDM server.
2. Wait a few minutes then confirm you can find the device (by serial) in <ENDPOINT_MANAGEMENT_PLATFORM>: **Devices** > **Prestage Enrollments** > **tablet device/mobile device Prestage** > **Scope**
3. Test the tablet device is enrolled by attempting to set it up and (hopefully) arriving at the **Remote Setup** page. If so, immediately stop and turn it off and mail to user or stage in IT closet.
