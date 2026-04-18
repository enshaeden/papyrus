# Advanced Blueprint Product Scope

Status: Pending decision required before more web UI or workflow expansion.

## Purpose

This record must decide whether advanced blueprint types stay in active Papyrus product scope.

Advanced blueprint types in current repo state:

- `policy`
- `system_design`

## Current repo truth

- Domain blueprints are active.
  `src/papyrus/domain/blueprints_seed.py:498-625`
- Web revision forms and validation support these types.
  `src/papyrus/interfaces/web/forms/revision_forms.py:328-342`
  `src/papyrus/interfaces/web/forms/revision_forms.py:424-439`
  `src/papyrus/interfaces/web/forms/revision_forms.py:522-540`
  `src/papyrus/interfaces/web/forms/revision_forms.py:565-572`
- Ingest and integration tests cover these types.
  `tests/integration/test_ingestion_to_authoring.py:258-382`
- Primary web authoring route intentionally hides these types.
  `tests/interfaces/test_write_ui.py:67-78`

## Decision needed

This record must answer:

- Are `policy` and `system_design` active operator product types now?
- Is direct web authoring on primary write route in scope?
- Are these types import-only for now?
- Are these types Admin-gated instead of Operator-visible?
- Are Reader surfaces expected to expose them as first-class readable objects?
- May migration cleanup remove partial bridges if direct product scope is deferred?

## Guardrail until decided

Do not add more UI affordances, workflow branches, search affordances, or reader-surface composition for `policy` or `system_design` until this record is decided.

Do not remove existing ingest or validation support unless this record explicitly authorizes that cleanup.
