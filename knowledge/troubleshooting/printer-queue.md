---
id: kb-troubleshooting-printer-queue
title: Printer Troubleshooting
canonical_path: knowledge/troubleshooting/printer-queue.md
summary: Restore common office printing failures by checking queue state, consumables, and endpoint printer mappings.
type: troubleshooting
status: active
owner: service_owner
source_type: native
source_system: repository
source_title: Printer Troubleshooting
team: Service Desk
systems:
- <PRINTER_MANAGEMENT_PLATFORM>
- <TICKETING_SYSTEM>
services:
- Printing
tags:
- printer
- service-desk
created: 2026-04-07
updated: 2026-04-07
last_reviewed: 2026-04-07
review_cadence: quarterly
audience: service_desk
prerequisites:
- Ticket includes office location, printer name, and whether the issue affects one user or multiple users.
- Ability to view the print queue or confirm printer panel status.
steps:
- Confirm whether the issue affects a single workstation or all users sending jobs to the same printer.
- Check the printer panel for paper, toner, or jam alerts before changing workstation settings.
- Review the queue on the Print Server and clear only the stuck jobs associated with the incident.
- Re-add the shared printer on the affected workstation if the queue is healthy but the workstation mapping is corrupt.
- Escalate to facilities or the hardware vendor if the printer reports repeated hardware faults after the queue is clear.
verification:
- Test page prints successfully from the affected workstation.
- The print queue drains normally after the fix.
- Ticket notes capture whether the issue was queue, consumable, driver, or hardware related.
rollback:
- Reconnect the previous printer mapping if the replacement queue targets the wrong printer.
- Restore removed jobs from the original request source if they must be reprinted after queue cleanup.
related_articles:
- kb-troubleshooting-meeting-room-av-triage
replaced_by: null
retirement_reason: null
references:
- title: Printer asset label
  note: 'Record the printer asset label or serial number: <SERIAL_NUMBER>'
change_log:
- date: 2026-04-07
  summary: Initial seed article.
  author: seed_sanitization
---

## Notes

Avoid restarting the Print Server service during office hours unless multiple queues are impacted and the change has been approved.
