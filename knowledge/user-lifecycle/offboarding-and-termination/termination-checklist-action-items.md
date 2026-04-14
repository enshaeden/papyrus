---
id: kb-user-lifecycle-offboarding-and-termination-termination-checklist-action-items
title: Termination Checklist Action items
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/termination-checklist-action-items.md
summary: Applications are listed alphabetically, A Z
knowledge_object_type: runbook
legacy_article_type: offboarding
object_lifecycle_state: active
owner: it_operations
source_type: imported
source_system: knowledge_portal_export
source_title: Termination Checklist Action items
team: IT Operations
systems:
- <HR_SYSTEM>
tags:
- offboarding
- checklist
created: '2026-02-17'
updated: '2026-02-25'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: it_ops
related_services:
- Offboarding
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
  source_ref: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-user-lifecycle-offboarding-and-termination-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Offboarding
related_articles:
- kb-user-lifecycle-offboarding-and-termination-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: docs/migration/seed-migration-rationale.md
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

Applications are listed alphabetically, A-Z

# **<PASSWORD_MANAGER>**

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Enter:
  1. **Search People:** [Name of the to-be-terminated user]
3. Click the **user’s name**

1. Click the **three dots**
2. Click **Suspend**

# <CREATIVE_PLATFORM>

1. Navigate to [<INTERNAL_URL>](<INTERNAL_URL>)
2. Log in with the it-team credentials stored in <PASSWORD_MANAGER> vault under IT (restricted) > AEM (cloud version).
3. Select the **User** tab on the top menu.
4. Using the search bar, look for the user’s email address. Once found, click on the name.
5. Under the **Products** tab, click on the **ellipsis icon > Edit** and click on the **X** on the top right corner of the name of the app to remove access. Repeat this process until you remove all products assigned.

1. Navigate to [<INTERNAL_URL>](<INTERNAL_URL>)
2. Log in with the it-team credentials stored in <PASSWORD_MANAGER> vault under **IT (restricted) > AEM on-premise.**
3. Click on the **hammer icon > Security > Users**
4. On the top search bar, enter the user’s email address or name, and click on the appropriate user.
5. Click on the trash icon on top of the user name.

# <COLLABORATION_PLATFORM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. **Search:** [Name of to-be-terminated user]
3. Click **[Name of to-be-terminated user]**
4. Click **security**

1. Click **Sign-in Cookies**
2. Click **RESET**

1. Click **SUSPEND USER**
2. Click **CHANGE ORGANIZATIONAL UNIT**
3. Click **Terminations** , then **CONTINUE**

## <COLLABORATION_PLATFORM> <BUSINESS_APPLICATION_B> and <COMPANY_NAME> Test

Follow identical steps for the two <COLLABORATION_PLATFORM> domains by opening an Incognito window and navigating to [<INTERNAL_URL>](<INTERNAL_URL>) and entering either <TEAM_NAME> or <EMAIL_ADDRESS> credentials to gain access to their respective <COLLABORATION_PLATFORM> admin portals.

## Remove Mobile Data

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click **Mobile Devices**
3. **Search:** [The name of the to-be-terminated user]
  1. Press **Enter/Return**
4. Click the **three dots**
5. Click **WIPE ACCOUNT**

# <ENDPOINT_MANAGEMENT_PLATFORM>

## Lock the device

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click **Computers**
3. **Search** for the assigned computer (record in <ASSET_MANAGEMENT_SYSTEM>)
4. Click **Management**
5. Click **Lock Computer**
  1. Set the 6-digit passcode
    2. (optional) set a lock message
      1. “This device has been marked for recovery and has been locked. If this action was in error, please reach out to <EMAIL_ADDRESS>”

# <DEVELOPER_TOOL_SUITE>

1. Log into <DEVELOPER_TOOL_SUITE> through [<IDENTITY_PROVIDER>](<INTERNAL_URL>)
2. Locate the terminated user in the list and **check the box**
3. Click **Manage**
4. Click **Revoke 1 license from user**
5. Click **Revoke 1 license**

# <TICKETING_SYSTEM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Enter:
  1. **Search for people and teams:** [Name of the to-be-terminated user]
    2. Click the **user’s name**
3. Click **the three dots**
4. Click **Manage access**
5. Toggle the **switch**

# <PRODUCTIVITY_PLATFORM>

## Office License recovery

**Steps to remove <COLLABORATION_PLATFORM> apps License**

1. **Go to <PRODUCTIVITY_PLATFORM> admin portal** : [<INTERNAL_URL>](<INTERNAL_URL>)
2. **Go to Active Users**

> In the left navigation panel, click Users **>** Select Active Users

1. **Select the User**

>Search for and click on the user’s name. >Open the Licenses and Apps tab.

1. **Remove the License**

>You’ll see assigned licenses (e.g., <COLLABORATION_PLATFORM> standard tier, Business Premium, etc.). >Uncheck the license you want to remove. >Click Save changes.

**Steps to remove Enterprise mobility + Security standard tier license**

1. **Access the <DIRECTORY_SERVICE> portal**
  - Navigate to the <DIRECTORY_SERVICE> portal [<INTERNAL_URL>](<INTERNAL_URL>)
    - On the <DIRECTORY_SERVICE> portal home page, click on **<DIRECTORY_SERVICE>** .

1. **Remove the User from the Group**
  - In <DIRECTORY_SERVICE>, navigate to **Groups** .
    - Under **Total groups** , use the search bar to find the group named " **Device attestation users** ".
    - Select the group and go to the **Manage** section, then choose **Members** .
    - Search for the specific user you wish to remove.
    - Select the user from the list.
    - Click on **Remove user** .

This action will successfully remove the user from the group. After a few minutes, the standard tier license will be automatically unassigned from the user.

# **<IDENTITY_PROVIDER>**

- Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
- **Find the user:**
  - Search **:** [Name of to-be-terminated user]
    - Click the user’s name
- **Reset access and authentication**
  - Reset or Remove password
      - Select “Temporary” - Do NOT send a reset email
    - Reset Authenticators
    - Clear User Sessions
- **Deactivate** the account

# <VIDEO_CONFERENCING_PLATFORM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. **Search:** [Name of terminated user]
3. Click **Edit**
4. Select **Basic**
5. Uncheck **Large Meeting** and/or **Webinar** if checked
6. Click **Save**

> INFO: If the terminated employee is within the Recruiting or the HR org please DELETE their account and TRANSFER one of <VIDEO_CONFERENCING_PLATFORM> Services accounts (<VIDEO_CONFERENCING_PLATFORM> Recruiter Accounts 1-10). This is done so <ONBOARDING_WORKFLOW> meetings aren’t affected. In addition, tag someone on the enterprise applications team to remove the user from the <VIDEO_CONFERENCING_PLATFORM> integration in <ONBOARDING_WORKFLOW>.
