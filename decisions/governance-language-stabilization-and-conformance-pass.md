# Governance Language Stabilization And Conformance Pass

Scope: Shared-route runtime behavior, remaining migration drift, outward contract cleanup, browser validation, and post-cutover follow-up.

## Runtime conformance outcome

This pass closed highest-risk shared-route drift:

- Request bootstrap now resolves request identity before route handling through `_resolve_request_identity`. `src/papyrus/interfaces/web/app.py:182-183`
- Root landing now keys off request role instead of app-global runtime default. `src/papyrus/interfaces/web/routes/home.py:7-10`
- Shared-route access now honors role hierarchy through `role_meets_minimum` instead of exact-role matching. `src/papyrus/interfaces/web/experience.py:321-327`
- Shared Admin access now reaches `/write/new`, `/import`, `/write/citations/search`, and `/write/objects/search` through canonical Operator-owned routes. `src/papyrus/interfaces/web/routes/write_search.py:13-63`
- Admin audit path is reduced to redirect compatibility instead of duplicate page ownership. `src/papyrus/interfaces/web/routes/manage.py:462-468`
- Ingest mapping review now renders canonical field name `object_lifecycle_state`. `src/papyrus/interfaces/web/routes/ingest.py:108-156`, `src/papyrus/interfaces/web/presenters/ingest_presenter.py:751-755`
- Role-shaped URL helper shims that no longer changed output were removed from canonical helper signatures. `src/papyrus/interfaces/web/urls.py:27-135`

## Remaining drift and weak spots

### 1. Identity resolution drift remains partial

- Contract violated:
  `decisions/runtime-role-context-and-access-resolution.md` requires request-scoped resolution order that can evolve to session or authenticated identity.
- File and line:
  `src/papyrus/interfaces/web/app.py:158-183`
- Runtime symptom:
  Request identity resolves once per request, but still only from configured local defaults derived from actor-to-role mapping.
- Risk:
  Production authority model still not separated from local-runtime bootstrap. Future auth work can drift if code keeps treating config defaults as final authority.
- Fix direction:
  Introduce dedicated request access-context resolver with dev-session override path, auth/session slot, and explicit `role_source` branching beyond `config_default`.

### 2. Dev actor bridge still outward-facing

- Contract violated:
  Dev-only switching may remain, but must not act like permanent production authority.
- File and line:
  `src/papyrus/application/role_visibility.py:16-35`
  `src/papyrus/domain/actor.py:21-70`
  `src/papyrus/interfaces/local_runtime_cli.py:83-84`
- Runtime symptom:
  `local.reviewer` and `local.manager` still exist as first-class actor IDs and default-role fallbacks.
- Risk:
  External scripts and future auth work may bind to migration-era actor labels instead of canonical roles.
- Fix direction:
  Keep until local-runtime auth decision exists. Then move dev switching behind explicit local session mechanism and remove outward actor-label dependence from defaults.

### 3. Redirect compatibility route still present for audit

- Contract violated:
  Migration rules say duplicated route ownership should not remain once shared canonical routes exist.
- File and line:
  `src/papyrus/interfaces/web/routes/manage.py:462-468`
- Runtime symptom:
  `/admin/audit` still exists as outward compatibility entrypoint, even though `/review/activity` is canonical shared route.
- Risk:
  Bookmarks and automation may keep anchoring to admin-shaped path. Shared-route ownership stays less obvious than it should be.
- Fix direction:
  Remove after external migration window and point docs, tests, automation, and bookmarks at `/review/activity`.

### 4. Legacy ingest field alias still accepted

- Contract violated:
  Canonical outward field is `object_lifecycle_state`.
- File and line:
  `src/papyrus/interfaces/web/routes/ingest.py:118-146`
- Runtime symptom:
  POST handling still accepts retired form field `status` as compatibility fallback.
- Risk:
  External automation can keep sending stale payload names and delay contract cleanup.
- Fix direction:
  Keep through external migration window only. Remove fallback after browser flows, scripts, and automation stop sending `status`.

### 5. CLI aliases still expose stale outward contracts

- Contract violated:
  Cutover intent is canonical governance language and canonical route/workflow naming.
- File and line:
  `src/papyrus/interfaces/cli.py:307-330`
  `src/papyrus/interfaces/cli.py:949-950`
  `src/papyrus/interfaces/cli.py:1032-1046`
- Runtime symptom:
  CLI still accepts `health` as alias for `dashboard` and `activity` as alias for `events`.
- Risk:
  Automation and operator habits keep depending on retired terms.
