---
id: kb-assets-audits-and-recordkeeping-quarterly-finance-asset-review-it-helpdesk-procedure
title: "Quarterly Finance Asset Review \u2013 IT Helpdesk Procedure"
canonical_path: knowledge/assets/audits-and-recordkeeping/quarterly-finance-asset-review-it-helpdesk-procedure.md
summary: Each quarter Finance requests IT to confirm asset utilization, identify any items ready for disposal, and highlight assets that Finance still lists as active but are already retired in IT. This page defines how...
type: asset
status: active
owner: service_owner
source_type: imported
source_system: knowledge_portal_export
source_title: "Quarterly Finance Asset Review \u2013 IT Helpdesk Procedure"
team: Workplace Engineering
systems:
- <ASSET_MANAGEMENT_SYSTEM>
- <TICKETING_SYSTEM>
services:
- Endpoint Provisioning
tags:
- endpoint
- service-desk
created: '2025-11-05'
updated: '2025-11-06'
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
- kb-assets-audits-and-recordkeeping-index
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

Each quarter Finance requests IT to confirm asset utilization, identify any items ready for disposal, and highlight assets that Finance still lists as active but are already retired in IT. This page defines how Helpdesk completes the review using a synced Inventory Snapshot and presents results through the Finance Audit Tracker interface.

# Scope

- All IT-owned device assets included in Finance’s quarterly workbook
- Infrastructure and AV items that may not be tracked by serial (handled as “remain in use” unless Infra says otherwise)
- Lost/Stolen handling via write-off (not disposal)

## Notes about the Finance File

- Sheet/tab names and numbering change each quarter. Do not rely on “Tab 2a/2c”.
- Work by category:

1. Previously Reviewed / Fully Depreciated (from prior quarter’s inquiry)
2. Newly Fully Depreciated (this quarter)
3. Active / Depreciating (Finance’s current active list)

## Systems and Data Sources

- <COLLABORATION_PLATFORM> Sheets – to open/clean Finance’s workbook
- <ASSET_MANAGEMENT_SYSTEM> – Finance Audit Tracker base:

– Inventory Snapshot (Synced) ← already synced from <COMPANY_NAME> IT (filtered view) – Review tables you import each quarter from the Finance workbook – Unified Interface for presentation

- <COMPANY_NAME> IT base – source of truth; Inventory view is the sync source
- <MESSAGING_PLATFORM>/<TICKETING_SYSTEM>/Email – for sending Finance the summary and interface link

### Required Data

#### Finance lists (each):

- Asset ID (or Finance Asset ID/FAM ID if present)
- Name / Asset Type
- Asset Description
- Supplier
- Purchase Date
- Quantity

#### Inventory Snapshot (Synced):

- Serial Number (if available), Model, Device Status, Country
- Optional but helpful: Assignee, Last Seen/MDM timestamp
- Status values expected: Deployed (in use), Pending Decommission, Decommissioned, Recycled, Lost, Stolen

#### STATUS → RECOMMENDATION MAPPING

- Deployed → Remain In Use
- Pending Decommission → Ready for Disposal
- Decommissioned or Recycled → Already Retired (reconcile Finance ledger)
- Lost or Stolen → Write-Off (handle via loss process; exclude from disposal)
- Unknown/Not tracked by serial (infra/AV projects) → Remain In Use unless Infra says otherwise

---

# Process

