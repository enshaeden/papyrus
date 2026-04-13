# Operator Web UI

This reference records the stable server-rendered web UI contract for Papyrus. It is for maintainers working on the web surface, not for operator step-by-step execution.

## Purpose

- The web UI is a thin role-scoped surface over shared application services.
- Route handlers read request state, call application queries or commands, and hand structured data to presenters.
- Presenters and templates own page layout, surface composition, and reusable components.
- Routes should not emit HTML fragments or re-derive governed meaning from raw state fields.

## Shared UI Contract

- Stable route groups are:
  - Reader: `/reader/*`
  - Operator: `/operator/*`
  - Admin: `/admin/*`
- Production UI must not expose an actor switcher or rely on a shared actor shell.
- Demo or development overlays may still map local actor IDs onto roles, but they are not part of the shipped route contract.

- The shared component canon is:
  - one shared surface partial with two roles:
    - flat `content-section` for primary reading and composition
    - bordered `context-panel` for right-rail metadata and operational context only
  - one summary strip
  - badges
  - decision cells and decision cards
  - tables
  - filter bars
  - action bars
  - empty states
  - metadata lists
  - form field controls
- Primary content should read through text, spacing, and dividers rather than stacked cards or softened panels.
- Non-critical surfaces should not carry visible containment. Backgrounds, borders, and radius are reserved for right-rail context panels, selected table rows, and explicit warning or error states.
- Governed, status, audit, citation, relationship, validation, and support surfaces should be flattened unless they are serving one of those explicitly contained roles.
- Projection-backed posture remains the source of UI meaning:
  - `ui_projection.state`
  - `ui_projection.use_guidance`
  - action descriptors
  - workflow projections
  - acknowledgement payloads
- Templates may present those contracts differently by surface, but should not recreate policy rules or fallback copy from raw lifecycle aliases.

## Stable HTML Hooks

Critical HTML must expose semantic hooks that survive copy edits and page simplification.

- `data-surface` identifies the page or panel work area.
- `data-component` identifies reusable UI primitives such as surface panels, summary strips, tables, badges, decision cards, and form fields.
- `data-action-id` identifies governed actions and other critical affordances.

Tests should assert those hooks plus structured contract payload behavior instead of exact headings, counts, or prose.

## Shell And Layout Rules

- Shell variants are explicit:
  - `normal` for navigation and browsing surfaces
  - `focus` for intentionally reduced-navigation work, not guided drafting
  - `minimal` for one-step decisions and system pages
- Guided drafting uses the `normal` shell. Sidebar navigation and the topbar role label remain visible while the operator works through guided sections.
- The global search field occupies the centered topbar slot. Identity and shell controls must not shift it off center.
- The right rail is optional and should render only when the page has actionable contextual support.
- The sidebar is a flat grouped list, not a stack of card containers.
- The left rail and topbar role label come from `src/papyrus/interfaces/web/experience.py`, not page-local duplication.
- There is no production actor-selection control and no separate page-header actor banner contract.
- Page headers are opt-in and should include only the elements the presenter asks for.
- Page-local role, status, and action affordances should not render as chips, pills, or soft cards; they should read as text with restrained accent cues.
- Density scales by role:
  - reader surfaces stay lowest density
  - operator surfaces stay medium density
  - admin governance surfaces use denser tables and selected-item context rails
- Admin governance screens should prefer table-first layouts with deterministic URL-driven selection state in the right rail.

## Surface Ownership Map

### Home

- `Home Launch Block`
  - `data-component`: `home-launch-block`
  - owner file: `src/papyrus/interfaces/web/presenters/home_launch_block_presenter.py`
  - upstream data source: `papyrus.application.read_models.home_dashboard`
  - CSS location: `src/papyrus/interfaces/web/static/css/home.css`
  - test location: `tests/test_web_home_launch_block_presenter.py`
- `Home Activity Block`
  - `data-component`: `home-activity-block`
  - owner file: `src/papyrus/interfaces/web/presenters/home_activity_block_presenter.py`
  - upstream data source: `papyrus.application.read_models.home_dashboard`
  - CSS location: `src/papyrus/interfaces/web/static/css/home.css`
  - test location: `tests/test_web_home_activity_block_presenter.py`

### Read

- `Read Filter Bar`
  - `data-component`: `read-filter-bar`
  - owner file: `src/papyrus/interfaces/web/presenters/read_filter_bar_presenter.py`
  - upstream data source: role-scoped read-route query/filter state
  - CSS location: `src/papyrus/interfaces/web/static/css/read.css`
  - test location: `tests/test_web_read_queue_presenters.py`
