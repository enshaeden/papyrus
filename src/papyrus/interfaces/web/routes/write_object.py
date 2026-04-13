from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.authoring_flow import ensure_draft_revision
from papyrus.application.commands import create_object_command
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.forms.object_forms import default_object_values, validate_object_form
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.write_presenter import present_object_setup_page
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.urls import write_object_url


def register(router, runtime) -> None:
    def create_object_page(request: Request):
        experience = require_experience(request, "operator")
        values = default_object_values()
        errors: dict[str, list[str]] = {}
        page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""
        if request.method == "POST":
            values = {key: request.form_value(key) for key in values}
            result = validate_object_form(values, taxonomies=runtime.taxonomies)
            if result.is_valid:
                created = create_object_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    actor=str(experience.audit_actor_id),
                    **result.cleaned_data,
                )
                draft = ensure_draft_revision(
                    object_id=created.object_id,
                    blueprint_id=str(result.cleaned_data["object_type"]),
                    actor=str(experience.audit_actor_id),
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                )
                return redirect_response(
                    write_object_url(created.object_id, revision_id=str(draft["revision_id"]))
                    + f"&notice={quote_plus('Draft setup saved. Continue the guided revision below.')}"
                    + "#revision-form"
                )
            errors = result.errors
            if errors:
                page_flash_html = FormPresenter(runtime.template_renderer).flash(
                    title="Attention",
                    body="Draft setup not saved. Fix the blocking fields below.",
                    tone="warning",
                )
        page_context = present_object_setup_page(runtime, values, errors, form_action=request.path)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_object_new.html",
                page_title="Start draft",
                page_header={
                    "headline": "Start draft",
                    "show_actor_links": True,
                },
                active_nav="write",
                flash_html=page_flash_html,
                role_id=experience.role,
                current_path=request.path,
                aside_html="",
                shell_variant="normal",
                page_context=page_context,
            )
        )

    router.add(["GET", "POST"], "/operator/write/new", create_object_page)
