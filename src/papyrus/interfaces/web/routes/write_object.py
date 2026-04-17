from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.authoring_flow import ensure_draft_revision
from papyrus.application.blueprint_registry import (
    list_advanced_authoring_blueprints,
    list_primary_authoring_blueprints,
)
from papyrus.application.commands import create_object_command
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.forms.object_forms import default_object_values, validate_object_form
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.write_presenter import present_object_setup_page
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.urls import write_object_url


def _render_object_setup_page(
    runtime,
    request: Request,
    *,
    authoring_blueprints,
    page_title: str,
    page_headline: str,
    authoring_mode: str,
):
    experience = require_experience(request, "operator")
    default_object_type = (
        list_advanced_authoring_blueprints()[0].blueprint_id
        if authoring_mode == "advanced" and list_advanced_authoring_blueprints()
        else authoring_blueprints[0].blueprint_id
    )
    values = default_object_values(object_type=default_object_type)
    errors: dict[str, list[str]] = {}
    page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""
    if request.method == "POST":
        values = {key: request.form_value(key) for key in values}
        result = validate_object_form(
            values,
            taxonomies=runtime.taxonomies,
            allowed_blueprint_ids={blueprint.blueprint_id for blueprint in authoring_blueprints},
        )
        if result.is_valid:
            created = create_object_command(
                database_path=runtime.database_path,
                source_root=runtime.source_root,
                actor=request.actor_id,
                **result.cleaned_data,
            )
            draft = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=str(result.cleaned_data["object_type"]),
                actor=request.actor_id,
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
    page_context = present_object_setup_page(
        runtime,
        values,
        errors,
        form_action=request.path,
        authoring_blueprints=authoring_blueprints,
        authoring_mode=authoring_mode,
    )
    return html_response(
        runtime.page_renderer.render_page(
            page_template="pages/write_object_new.html",
            page_title=page_title,
            page_header={
                "headline": page_headline,
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


def register(router, runtime) -> None:
    primary_authoring_blueprints = list_primary_authoring_blueprints()
    def write_landing_page(request: Request):
        require_experience(request, "operator", "admin")
        return redirect_response("/write/new")

    def create_primary_object_page(request: Request):
        return _render_object_setup_page(
            runtime,
            request,
            authoring_blueprints=primary_authoring_blueprints,
            page_title="Start draft",
            page_headline="Start draft",
            authoring_mode="primary",
        )

    router.add(["GET"], "/write", write_landing_page, minimum_visible_role="operator")
    router.add(["GET", "POST"], "/write/new", create_primary_object_page, minimum_visible_role="operator")