- `Read Result Card` and `Read Results Table`
  - `data-component`: `read-result-card`, `read-results-table`
  - owner file: `src/papyrus/interfaces/web/presenters/read_results_presenter.py`
  - upstream data source: queue items plus `ui_projection.use_guidance`
  - CSS location: `src/papyrus/interfaces/web/static/css/read.css`
  - test location: `tests/test_web_read_queue_presenters.py`
- `Read Selected Context`
  - `data-component`: `read-selected-context`
  - owner file: `src/papyrus/interfaces/web/presenters/read_selected_context_presenter.py`
  - upstream data source: selected queue item
  - CSS location: `src/papyrus/interfaces/web/static/css/read.css`
  - test location: `tests/test_web_read_queue_presenters.py`

### Object Detail

- Object detail title, summary, and primary actions render through the shared page header in `src/papyrus/interfaces/web/rendering.py`.
- `Article Section`
  - `data-component`: `article-section`
  - owner file: `src/papyrus/interfaces/web/presenters/article_section_presenter.py`
  - upstream data source: `papyrus.interfaces.web.view_models.article_projection`
  - CSS location: `src/papyrus/interfaces/web/static/css/article.css`
  - test location: `tests/test_web_object_detail_presenters.py`
- `Article Context Panel`
  - `data-component`: `article-context-panel`
  - owner file: `src/papyrus/interfaces/web/presenters/article_context_panel_presenter.py`
  - upstream data source: `papyrus.interfaces.web.view_models.article_projection`
  - CSS location: `src/papyrus/interfaces/web/static/css/article.css`
  - test location: `tests/test_web_object_detail_presenters.py`

### Services

- `Service Map`
  - `data-component`: `service-map`
  - owner file: `src/papyrus/interfaces/web/presenters/service_map_presenter.py`
  - upstream data source: `/services` route payload
  - CSS location: `src/papyrus/interfaces/web/static/css/services.css`
  - test location: `tests/test_web_service_presenters.py`
- `Service Map Card`
  - `data-component`: `service-map-card`
  - owner file: `src/papyrus/interfaces/web/presenters/service_map_presenter.py`
  - upstream data source: service catalog rows
  - CSS location: `src/papyrus/interfaces/web/static/css/services.css`
  - test location: `tests/test_web_service_presenters.py`
- Service detail title, service facts, and primary actions render through the shared page header in `src/papyrus/interfaces/web/rendering.py`.
- `Service Pressure`
  - `data-component`: `service-pressure`
  - owner file: `src/papyrus/interfaces/web/presenters/service_pressure_presenter.py`
  - upstream data source: service posture summary
  - CSS location: `src/papyrus/interfaces/web/static/css/services.css`
  - test location: `tests/test_web_service_presenters.py`
- `Service Path`
  - `data-component`: `service-path`, `service-path-item`
  - owner file: `src/papyrus/interfaces/web/presenters/service_path_presenter.py`
  - upstream data source: linked service objects
  - CSS location: `src/papyrus/interfaces/web/static/css/services.css`
  - test location: `tests/test_web_service_presenters.py`

### Knowledge Health

- `Health Board`
  - `data-component`: `health-board`
  - owner file: `src/papyrus/interfaces/web/presenters/health_board_presenter.py`
  - upstream data source: trust dashboard queue payload
  - CSS location: `src/papyrus/interfaces/web/static/css/health.css`
  - test location: `tests/test_web_health_presenters.py`
- `Health Cleanup Board`
  - `data-component`: `health-cleanup-board`
  - owner file: `src/papyrus/interfaces/web/presenters/health_cleanup_board_presenter.py`
  - upstream data source: trust dashboard cleanup counts
  - CSS location: `src/papyrus/interfaces/web/static/css/health.css`
  - test location: `tests/test_web_health_presenters.py`
- `Health Validation Board`
  - `data-component`: `health-validation-board`
  - owner file: `src/papyrus/interfaces/web/presenters/health_validation_board_presenter.py`
  - upstream data source: trust dashboard validation posture
  - CSS location: `src/papyrus/interfaces/web/static/css/health.css`
  - test location: `tests/test_web_health_presenters.py`

### Review