- Fix direction:
  Keep during migration notice period. Remove aliases after external migration checklist completes.

### 6. Legacy markdown normalization remains active

- Contract violated:
  Migration shims should remain only where source migration still depends on them.
- File and line:
  `src/papyrus/infrastructure/markdown/parser.py:225-354`
- Runtime symptom:
  Parser still emits legacy notes, legacy section defaults, legacy citation conversion, and explicit rename warning for `status -> object_lifecycle_state`.
- Risk:
  Old content shapes can continue to flow through import paths and hide missing canonical field upgrades.
- Fix direction:
  Keep only while source-workspace migration still needs it. Remove field-normalization bridges after external content corpus finishes canonical rewrite.

### 7. Advanced blueprint scope still unresolved

- Contract violated:
  Product scope for active object types is not clearly owned by a dedicated decision record.
- File and line:
  `src/papyrus/domain/blueprints_seed.py:498-625`
  `src/papyrus/interfaces/web/forms/revision_forms.py:328-342`
  `src/papyrus/interfaces/web/forms/revision_forms.py:424-439`
  `tests/interfaces/test_write_ui.py:67-78`
- Runtime symptom:
  `policy` and `system_design` are active in domain blueprints, forms, ingest, and validation, but hidden from primary write route and reader route expectations.
- Risk:
  UI and workflow work can drift into accidental partial support.
- Fix direction:
  Record explicit scope decision before any more web authoring or reader-surface expansion for advanced blueprint types.

## External migration checklist

### High urgency

- Update bookmarks, links, scripts, and browser tests away from retired role-shaped routes:
  legacy /operator/read path
  legacy /reader/object/{object_id} path
  legacy admin inspect path
  legacy /dashboard/oversight path
  legacy review queue path
  legacy /operator/import path
  legacy /operator/write/new path
  retired advanced write route copy
- Update all external ingest form automation from `status` to `object_lifecycle_state`.
- Update any schema consumers that still look for retired outward lifecycle labels:
  `revision_state`
  `draft_state`
  `approval_state`

### Medium urgency

- Update CLI automation from `health` to `dashboard`.
- Update CLI automation from `activity` to `events`.
- Replace outward dev actor defaults that still name:
  `local.reviewer`
  `local.manager`
- Confirm no external runbooks still reference removed migration scripts from the old migration pass.

### Low urgency

- Update browser and manual automation to target semantic hooks:
  `data-component`
  `data-action-id`
- Remove raw CSS-selector or text-selector probes when a semantic hook already exists.

## Compatibility-shim cleanup plan

### Keep

- Dev actor mapping in `src/papyrus/application/role_visibility.py:16-35`
  Rationale: Local runtime still needs synthetic actors until auth/session decision lands.
- Local actor registry and default-role bridge in `src/papyrus/domain/actor.py:21-70`
  Rationale: Same local-runtime bridge. Removal now would break current no-auth workflow.
- Markdown parser legacy normalization in `src/papyrus/infrastructure/markdown/parser.py:225-354`
  Rationale: Source migration still depends on canonicalization of older content shapes.

### Remove now

- Exact-role guard semantics in `src/papyrus/interfaces/web/experience.py`
  Status: removed in this pass.
- Role-ignored URL helper shims in `src/papyrus/interfaces/web/urls.py`
  Status: removed in this pass.
- Duplicate Admin audit page ownership
  Status: reduced in this pass to redirect-only compatibility at `src/papyrus/interfaces/web/routes/manage.py:462-468`.

### Remove after external migration

- `/admin/audit` redirect compatibility route in `src/papyrus/interfaces/web/routes/manage.py:462-468`
- Ingest `status` POST fallback in `src/papyrus/interfaces/web/routes/ingest.py:118-146`
- CLI aliases in `src/papyrus/interfaces/cli.py:307-330`, `src/papyrus/interfaces/cli.py:949-950`, `src/papyrus/interfaces/cli.py:1032-1046`
- Outward dev actor defaults in CLI and API entrypoints:
  `src/papyrus/interfaces/cli.py:365-584`
  `src/papyrus/interfaces/ingest_event_cli.py:58`
  `src/papyrus/interfaces/api.py:354`

## Decision and scope follow-ups

- Required decision record:
  `decisions/advanced-blueprint-product-scope.md`
- Decision questions:
  Whether `policy` and `system_design` are active operator product types now.
  Whether web authoring should expose them directly, keep them import-only, gate them to Admin, or defer them.
  Whether Reader surfaces should treat them as first-class read objects.
  Whether cleanup work may remove current advanced-blueprint bridges after migration.
