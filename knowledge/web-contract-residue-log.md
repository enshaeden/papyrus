# Web Contract Residue Log

Date: 2026-04-10

Purpose:
- Record the repository-wide residue searches required by the web contract repair plan.
- Note whether each match was removed or remains intentional.

## Search: dead actor-banner references

Pattern:
- `show_actor_banner`
- `has-actor-banner`
- `actor_banner_html`

Result:
- No matches under `src/`, `tests/`, `knowledge/`, `docs/`, or `README.md`.

Disposition:
- Removed completely.

## Search: frozen request mutation

Pattern:
- `object.__setattr__(request`
- `object.__setattr__`

Result:
- No matches under `src/` or `tests/`.

Disposition:
- Removed completely. Routed requests now use immutable copies with route params attached.

## Search: GET-based guided draft creation links

Pattern:
- `/operator/write/object/{object_id}` without a `revision_id`
- `/operator/write/object/{object_id}#revision-form`

Matches and disposition:
- [knowledge/operator-web-ui.md](operator-web-ui.md): intentional.
  - Documents the load-only GET route contract.
- [tests/interfaces/test_write_ui.py](../tests/interfaces/test_write_ui.py): intentional.
  - Exercises the explicit `400 Bad Request` path for an invalid load-only request.
- [src/papyrus/interfaces/web/routes/write_guided.py](../src/papyrus/interfaces/web/routes/write_guided.py): intentional.
  - Declares the load-only route and redirects to it only with `revision_id`.
- [src/papyrus/interfaces/web/routes/write_object.py](../src/papyrus/interfaces/web/routes/write_object.py): intentional.
  - Redirect target always appends a concrete `revision_id`.
- [src/papyrus/interfaces/web/presenters/ingest_presenter.py](../src/papyrus/interfaces/web/presenters/ingest_presenter.py): intentional.
  - Open-converted-draft link always appends a concrete `revision_id`.

Disposition:
- No GET affordance remains that relies on page-load side effects to create a draft.

## Search: old action labels associated with draft start

Pattern:
- `Draft first revision`
- `Revise guidance`

Matches and disposition:
- [src/papyrus/interfaces/web/presenters/governed_presenter.py](../src/papyrus/interfaces/web/presenters/governed_presenter.py): intentional.
  - Label text is still used for an explicit POST start action, not a GET creation link.
- [src/papyrus/interfaces/web/presenters/object_presenter.py](../src/papyrus/interfaces/web/presenters/object_presenter.py): intentional.
  - Label text remains, but the affordance now resolves through centralized governed authoring-entry logic and uses POST start when creation may be needed.

Disposition:
- Kept intentionally as wording only. Semantics are now honest.

## Search: home-route governance math after query extraction

Pattern:
- `projection_use_guidance`
- `read_ready`
- `review_required`
- `needs_revalidation`

Matches and disposition:
- [src/papyrus/application/read_models/home_dashboard.py](../src/papyrus/application/read_models/home_dashboard.py): intentional.
  - Application query owns the grouped counts and work-area derivation.
- [src/papyrus/interfaces/web/presenters/home_presenter.py](../src/papyrus/interfaces/web/presenters/home_presenter.py): intentional.
  - Presenter only renders already-grouped query output.
- [src/papyrus/interfaces/web/routes/write_search.py](../src/papyrus/interfaces/web/routes/write_search.py): intentional and out of scope for the home-route phase.
  - Route reads `ui_projection` guidance text from an existing backend contract; it does not derive governed meaning from raw lifecycle state.

Disposition:
- No home-route governance math remains. Remaining matches are application-owned or projection-backed.

## Search: documentation drift on shell and actor presentation

Pattern:
- `focus` drafting claims
- `actor banner`
- `revisions/start`
- `400 bad request`

Result:
- Matches now describe the implemented contract in:
  - [knowledge/operator-web-ui.md](operator-web-ui.md)
  - [tests/test_documentation_contract.py](../tests/test_documentation_contract.py)

Disposition:
- Updated intentionally to match implementation.

## Search: removed shared-route contract

Pattern:
- `/read`
- `/review`
- `/objects/`
- `/services/`
- `/write/objects/`
- `/ingest`

Result:
- Repository-owned docs, presenters, and tests now use only `/reader/*`, `/operator/*`, and `/admin/*` web routes.
- Operator JSON API routes intentionally remain non-role-prefixed in `src/papyrus/interfaces/api.py`.

Disposition:
- Shared web routes removed. Any future role-prefixed API change requires a separate decision and migration.

## Search: retired thin presenter shards after family consolidation

Pattern:
- `read_filter_bar_presenter`
- `article_section_presenter`
- `service_map_presenter`
- `health_board_presenter`
- `review_lane_presenter`
- `activity_event_list_presenter`
- `revision_history_table_presenter`
- `impact_summary_presenter`
- `ingest_upload_presenter`
- `manage_presenter`

Result:
- No matches remain under `src/` or `tests/`.
- Documentation ownership references now point to:
  - `queue_presenter.py`
  - `object_presenter.py`
  - `service_presenter.py`
  - `dashboard_presenter.py`
  - `review_presenter.py`
  - `activity_presenter.py`
  - `revision_presenter.py`
  - `impact_presenter.py`
  - `ingest_presenter.py`

Disposition:
- Thin presenter shards removed completely.
- Shared primitives intentionally retained in `common.py`, `form_presenter.py`, `governed_presenter.py`, `write_presenter.py`, and `write_support_presenter.py`.
