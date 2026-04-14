# Taxonomy Restoration For Runtime Validation

Status: Approved
Owner: Repository Governance
Scope: Controlled vocabulary values required by canonical knowledge content and runtime projection validation

## Purpose

Restore controlled taxonomy values that are already used by canonical knowledge content and by the repository contract so runtime validation, projection builds, and local startup remain aligned with the current product model.

## Decision

The following values remain valid and supported:

- `service_record` in `taxonomies/knowledge_object_types.yml`
- `Workplace Engineering` and `Identity and Access` in `taxonomies/teams.yml`
- `identity_admins` in `taxonomies/audiences.yml`
- `Printing` in `taxonomies/services.yml`
- `printer` in `taxonomies/tags.yml`

## Rationale

Canonical content under `knowledge/` still uses these values extensively, and `schemas/repository_policy.yml` plus `schemas/knowledge_objects/service_record.yml` still define `service_record` as part of the governed repository model.

Removing the vocabulary entries without a coordinated content migration created taxonomy drift that blocks:

- repository validation
- search projection builds
- local operator startup
- local demo runtime startup

Restoring the taxonomy values is the smallest correct change because it re-aligns the governing vocabularies with the currently authoritative content and schema contracts without weakening the validation gate.

## Tradeoffs

- This keeps legacy vocabulary in the taxonomy set a little longer.
- A future cleanup may still consolidate or rename these values, but that must happen as an explicit migration across schemas, taxonomies, canonical content, and runtime expectations.

## Operational impact

- `python3 scripts/validate.py` should no longer fail on these missing-value errors.
- `python3 scripts/run.py --operator` and `python3 scripts/run.py --demo` can rebuild projections again once validation is clean.