- `Review Cleanup Strip`
  - `data-component`: `review-cleanup-strip`
  - owner file: `src/papyrus/interfaces/web/presenters/review_cleanup_strip_presenter.py`
  - upstream data source: review queue cleanup counts
  - CSS location: `src/papyrus/interfaces/web/static/css/review.css`
  - test location: `tests/test_web_review_presenters.py`
- `Review Lane`
  - `data-component`: `review-lane`
  - owner file: `src/papyrus/interfaces/web/presenters/review_lane_presenter.py`
  - upstream data source: review queue lane items plus governed actions
  - CSS location: `src/papyrus/interfaces/web/static/css/review.css`
  - test location: `tests/test_web_review_presenters.py`

### Activity

- `Activity Filter Bar`
  - `data-component`: `activity-filter-bar`
  - owner file: `src/papyrus/interfaces/web/presenters/activity_filter_bar_presenter.py`
  - upstream data source: `/operator/review/activity` and `/admin/audit` filter state
  - CSS location: `src/papyrus/interfaces/web/static/css/activity.css`
  - test location: `tests/test_web_activity_presenters.py`
- `Activity Event`
  - `data-component`: `activity-event`
  - owner file: `src/papyrus/interfaces/web/presenters/activity_event_list_presenter.py`
  - upstream data source: structured activity events
  - CSS location: `src/papyrus/interfaces/web/static/css/activity.css`
  - test location: `tests/test_web_activity_presenters.py`
- `Activity Audit Log`
  - `data-component`: `activity-audit-log`
  - owner file: `src/papyrus/interfaces/web/presenters/activity_audit_log_presenter.py`
  - upstream data source: raw audit events
  - CSS location: `src/papyrus/interfaces/web/static/css/activity.css`
  - test location: `tests/test_web_activity_presenters.py`
- `Activity Validation Log`
  - `data-component`: `activity-validation-log`
  - owner file: `src/papyrus/interfaces/web/presenters/activity_validation_log_presenter.py`
  - upstream data source: validation run summaries
  - CSS location: `src/papyrus/interfaces/web/static/css/activity.css`
  - test location: `tests/test_web_activity_presenters.py`

### Revision History

- `Revision History Table`
  - `data-component`: `revision-history-table`
  - owner file: `src/papyrus/interfaces/web/presenters/revision_history_table_presenter.py`
  - upstream data source: object revision history payload
  - CSS location: `src/papyrus/interfaces/web/static/css/revision.css`
  - test location: `tests/test_web_revision_presenters.py`
- `Revision Audit Sequence`
  - `data-component`: `revision-audit-sequence`
  - owner file: `src/papyrus/interfaces/web/presenters/revision_audit_sequence_presenter.py`
  - upstream data source: object audit events
  - CSS location: `src/papyrus/interfaces/web/static/css/revision.css`
  - test location: `tests/test_web_revision_presenters.py`
- `Revision Comparison Cues`
  - `data-component`: `revision-comparison-cues`
  - owner file: `src/papyrus/interfaces/web/presenters/revision_comparison_cues_presenter.py`
  - upstream data source: presenter-owned comparison guidance
  - CSS location: `src/papyrus/interfaces/web/static/css/revision.css`
  - test location: `tests/test_web_revision_presenters.py`

### Impact

- `Impact Summary`
  - `data-component`: `impact-summary`
  - owner file: `src/papyrus/interfaces/web/presenters/impact_summary_presenter.py`
  - upstream data source: impact route payload counts
  - CSS location: `src/papyrus/interfaces/web/static/css/impact.css`
  - test location: `tests/test_web_impact_presenters.py`
- `Impact Trace`
  - `data-component`: `impact-trace`
  - owner file: `src/papyrus/interfaces/web/presenters/impact_trace_presenter.py`
  - upstream data source: impacted object list and URL selection state
  - CSS location: `src/papyrus/interfaces/web/static/css/impact.css`
  - test location: `tests/test_web_impact_presenters.py`
- `Impact Profile`
  - `data-component`: `impact-profile`
  - owner file: `src/papyrus/interfaces/web/presenters/impact_profile_presenter.py`
  - upstream data source: current impact summary for object or service
  - CSS location: `src/papyrus/interfaces/web/static/css/impact.css`
  - test location: `tests/test_web_impact_presenters.py`
- `Impact Selected Item`
  - `data-component`: `impact-selected-item`
  - owner file: `src/papyrus/interfaces/web/presenters/impact_selected_item_presenter.py`
  - upstream data source: currently selected impacted object
  - CSS location: `src/papyrus/interfaces/web/static/css/impact.css`
  - test location: `tests/test_web_impact_presenters.py`
