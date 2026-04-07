---
id: kb-user-lifecycle-offboarding-and-termination-automated-offboarding-processes
title: Automated Offboarding processes
canonical_path: knowledge/user-lifecycle/offboarding-and-termination/automated-offboarding-processes.md
summary: Follow identical steps for the two <COLLABORATION_PLATFORM> domains by opening an Incognito window and navigating to <INTERNAL_URL> and entering either <TEAM_NAME> or @<COMPANY_NAME> test.com credentials to gain access to...
type: offboarding
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Automated Offboarding processes
team: Identity and Access
systems:
- <HR_SYSTEM>
services:
- Offboarding
tags:
- offboarding
created: '2026-02-17'
updated: '2026-02-18'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: identity_admins
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
related_articles:
- kb-user-lifecycle-offboarding-and-termination-index
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

## Automated steps (reference)

> INFO: The remaining steps are automated and no work should be necessary to complete them

### <COLLABORATION_PLATFORM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Enter:
  1. **Search:** [Name of to-be-terminated user]
3. Click **[Name of to-be-terminated user]**

1. Click **security**

1. Click **Sign-in Cookies**

1. Click **RESET**

1. Click **SUSPEND USER**

1. Click **CHANGE ORGANIZATIONAL UNIT**

1. Click **Terminations** , then **CONTINUE**

Follow identical steps for the two <COLLABORATION_PLATFORM> domains by opening an Incognito window and navigating to [<INTERNAL_URL>](<INTERNAL_URL>) and entering either <TEAM_NAME> or <EMAIL_ADDRESS> credentials to gain access to their respective <COLLABORATION_PLATFORM> admin portals.

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click **Mobile Devices**
3. **Search:** [The name of the to-be-terminated user]
  1. Press **Enter/Return**
4. Click the **three dots**
5. Click **WIPE ACCOUNT**

### <ENDPOINT_MANAGEMENT_PLATFORM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Click **Computers**

1. Click the **user’s computer** in the search results

1. Click **Management**
2. Click **Lock Computer**

### <TICKETING_SYSTEM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Enter:
  1. **Search for people and teams:** [Name of the to-be-terminated user]
    2. Click the **user’s name**

1. Click **the three dots**
2. Click **Manage access**

1. Click the **switch**

### <PRODUCTIVITY_PLATFORM>

1. Navigate to: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Enter:
  1. **Search:** [Name of the to-be-terminated user]

1. Click the **user’s row**

1. Click **Block sign-in**
2. Click **Reset password**
