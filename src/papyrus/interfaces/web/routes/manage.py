from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.commands import (
    archive_object_command,
    approve_revision_command,
    assign_reviewer_command,
    mark_object_suspect_due_to_change_command,
    request_evidence_revalidation_command,
    record_validation_run_command,
    reject_revision_command,
    supersede_object_command,
)
from papyrus.application.queries import (
    audit_view,
    event_history,
    impact_view_for_object,
    knowledge_object_detail,
    manage_queue,
    review_detail,
    validation_run_history,
)
from papyrus.application.writeback_flow import preview_revision_writeback
from papyrus.interfaces.web.forms.revision_forms import build_submission_findings
from papyrus.interfaces.web.forms.review_forms import (
    validate_archive_form,
    validate_assignment_form,
    validate_decision_form,
    validate_suspect_form,
    validate_supersede_form,
    validate_validation_run_form,
)
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.governed_presenter import action_descriptor
from papyrus.interfaces.web.presenters.manage_presenter import (
    present_audit_page,
    present_evidence_revalidation_page,
    present_manage_queue_page,
    present_object_archive_page,
    present_object_suspect_page,
    present_object_supersede_page,
    present_review_assignment_page,
    present_review_decision_page,
    present_validation_run_new_page,
    present_validation_runs_page,
    present_warning_flash,
)
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import quoted_path


def _render_page(runtime, request: Request, *, page: dict[str, object], flash_html: str | None = None):
    return html_response(
        runtime.page_renderer.render_page(
            flash_html=flash_html if flash_html is not None else flash_html_for_request(runtime, request),
            actor_id=actor_for_request(request),
            current_path=request.path,
            **page,
        )
    )