- `Impact Event Log`
  - `data-component`: `impact-event-log`
  - owner file: `src/papyrus/interfaces/web/presenters/impact_event_log_presenter.py`
  - upstream data source: impact route recent events
  - CSS location: `src/papyrus/interfaces/web/static/css/impact.css`
  - test location: `tests/test_web_impact_presenters.py`
- `Impact Relationship List`
  - `data-component`: `impact-relationship-list`
  - owner file: `src/papyrus/interfaces/web/presenters/impact_relationship_list_presenter.py`
  - upstream data source: inbound relationships, citation dependents, and related services
  - CSS location: `src/papyrus/interfaces/web/static/css/impact.css`
  - test location: `tests/test_web_impact_presenters.py`

### Ingest

- `Ingest Upload`
  - `data-component`: `ingest-upload`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_upload_presenter.py`
  - upstream data source: import form state and validation errors
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest List`
  - `data-component`: `ingest-list`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_list_presenter.py`
  - upstream data source: import workbench listing payload
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Progress`
  - `data-component`: `ingest-progress`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_progress_presenter.py`
  - upstream data source: ingestion detail lifecycle state
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Stage Board`
  - `data-component`: `ingest-stage-board`, `ingest-stage-card`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_stage_board_presenter.py`
  - upstream data source: normalized content, classification, and mapping summary
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Parsed Content`
  - `data-component`: `ingest-parsed-content`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_parsed_content_presenter.py`
  - upstream data source: normalized parsed-content summary
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Parser Assessment`
  - `data-component`: `ingest-parser-assessment`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_parser_assessment_presenter.py`
  - upstream data source: parser warnings and extraction quality
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Mapping Table`
  - `data-component`: `ingest-mapping-table`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_mapping_table_presenter.py`
  - upstream data source: mapping result sections
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Mapping Gaps`
  - `data-component`: `ingest-mapping-gaps`, `ingest-mapping-gap`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_mapping_gaps_presenter.py`
  - upstream data source: mapping result gaps and conflicts
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`
- `Ingest Convert Form`
  - `data-component`: `ingest-convert-form`
  - owner file: `src/papyrus/interfaces/web/presenters/ingest_convert_form_presenter.py`
  - upstream data source: mapping review detail, taxonomy choices, and conversion errors
  - CSS location: `src/papyrus/interfaces/web/static/css/ingest.css`
  - test location: `tests/test_web_ingest_presenters.py`

## Web Authoring Route Contract

- `POST /operator/write/object/{object_id}/start` is the explicit guided authoring start route. It may reuse a compatible draft or create a new one through application-owned policy.
- `GET /operator/write/object/{object_id}` is load-only:
  - with `revision_id`, it loads that revision context only
  - without `revision_id`, it may load only an existing compatible draft
  - if no compatible draft exists, it returns `400 Bad Request` with an operator-facing reason and does not redirect implicitly
- `/operator/write/new` creates the object shell and eagerly starts the first draft before redirecting to the guided page with a concrete `revision_id`.
- `GET /operator/write/citations/search` and `GET /operator/write/objects/search` are operator-only JSON helpers for guided authoring widgets.
- Presenters should link to an existing guided revision only when they already have a concrete `revision_id`. When a draft may need to be created or reused, presenters should use the explicit POST start route instead of GET-side effects.

## Current Boundaries

- Page presenters now assemble browser-visible surfaces from explicit owner files for Home, Read, object detail, services, knowledge health, review, activity, revision history, impact, and ingest.
- Shared components still provide low-level building blocks such as badges, decision cells, and governed panels, but surface-specific copy and internal markup now live in the owning presenter for that visible component.
- `papyrus.application.read_models.home_dashboard` now supplies role-scoped dashboard data rather than Home-specific launch or activity structures.
- Object-detail section composition belongs to the web view-model layer, not `papyrus.application.read_models`.
- No authentication or CSRF layer is introduced in this interface; the surface remains intended for local or otherwise trusted operator environments.

## Testing And Maintenance

- Prefer presenter tests and WSGI surface tests over copy-pinned HTML assertions.
- When a new visible surface is introduced, give it an explicit owner, `data-component`, CSS scope, and localized test coverage before considering abstraction.
- Shared helpers should stay low-level. Do not move browser-visible rows, tiles, badges, or copy back into broad read models or page assemblers.
