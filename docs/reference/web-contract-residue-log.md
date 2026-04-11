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
- No matches under `src/`, `tests/`, `docs/`, or `README.md`.

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
- `/write/objects/.../revisions/new` without a `revision_id`
- `/revisions/new#revision-form`

Matches and disposition:
- [docs/reference/operator-web-ui.md](operator-web-ui.md): intentional.
  - Documents the load-only GET route contract.
- [tests/interfaces/test_write_ui.py](../../tests/interfaces/test_write_ui.py): intentional.
  - Exercises the explicit `400 Bad Request` path for an invalid load-only request.
- [src/papyrus/interfaces/web/routes/write_guided.py](../../src/papyrus/interfaces/web/routes/write_guided.py): intentional.
  - Declares the load-only route and redirects to it only with `revision_id`.
- [src/papyrus/interfaces/web/routes/write_object.py](../../src/papyrus/interfaces/web/routes/write_object.py): intentional.
  - Redirect target always appends a concrete `revision_id`.
- [src/papyrus/interfaces/web/presenters/ingest_presenter.py](../../src/papyrus/interfaces/web/presenters/ingest_presenter.py): intentional.
  - Open-converted-draft link always appends a concrete `revision_id`.

Disposition:
- No GET affordance remains that relies on page-load side effects to create a draft.

## Search: old action labels associated with draft start

Pattern:
- `Draft first revision`
- `Revise guidance`

Matches and disposition:
- [src/papyrus/interfaces/web/presenters/governed_presenter.py](../../src/papyrus/interfaces/web/presenters/governed_presenter.py): intentional.
  - Label text is still used for an explicit POST start action, not a GET creation link.
- [src/papyrus/interfaces/web/presenters/object_presenter.py](../../src/papyrus/interfaces/web/presenters/object_presenter.py): intentional.
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
- [src/papyrus/application/read_models/home_dashboard.py](../../src/papyrus/application/read_models/home_dashboard.py): intentional.
  - Application query owns the grouped counts and work-area derivation.
- [src/papyrus/interfaces/web/presenters/home_presenter.py](../../src/papyrus/interfaces/web/presenters/home_presenter.py): intentional.
  - Presenter only renders already-grouped query output.
- [src/papyrus/interfaces/web/routes/write_search.py](../../src/papyrus/interfaces/web/routes/write_search.py): intentional and out of scope for the home-route phase.
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
  - [docs/reference/operator-web-ui.md](operator-web-ui.md)
  - [tests/test_documentation_contract.py](../../tests/test_documentation_contract.py)

Disposition:
- Updated intentionally to match implementation.
