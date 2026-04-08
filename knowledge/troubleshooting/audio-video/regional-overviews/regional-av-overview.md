---
id: kb-troubleshooting-audio-video-regional-overviews-regional-av-overview
title: Regional AV Overview
canonical_path: knowledge/troubleshooting/audio-video/regional-overviews/regional-av-overview.md
summary: Cross-site orientation for the AV support footprint and the site-specific overview pages that define local room standards.
knowledge_object_type: known_error
legacy_article_type: troubleshooting
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: Regional AV Overview
team: Workplace Engineering
systems:
- <VIDEO_CONFERENCING_PLATFORM>
tags:
- av
- service-desk
created: '2025-11-21'
updated: '2025-11-21'
last_reviewed: '2026-04-07'
review_cadence: quarterly
audience: systems_admins
related_services:
- Collaboration
symptoms:
- Operators need to choose the correct site-specific AV baseline before applying maintenance, sweep, or room-support guidance.
scope: Use this page for regional orientation and site selection only. Follow the linked site-specific overview for room standards, automation labels, and local maintenance notes.
cause: AV operations differ by site layout, room mix, and automation labels; using the wrong site baseline can send operators to the wrong rooms, hardware expectations, or monthly sweep workflow.
diagnostic_checks:
- Confirm the office or region in scope before selecting a room-support article.
- Use the site-specific overview page to verify local room types, automation labels, and maintenance expectations.
- Escalate if the site does not match any of the maintained overview pages.
mitigations:
- Route the request to the correct site-specific overview before taking room-level action.
- Escalate to the owning team if the local AV footprint has drifted beyond the current overviews.
permanent_fix_status: unknown
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
- kb-troubleshooting-audio-video-regional-overviews-index
- kb-troubleshooting-audio-video-regional-overviews-office-site-a-av
- kb-troubleshooting-audio-video-regional-overviews-office-site-b-av
- kb-troubleshooting-audio-video-regional-overviews-office-site-c-av
prerequisites:
- Confirm the office or site in scope before selecting a child overview.
- Gather the room identifier, issue context, and maintenance objective before navigating to a site-specific page.
steps:
- Start with the site summary table below to identify the correct regional AV overview.
- Open the linked site-specific article and use that page for room-level maintenance or troubleshooting.
- Record any new site-level drift so the overview set can be updated without duplicating guidance.
verification:
- Operators can reach the correct site-specific AV page without ambiguity.
- Site-level automation labels, room mix expectations, and maintenance posture are captured in the child overviews instead of duplicated here.
rollback:
- Restore the previous overview structure from version control if the regional summary no longer reflects the maintained child pages.
- Escalate to the owning team if a site needs a new standalone overview rather than a regional summary update.
superseded_by: null
replaced_by: null
retirement_reason: null
services:
- Collaboration
related_articles:
- kb-troubleshooting-audio-video-regional-overviews-index
- kb-troubleshooting-audio-video-regional-overviews-office-site-a-av
- kb-troubleshooting-audio-video-regional-overviews-office-site-b-av
- kb-troubleshooting-audio-video-regional-overviews-office-site-c-av
references:
- title: <KNOWLEDGE_PORTAL> seed import manifest
  path: migration/import-manifest.yml
  note: Sanitized source record.
change_log:
- date: '2026-04-07'
  summary: Imported from <KNOWLEDGE_PORTAL> seed content.
  author: seed_sanitization
- date: '2026-04-07'
  summary: Reworked this page into a true regional overview to remove duplicated site-specific content.
  author: codex
---

## Regional Summary

Use this page to choose the correct site-specific AV baseline before running a room sweep, triaging an AV issue, or updating local maintenance expectations.

| Site | Primary Use | Site Overview |
| --- | --- | --- |
| <OFFICE_SITE_A> | Larger hybrid collaboration rooms and training spaces | [<OFFICE_SITE_A> AV](office-site-a-av.md) |
| <OFFICE_SITE_B> | Smaller collaboration rooms and lightweight meeting setups | [<OFFICE_SITE_B> AV](office-site-b-av.md) |
| <OFFICE_SITE_C> | Primary hub with the broadest room mix and monthly sweep baseline | [<OFFICE_SITE_C> AV](office-site-c-av.md) |

## How To Use This Overview

- Confirm the office or regional queue label in the request before opening a child page.
- Use the site-specific overview for room counts, equipment expectations, automation labels, and local maintenance notes.
- Capture any regional drift that affects multiple sites here, but keep room-level operational detail in the child pages.

## Cross-Site Rules

- Use a monthly sweep issue structure that is traceable in <TICKETING_SYSTEM>.
- Record room identifiers and notable hardware variance in ticket comments so site owners can reconcile local drift.
- Escalate any site that no longer matches its documented equipment mix instead of copy-editing another site's guidance into place.