1. PREPARE THE FINANCE FILE (<COLLABORATION_PLATFORM> spreadsheet) a. Open the Finance workbook in <COLLABORATION_PLATFORM> Sheets. b. Identify the three lists by content (titles vary each quarter): – List A: Previously Reviewed / Fully Depreciated (from last quarter’s inquiry) – List B: Newly Fully Depreciated (this quarter) – List C: Active / Depreciating (current active items in Finance) c. For each list, remove non-IT items (e.g., Facilities, Leaseholds), “Total” rows, repeated headers. d. Confirm the columns listed in “DATA YOU NEED IN EACH TABLE”. e. Download each cleaned list as CSV: – Previously_Reviewed.csv – Newly_Fully_Depreciated.csv – Active_Assets.csv
2. CONFIRM THE INVENTORY SNAPSHOT (SYNCED) a. In Finance Audit Tracker, ensure the “Inventory Snapshot (Synced)” table is up to date: – It should be a synced view from <COMPANY_NAME> IT → Inventory, filtered to include Deployed, Pending Decommission, Decommissioned, Recycled (and Lost/Stolen if you track them). – If the sync is manual, click refresh. If it’s automatic, confirm the last refresh time shows today.
3. IMPORT THE FINANCE LISTS INTO FINANCE AUDIT TRACKER a. Import the three CSVs as new tables: – Finance – Previously Reviewed – Finance – Newly Fully Depreciated – Finance – Active Assets b. Standardize field names to: Asset ID, Name, Asset Description, Supplier, Purchase Date, Quantity. c. Add these helper fields to each Finance table: – Family (single line text; optional grouping label like “Mac laptop Pro”, “Printer”, “AV/Conference”) – Link to Inventory (link to “Inventory Snapshot (Synced)”) – Device Status (lookup from the linked Inventory) – Country (lookup) – Recommendation (single line text; use the mapping above)
4. LINK FINANCE RECORDS TO INVENTORY a. Attempt the link in this order: – If both sides have a common ID (rare): link by Asset ID. – If the Finance description includes a serial number: link by Serial Number. – Otherwise link at the model/family level as supporting evidence (do not “explode” multi-quantity rows). b. For multi-quantity Finance rows, do not duplicate the Finance record. Instead: – Add “Inventory Match Count” (rollup of linked Inventory records → COUNT(values)). – Add a “Reconciliation” formula: {Inventory Match Count} & " of " & {Quantity}. – This gives Finance confidence without creating hundreds of duplicate rows.
5. CLASSIFY RECOMMENDATIONS (FAST) Option A (manual but quick): – Set Recommendation using the Status → Recommendation mapping. Option B (preferred): – Create a formula field “Recommendation” that evaluates the Inventory Device Status: IF({Device Status}="Pending Decommission","Ready for Disposal", IF(OR({Device Status}="Decommissioned",{Device Status}="Recycled"),"Already Retired (reconcile Finance)", IF({Device Status}="Deployed","Remain In Use", IF(OR({Device Status}="Lost",{Device Status}="Stolen"),"Write-Off (Lost/Stolen)","Review with Infra Team")))) ) – For infra/AV project purchases with no serial tracking, set Recommendation to “Remain In Use – Infra/AV” unless Infra advises otherwise.
6. REVIEW AND VERIFY a. Previously Reviewed list: – Expect most infra/AV items to remain in use; confirm no unexpected Pending/Decommissioned statuses. b. Newly Fully Depreciated list: – Flag “Ready for Disposal” only when Inventory shows Pending Decommission. – Infra/AV or printer lines without device tracking typically remain in use. c. Active list: – Produce two outputs for Finance:
  1. Items “Ready for Disposal” (Inventory shows Pending Decommission)
    2. Items “Already Retired” in Inventory (Decommissioned/Recycled) but still counted as Active by Finance → request ledger cleanup
7. UPDATE THE INTERFACE (ONE PAGE) a. Open the unified Interface in Finance Audit Tracker (single page, all components). b. Show: – Metric cards (counts): Reviewed total, Ready for Disposal, Already Retired, Remain In Use – Charts: counts by Recommendation; counts by Family – Unified grid: all Finance review records (Previously Reviewed + Newly FD + Active snippets if you include them), grouped by Recommendation or Source c. Add a short notes section with this cycle’s key takeaways. d. Share a read-only link with Finance.
8. SEND FINANCE THE SUMMARY Provide a short summary in the ticket/email: • Previously reviewed items: remain in use (no changes) unless noted • Newly fully depreciated items: ready for disposal only where Inventory shows Pending Decommission; otherwise remain in use • Active list: X devices ready for disposal (Pending Decommission) and Y devices already retired in IT (reconcile Finance active ledger) Include the <ASSET_MANAGEMENT_SYSTEM> interface link and attach CSV exports if requested.
9. ARCHIVE FOR NEXT QUARTER a. Add a “Quarter” single-select to all Finance tables (e.g., Q1 FY2026) and stamp it. b. Duplicate the three imported tables to an “Archive” section or copy records to an “Archive” table. c. The Inventory Snapshot remains synced; no change needed.

---

# Quality Checks (DO THESE BEFORE SENDING)

- Inventory Snapshot (Synced) shows today’s refresh time.
- Recommendation counts look sensible (e.g., infra/AV lines not incorrectly flagged “Ready for Disposal”).
- Lost/Stolen are excluded from disposal and noted for write-off.
- Reconciliation column shows sensible ratios for high-quantity Finance rows (e.g., “23 of 25”).
- The interface link opens in read-only for Finance.

# Troubleshooting

- CSV won’t import or shows one column: paste to <COLLABORATION_PLATFORM> Sheets → File > Download > CSV → import that file.
- Mismatched totals between Finance and Inventory: check whether Finance rows group multiple devices; use the Reconciliation count rather than forcing 1:1 linking.
- Infra/AV items missing in Inventory: treat as “Remain In Use – Infra/AV” unless Infra instructs otherwise.
- Device Status values inconsistent: normalize via a small single-select map (Deployed, Pending Decommission, Decommissioned, Recycled, Lost, Stolen).

## Outstanding improvement tasks (WHEN READY)

- Add a “Finance Raw Uploads” table to drop the workbook as-is; use a small automation to route rows into the three lists by keywords.
- Add a formula-based Recommendation field everywhere to remove manual tagging.
- Add an AI summary block in the interface with a “Copy summary” button for the Finance ticket.
