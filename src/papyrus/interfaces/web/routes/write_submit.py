from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.authoring_flow import validate_draft_progress
from papyrus.application.blueprint_registry import get_blueprint
from papyrus.application.commands import submit_for_review_command
from papyrus.application.queries import knowledge_object_detail, review_detail
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.forms.review_forms import validate_submit_form
from papyrus.interfaces.web.forms.revision_forms import build_submission_findings
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.write_presenter import present_submit_page
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.urls import review_assignment_url


def register(router, runtime) -> None:
    def submit_revision_page(request: Request):
        experience = require_experience(request, "operator")
        object_id = request.route_value("object_id")
        object_detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        revision_id = request.query_value("revision_id") or str(
            (object_detail["current_revision"] or {})["revision_id"]
        )
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        values = {"notes": request.form_value("notes")}
        form_errors: dict[str, list[str]] = {}
        draft_status = validate_draft_progress(
            object_id=object_id,
            revision_id=revision_id,
            database_path=runtime.database_path,
            source_root=runtime.source_root,
        )
        blueprint = get_blueprint(
            str(detail["revision"]["blueprint_id"] or detail["object"]["object_type"])
        )
        findings = [
            *draft_status["completion"]["blockers"],
            *draft_status["completion"]["warnings"],
            *build_submission_findings(
                object_type=detail["object"]["object_type"],
                payload=detail["revision"]["metadata"],
            ),
        ]
        if request.method == "POST":
            result = validate_submit_form(values)
            if result.is_valid and not draft_status["completion"]["blockers"]:
                submit_for_review_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    object_id=object_id,
                    revision_id=revision_id,
                    actor=request.actor_id,
                    notes=result.cleaned_data["notes"],
                )
                return redirect_response(
                    review_assignment_url(experience.role, object_id, revision_id)
                    + f"?notice={quote_plus('Revision submitted for review')}"
                )
            form_errors = result.errors
            if draft_status["completion"]["blockers"]:
                form_errors.setdefault("notes", []).append(
                    "Clear the draft blockers before submitting for review."
                )
        page_context = present_submit_page(
            runtime,
            role=experience.role,
            detail=detail,
            object_detail=object_detail,
            blueprint=blueprint,
            completion=draft_status["completion"],
            findings=findings,
            form_errors=form_errors,
            values=values,
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/review_submit.html",
                page_title="Submit for review",
                page_header={"headline": "Send to review"},
                active_nav="write",
                flash_html=flash_html_for_request(runtime, request),
                role_id=experience.role,
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context=page_context,
            )
        )

    router.add(
        ["GET", "POST"],
        "/write/object/{object_id}/submit",
        submit_revision_page,
        minimum_visible_role="operator",
    )
