# Operator Web UI

This document describes the current Papyrus operator web interface after the server-rendered UI refactor.

## Purpose And Scope

- Provide a stable operator shell for three modes of use: read, write, and manage.
- Preserve the application service layer as the source of workflow behavior.
- Keep trust posture, approval state, evidence health, and audit signals visible across the interface.
- Support governed POST workflows for object creation, revision authoring, review submission, reviewer assignment, approval, and rejection.

This change does not rework repository schemas, canonical source layout, or the underlying governance workflow model.

## Technical Approach

- `papyrus.interfaces.web` is now a package rather than a monolithic module.
- WSGI request parsing, route matching, template rendering, and static asset serving are separated into dedicated modules.
- Route handlers stay thin:
  - read request state
  - call application queries or commands
  - pass structured results into presenters
  - render server-side HTML
- Templates live under `src/papyrus/interfaces/web/templates/` and are organized into:
  - shared shell layout
  - reusable partial components
  - page templates
- CSS is split into tokens, layout, components, and page-level rules under `src/papyrus/interfaces/web/static/css/`.
- Minimal progressive enhancement lives in `src/papyrus/interfaces/web/static/js/` for search filtering, disclosure hooks, and path/id suggestions in forms.

## Dependencies Introduced Or Modified

- No new third-party Python dependencies were introduced.
- The refactor continues to use the existing standard-library WSGI stack and repository taxonomies.
- The JSON API was extended to expose thin write/manage endpoints aligned to existing application commands.

## Tradeoffs And Known Limitations

- Draft objects and draft revisions remain runtime-governed records; the UI does not write canonical Markdown source files.
- Revision history is comparison-friendly, but it does not yet implement a true side-by-side diff view.
- The interface is still intended for local or otherwise trusted operator environments; it does not introduce an authentication or CSRF layer.
- Form structure is typed and guided, but repeated citation entry is intentionally modest rather than fully dynamic.

## Operational Notes

- The old inline-rendering `src/papyrus/interfaces/web.py` implementation was removed.
- The compatibility import path remains the same: `papyrus.interfaces.web`.
- Read surfaces preserve queue, object detail, revision history, service detail, dashboard, and impact coverage while improving trust visibility.
- Write and manage flows now use redirect-after-post patterns so operator actions are explicit and inspectable.
