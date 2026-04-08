---
id: kb-applications-business-apps-messaging-platform-creating-automated-messaging-platform-groups-channels-via-identity-provider
title: Creating automated <MESSAGING_PLATFORM> Groups (+channels) via <IDENTITY_PROVIDER>
canonical_path: knowledge/applications/business-apps/messaging-platform/creating-automated-messaging-platform-groups-channels-via-identity-provider.md
summary: You should now have a <MESSAGING_PLATFORM> User group that automatically adds users to a specific
  channel when added to the group.
knowledge_object_type: runbook
legacy_article_type: access
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Creating automated <MESSAGING_PLATFORM> Groups (+channels) via <IDENTITY_PROVIDER>
team: Identity and Access
systems:
- <IDENTITY_PROVIDER>
tags:
- account
- authentication
created: '2025-10-29'
updated: '2025-10-29'
last_reviewed: '2026-04-07'
review_cadence: after_change
audience: identity_admins
related_services:
- Identity
- Collaboration
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
  source_ref: migration/import-manifest.yml
  note: Sanitized source record.
  excerpt: null
  captured_at: null
  validity_status: verified
  integrity_hash: null
related_object_ids:
- kb-applications-business-apps-messaging-platform-index
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Identity
- Collaboration
related_articles:
- kb-applications-business-apps-messaging-platform-index
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
---

# **Instructions**

### **Create the <MESSAGING_PLATFORM> User Group and Channel**

1. If necessary create the new <MESSAGING_PLATFORM> Channel the users will be automatically added to or removed from: <MESSAGING_PLATFORM> Admin > Manage Channels
  1. [<INTERNAL_URL>](<INTERNAL_URL>)
2. In the <MESSAGING_PLATFORM> Admin > User Group area, create a user Group: [<INTERNAL_URL>](<INTERNAL_URL>)
  1. In the last step of the user group it will ask you if you’d like to add the group to a default channel, use the group you created (or already know) from Step 1

You should now have a <MESSAGING_PLATFORM> User group that automatically adds users to a specific channel when added to the group.

### **Create the <IDENTITY_PROVIDER> Group + Rule**

1. In <IDENTITY_PROVIDER> admin > Groups, create a new group with the correct naming convention (i.e. **Team - ABC** , **Department - ABC** , etc): [<INTERNAL_URL>](<INTERNAL_URL>)
2. In <IDENTITY_PROVIDER> admin > Groups > Rules, create a rule that adds your users to your new group: [<INTERNAL_URL>](<INTERNAL_URL>)

A few examples:

*Basic group:*

*Basic group narrowed by country code:*

*Contractors - Cognizant*

1. You may ‘Save’ a Rule before anything takes effect so please make sure to save then go back in to test a few users you expect to be members or non-members of the group
2. Click ‘Actions’ to the right of the Rule name, then ‘Activate’ to populate your new Group
3. Confirm it’s correct by then clicking into the group and spot checking names and amount of users

### **Create the <IDENTITY_PROVIDER> > <MESSAGING_PLATFORM> connection via Push Group**

1. Head to the <MESSAGING_PLATFORM> app in <IDENTITY_PROVIDER> and select the ‘Push Groups’ tab: [<INTERNAL_URL>](<INTERNAL_URL>)
2. Select the ‘Push Groups’ button then select ‘find groups by name’
3. Start by entering the name of your <IDENTITY_PROVIDER> group that was created (and populated) above
4. On the right, under ‘Match result & push action’ you can then select ‘Link Group’ and search for your newly created **<MESSAGING_PLATFORM>** group (from the first steps of this walkthrough), though it will likely not find it, if so instead select ‘Create Group’ and type in the exact name of the **<MESSAGING_PLATFORM>** group (from the first steps of this walkthrough)
5. Click ‘Save’
6. First confirm your <MESSAGING_PLATFORM> Group has the correct amount of users: [<INTERNAL_URL>](<INTERNAL_URL>)
7. Then confirm your <MESSAGING_PLATFORM> Channel has the correct amount of users: [<INTERNAL_URL>](<INTERNAL_URL>)