def register(router, runtime) -> None:
    def manage_queue_page(request: Request):
        queue = manage_queue(database_path=runtime.database_path)
        page = present_manage_queue_page(
            runtime.template_renderer,
            queue=queue,
            selected_object_id=request.query_value("selected_object_id").strip(),
            selected_revision_id=request.query_value("selected_revision_id").strip(),
        )
        return _render_page(runtime, request, page=page)

    def object_supersede_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        values = {
            "replacement_object_id": request.form_value("replacement_object_id"),
            "notes": request.form_value("notes"),
        }
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            result = validate_supersede_form(values)
            if result.is_valid:
                supersede_object_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    object_id=object_id,
                    replacement_object_id=str(result.cleaned_data["replacement_object_id"]),
                    actor=actor_for_request(request),
                    notes=str(result.cleaned_data["notes"]),
                )
                return redirect_response(
                    f"/objects/{quoted_path(object_id)}?notice={quote_plus('Object superseded and audit trail recorded')}"
                )
            errors = result.errors
        page = present_object_supersede_page(
            runtime.template_renderer,
            detail=detail,
            values=values,
            errors=errors,
        )
        return _render_page(runtime, request, page=page)

    def object_suspect_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        values = {
            "reason": request.form_value("reason"),
            "changed_entity_type": request.form_value("changed_entity_type"),
            "changed_entity_id": request.form_value("changed_entity_id"),
        }
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            result = validate_suspect_form(values)
            if result.is_valid:
                mark_object_suspect_due_to_change_command(
                    database_path=runtime.database_path,
                    object_id=object_id,
                    actor=actor_for_request(request),
                    reason=str(result.cleaned_data["reason"]),
                    changed_entity_type=str(result.cleaned_data["changed_entity_type"]),
                    changed_entity_id=result.cleaned_data["changed_entity_id"],
                )
                return redirect_response(
                    f"/objects/{quoted_path(object_id)}?notice={quote_plus('Object marked suspect with explicit rationale')}"
                )
            errors = result.errors
        page = present_object_suspect_page(
            runtime.template_renderer,
            detail=detail,
            values=values,
            errors=errors,
        )
        return _render_page(runtime, request, page=page)

    def object_archive_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        values = {
            "retirement_reason": request.form_value("retirement_reason"),
            "notes": request.form_value("notes"),
        }
        selected_acknowledgements = request.form_values("acknowledgements")
        archive_action = action_descriptor(detail.get("ui_projection"), "archive_object") or {}
        required_acknowledgements = [
            str(item)
            for item in ((archive_action.get("policy") or {}).get("required_acknowledgements") or [])
        ]
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            result = validate_archive_form(
                values,
                selected_acknowledgements=selected_acknowledgements,
                required_acknowledgements=required_acknowledgements,
            )
            if result.is_valid:
                archive_object_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    object_id=object_id,
                    actor=actor_for_request(request),
                    retirement_reason=str(result.cleaned_data["retirement_reason"]),
                    notes=result.cleaned_data["notes"],
                    acknowledgements=result.cleaned_data["acknowledgements"],
                )
                return redirect_response(
                    f"/objects/{quoted_path(object_id)}?notice={quote_plus('Object archived and canonical path moved under archive/knowledge/')}"
                )
            errors = result.errors
        page = present_object_archive_page(
            runtime.template_renderer,
            detail=detail,
            values=values,
            errors=errors,
            selected_acknowledgements=selected_acknowledgements,
        )
        return _render_page(runtime, request, page=page)

    def evidence_revalidation_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        values = {"notes": request.form_value("notes")}
        if request.method == "POST":
            request_evidence_revalidation_command(
                database_path=runtime.database_path,
                object_id=object_id,
                actor=actor_for_request(request),
                notes=values["notes"] or None,
            )
            return redirect_response(
                f"/objects/{quoted_path(object_id)}?notice={quote_plus('Evidence revalidation requested')}"
            )
        page = present_evidence_revalidation_page(
            runtime.template_renderer,
            detail=detail,
            values=values,
        )
        return _render_page(runtime, request, page=page)

    def review_assignment_page(request: Request):
        object_id = request.route_value("object_id")
        revision_id = request.route_value("revision_id")
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        values = {
            "reviewer": request.form_value("reviewer"),
            "notes": request.form_value("notes"),
            "due_at": request.form_value("due_at"),
        }
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            result = validate_assignment_form(values)
            if result.is_valid:
                assign_reviewer_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    object_id=object_id,
                    revision_id=revision_id,
                    reviewer=str(result.cleaned_data["reviewer"]),
                    actor=actor_for_request(request),
                    due_at=result.cleaned_data["due_at"],
                    notes=result.cleaned_data["notes"],
                )
                return redirect_response(
                    f"/manage/reviews/{quoted_path(object_id)}/{quoted_path(revision_id)}?notice={quote_plus('Reviewer assigned')}"
                )
            errors = result.errors
        page = present_review_assignment_page(
            runtime.template_renderer,
            detail=detail,
            values=values,
            errors=errors,
        )
        return _render_page(runtime, request, page=page)

    def review_decision_page(request: Request):
        object_id = request.route_value("object_id")
        revision_id = request.route_value("revision_id")
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        impact = impact_view_for_object(object_id, database_path=runtime.database_path)
        preview = preview_revision_writeback(
            database_path=runtime.database_path,
            object_id=object_id,
            revision_id=revision_id,
            root_path=runtime.source_root,
        )
        findings = build_submission_findings(
            object_type=detail["object"]["object_type"],
            payload=detail["revision"]["metadata"],
        )
        values = {
            "reviewer": request.form_value("reviewer"),
            "notes": request.form_value("notes"),
        }
        errors: dict[str, list[str]] = {}
        page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""
        if request.method == "POST":
            action = request.form_value("decision")
            result = validate_decision_form(values, require_notes=action == "reject")
            errors = dict(result.errors)
            if result.is_valid:
                try:
                    if action == "approve":
                        approve_revision_command(
                            database_path=runtime.database_path,
                            source_root=runtime.source_root,
                            object_id=object_id,
                            revision_id=revision_id,
                            reviewer=str(result.cleaned_data["reviewer"]),
                            actor=actor_for_request(request),
                            notes=result.cleaned_data["notes"],
                        )
                        return redirect_response(
                            f"/objects/{quoted_path(object_id)}?notice={quote_plus('Revision approved')}"
                        )
                    reject_revision_command(
                        database_path=runtime.database_path,
                        source_root=runtime.source_root,
                        object_id=object_id,
                        revision_id=revision_id,
                        reviewer=str(result.cleaned_data["reviewer"]),
                        actor=actor_for_request(request),
                        notes=str(result.cleaned_data["notes"]),
                    )
                    return redirect_response(
                        f"/manage/reviews/{quoted_path(object_id)}/{quoted_path(revision_id)}?notice={quote_plus('Revision rejected')}"
                    )
                except ValueError as exc:
                    errors.setdefault("notes", []).append(str(exc))
                    page_flash_html = present_warning_flash(
                        runtime.template_renderer,
                        title="Attention",
                        body=str(exc),
                    )
        page = present_review_decision_page(
            runtime.template_renderer,
            detail=detail,
            impact=impact,
            preview=preview,
            findings=findings,
            values=values,
            errors=errors,
        )
        return _render_page(runtime, request, page=page, flash_html=page_flash_html)

    def audit_page(request: Request):
        object_id = request.query_value("object_id") or None
        selected_group = request.query_value("group").strip()
        events = audit_view(object_id=object_id, database_path=runtime.database_path)
        structured_events = event_history(
            entity_id=object_id,
            limit=20,
            database_path=runtime.database_path,
        )
        if selected_group:
            structured_events = [event for event in structured_events if event["group"] == selected_group]
        validation_runs = validation_run_history(database_path=runtime.database_path)
        page = present_audit_page(
            runtime.template_renderer,
            events=events,
            structured_events=structured_events,
            validation_runs=validation_runs,
            object_id=object_id,
            selected_group=selected_group,
        )
        return _render_page(runtime, request, page=page)

    def validation_runs_page(request: Request):
        runs = validation_run_history(database_path=runtime.database_path)
        page = present_validation_runs_page(
            runtime.template_renderer,
            runs=runs,
        )
        return _render_page(runtime, request, page=page)

    def validation_run_new_page(request: Request):
        values = {
            "run_id": request.form_value("run_id"),
            "run_type": request.form_value("run_type"),
            "status": request.form_value("status", "passed"),
            "finding_count": request.form_value("finding_count", "0"),
            "details": request.form_value("details"),
        }
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            result = validate_validation_run_form(values)
            if result.is_valid:
                details_text = result.cleaned_data["details"]
                record_validation_run_command(
                    database_path=runtime.database_path,
                    run_id=str(result.cleaned_data["run_id"]),
                    run_type=str(result.cleaned_data["run_type"]),
                    status=str(result.cleaned_data["status"]),
                    finding_count=int(result.cleaned_data["finding_count"]),
                    details={"summary": details_text} if details_text else {},
                    actor=actor_for_request(request),
                )
                return redirect_response(
                    "/manage/validation-runs?notice="
                    + quote_plus("Validation run recorded with audit evidence")
                )
            errors = result.errors
        page = present_validation_run_new_page(
            runtime.template_renderer,
            values=values,
            errors=errors,
        )
        return _render_page(runtime, request, page=page)

    router.add(["GET"], "/manage/queue", manage_queue_page)
    router.add(["GET"], "/review", manage_queue_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/supersede", object_supersede_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/archive", object_archive_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/suspect", object_suspect_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/evidence/revalidate", evidence_revalidation_page)
    router.add(["GET", "POST"], "/manage/reviews/{object_id}/{revision_id}/assign", review_assignment_page)
    router.add(["GET", "POST"], "/manage/reviews/{object_id}/{revision_id}", review_decision_page)
    router.add(["GET"], "/manage/audit", audit_page)
    router.add(["GET"], "/activity", audit_page)
    router.add(["GET"], "/manage/validation-runs", validation_runs_page)
    router.add(["GET", "POST"], "/manage/validation-runs/new", validation_run_new_page)
