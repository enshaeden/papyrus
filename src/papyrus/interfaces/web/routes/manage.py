from __future__ import annotations

import json
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
from papyrus.application.queries import audit_view, event_history, impact_view_for_object, knowledge_object_detail, manage_queue, review_detail, validation_run_history
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
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    action_descriptor,
    compact_action_menu_html,
    primary_surface_href,
    projection_reasons,
    projection_state,
    projection_use_guidance,
    render_acknowledgement_panel,
    render_action_contract_panel,
    render_contract_status_panel,
    render_governed_action_panel,
    render_projection_status_panel,
)
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path, render_list, tone_for_approval, tone_for_trust


def _manage_item_detail_href(item: dict[str, object]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _manage_item_actions(components: ComponentPresenter, item: dict[str, object]) -> str:
    return compact_action_menu_html(
        components,
        ui_projection=item.get("ui_projection"),
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
    )


def _governed_context_html(
    components: ComponentPresenter,
    *,
    detail: dict[str, object],
    status_title: str,
    action_id: str | None = None,
    action_title: str | None = None,
    show_actions: bool = False,
) -> str:
    panels = [
        render_projection_status_panel(
            components,
            title=status_title,
            ui_projection=detail.get("ui_projection"),
        )
    ]
    if action_id is not None:
        panels.append(
            render_action_contract_panel(
                components,
                title=action_title or "Action contract",
                action=action_descriptor(detail.get("ui_projection"), action_id),
            )
        )
    if show_actions:
        panels.append(
            render_governed_action_panel(
                components,
                title="Governed actions",
                ui_projection=detail.get("ui_projection"),
                object_id=str(detail["object"]["object_id"]),
                revision_id=str((detail.get("revision") or detail.get("current_revision") or {}).get("revision_id") or "") or None,
                show_ctas=False,
            )
        )
    return join_html(panels)


def _manage_table(components, title: str, items: list[dict[str, object]]) -> str:
    rows = []
    for item in items:
        use_guidance = projection_use_guidance(item.get("ui_projection"))
        state = projection_state(item.get("ui_projection"))
        reasons = projection_reasons(item.get("ui_projection"))
        rows.append(
            [
                components.decision_cell(
                    title_html=link(str(item["title"]), _manage_item_detail_href(item)),
                    supporting_html=escape(item.get("change_summary") or item.get("summary") or "No recent summary recorded."),
                    meta=[
                        escape(str(item.get("object_id") or "")),
                    ],
                ),
                components.decision_cell(
                    title_html=escape(use_guidance.get("summary") or "Backend guidance unavailable"),
                    badges=[
                        components.badge(
                            label="Trust",
                            value=str(state.get("trust_state") or "unknown"),
                            tone=tone_for_trust(str(state.get("trust_state") or "unknown")),
                        ),
                        components.badge(
                            label="Approval",
                            value=str(state.get("approval_state") or "unknown"),
                            tone=tone_for_approval(str(state.get("approval_state") or "unknown")),
                        ),
                        components.badge(
                            label="Revision",
                            value=str(state.get("revision_review_state") or "unknown"),
                            tone=tone_for_approval(str(state.get("revision_review_state") or "unknown")),
                        ),
                    ],
                    supporting_html=escape(use_guidance.get("detail") or "Papyrus did not return governed detail for this queue item."),
                ),
                components.decision_cell(
                    title_html=escape(use_guidance.get("next_action") or "Review this item"),
                    supporting_html=escape(", ".join(reasons) or "Papyrus did not attach explicit reasons to this queue item."),
                    extra_html=(
                        components.inline_disclosure(
                            label="Why this item is here",
                            body_html=render_list([escape(reason) for reason in reasons], css_class="panel-list")
                            or '<p class="empty-state-copy">No explicit reasons were attached to this queue item.</p>',
                        )
                        if reasons
                        else ""
                    ),
                ),
                components.decision_cell(
                    title_html=escape(str(item["owner"])),
                ),
                _manage_item_actions(components, item),
            ]
        )
    return components.section_card(
        title=title,
        eyebrow="Stewardship",
        body_html=components.queue_table(
            headers=["Guidance", "Status", "Attention", "Steward", "Next action"],
            rows=rows,
            table_id=title.lower().replace(" ", "-"),
        ) if rows else '<p class="empty-state-copy">No items in this queue.</p>',
    )


def register(router, runtime) -> None:
    def manage_queue_page(request: Request):
        queue = manage_queue(database_path=runtime.database_path)
        components = ComponentPresenter(runtime.template_renderer)
        overview_html = components.trust_summary(
            title="Stewardship workload",
            badges=[
                components.badge(label="Ready for review", value=len(queue["ready_for_review"]), tone="pending"),
                components.badge(label="Needs decision", value=len(queue["needs_decision"]), tone="pending"),
                components.badge(label="Needs revalidation", value=len(queue["needs_revalidation"]), tone="warning"),
                components.badge(label="Recently changed", value=len(queue["recently_changed"]), tone="brand"),
            ],
            summary="Work is grouped by the next decision, not by raw state.",
        )
        tables_html = join_html(
            [
                _manage_table(components, "Ready for review", queue["ready_for_review"]),
                _manage_table(components, "Needs decision", queue["needs_decision"]),
                _manage_table(components, "Needs revalidation", queue["needs_revalidation"]),
                _manage_table(components, "Drafts and rework", queue["draft_items"]),
                _manage_table(components, "Recently changed", queue["recently_changed"][:10]),
                _manage_table(components, "Superseded or deprecated guidance", queue["superseded_items"]),
            ]
        )
        body = runtime.template_renderer.render(
            "pages/manage_queue.html",
            {"overview_html": overview_html, "tables_html": tables_html},
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_queue.html",
                page_title="Review / Approvals",
                page_header={
                    "headline": "Review queue",
                    "show_actor_banner": True,
                    "show_actor_links": True,
                },
                active_nav="review",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                page_context={"overview_html": overview_html, "tables_html": tables_html},
            )
        )

    def object_supersede_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
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
        summary_html = _governed_context_html(
            components,
            detail=detail,
            status_title=f"{detail['object']['title']} governed posture",
            action_id="supersede_object",
            action_title="Supersession contract",
        )
        form_html = components.section_card(
            title="Supersede object",
            eyebrow="Manage",
            body_html=(
                '<form class="governed-form" method="post">'
                + forms.field(
                    field_id="replacement_object_id",
                    label="Replacement object ID",
                    control_html=forms.input(field_id="replacement_object_id", name="replacement_object_id", value=values["replacement_object_id"]),
                    hint="Use the governed object ID that replaces this content.",
                    errors=errors.get("replacement_object_id"),
                )
                + forms.field(
                    field_id="notes",
                    label="Supersession rationale",
                    control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=4),
                    hint="Required. Explain why operators should stop relying on this object.",
                    errors=errors.get("notes"),
                )
                + forms.button(label="Set replacement")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_object_form.html",
                page_title="Supersede object",
                page_header={"headline": "Supersede guidance"},
                active_nav="health",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"summary_html": summary_html, "form_html": form_html},
            )
        )

    def object_suspect_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
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
        summary_html = _governed_context_html(
            components,
            detail=detail,
            status_title=f"{detail['object']['title']} governed posture",
            action_id="mark_suspect",
            action_title="Suspect contract",
        )
        form_html = components.section_card(
            title="Mark object suspect",
            eyebrow="Manage",
            body_html=(
                '<form class="governed-form" method="post">'
                + forms.field(
                    field_id="changed_entity_type",
                    label="Changed entity type",
                    control_html=forms.input(field_id="changed_entity_type", name="changed_entity_type", value=values["changed_entity_type"], placeholder="service"),
                    hint="Examples: service, dependency, citation_target, upstream_system.",
                    errors=errors.get("changed_entity_type"),
                )
                + forms.field(
                    field_id="changed_entity_id",
                    label="Changed entity ID",
                    control_html=forms.input(field_id="changed_entity_id", name="changed_entity_id", value=values["changed_entity_id"]),
                    hint="Optional identifier for the specific changed dependency.",
                    errors=errors.get("changed_entity_id"),
                )
                + forms.field(
                    field_id="reason",
                    label="Suspect rationale",
                    control_html=forms.textarea(field_id="reason", name="reason", value=values["reason"], rows=4),
                    hint="Required. Make the degradation legible to future operators and reviewers.",
                    errors=errors.get("reason"),
                )
                + forms.button(label="Flag for review")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_object_form.html",
                page_title="Mark object suspect",
                page_header={"headline": "Mark guidance suspect"},
                active_nav="health",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"summary_html": summary_html, "form_html": form_html},
            )
        )

    def object_archive_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
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
        summary_html = _governed_context_html(
            components,
            detail=detail,
            status_title=f"{detail['object']['title']} governed posture",
            action_id="archive_object",
            action_title="Archive contract",
        )
        form_html = components.section_card(
            title="Archive object",
            eyebrow="Manage",
            body_html=(
                '<form class="governed-form" method="post">'
                + forms.field(
                    field_id="retirement_reason",
                    label="Retirement rationale",
                    control_html=forms.textarea(field_id="retirement_reason", name="retirement_reason", value=values["retirement_reason"], rows=4),
                    hint="Required. State why operators should no longer treat this as active guidance.",
                    errors=errors.get("retirement_reason"),
                )
                + forms.field(
                    field_id="notes",
                    label="Operator notes",
                    control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=3),
                    hint="Optional notes stored with the archive audit event.",
                )
                + render_acknowledgement_panel(
                    components,
                    forms,
                    title="Required acknowledgements",
                    required_acknowledgements=required_acknowledgements,
                    selected_acknowledgements=selected_acknowledgements,
                    operator_message=str(archive_action.get("detail") or "Review the required acknowledgements before continuing."),
                    errors=errors.get("acknowledgements"),
                )
                + forms.button(label="Archive guidance")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_object_form.html",
                page_title="Archive object",
                page_header={"headline": "Archive guidance"},
                active_nav="health",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"summary_html": summary_html, "form_html": form_html},
            )
        )

    def evidence_revalidation_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
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
        summary_html = _governed_context_html(
            components,
            detail=detail,
            status_title=f"{detail['object']['title']} governed posture",
            action_id="request_evidence_revalidation",
            action_title="Evidence follow-up contract",
        )
        form_html = components.section_card(
            title="Revalidate evidence",
            eyebrow="Evidence",
            body_html=(
                '<form class="governed-form" method="post">'
                + forms.field(
                    field_id="notes",
                    label="Revalidation notes",
                    control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=4),
                    hint="Optional notes for the next reviewer or operator.",
                )
                + forms.button(label="Request evidence revalidation")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_object_form.html",
                page_title="Revalidate evidence",
                page_header={"headline": "Revalidate evidence"},
                active_nav="health",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"summary_html": summary_html, "form_html": form_html},
            )
        )

    def review_assignment_page(request: Request):
        object_id = request.route_value("object_id")
        revision_id = request.route_value("revision_id")
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
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
        summary_html = _governed_context_html(
            components,
            detail=detail,
            status_title=f"{detail['object']['title']} review posture",
            action_id="assign_reviewer",
            action_title="Reviewer assignment contract",
            show_actions=True,
        )
        assignment_html = components.audit_panel(
            title="Current assignments",
            items=[
                f"{escape(assignment['reviewer'])} · {escape(assignment['state'])} · assigned {escape(format_timestamp(assignment['assigned_at']))}"
                for assignment in detail["assignments"]
            ],
            empty_label="No reviewers assigned yet.",
        )
        form_html = components.section_card(
            title="Assign reviewer",
            eyebrow="Manage",
            body_html=(
                '<form class="governed-form" method="post">'
                + forms.field(field_id="reviewer", label="Reviewer", control_html=forms.input(field_id="reviewer", name="reviewer", value=values["reviewer"]), errors=errors.get("reviewer"))
                + forms.field(field_id="due_at", label="Due date", control_html=forms.input(field_id="due_at", name="due_at", value=values["due_at"], input_type="date"), errors=errors.get("due_at"))
                + forms.field(field_id="notes", label="Assignment notes", control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=3))
                + forms.button(label="Assign reviewer")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/review_assignment.html",
                page_title="Assign reviewer",
                page_header={"headline": "Assign reviewer"},
                active_nav="review",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"summary_html": summary_html, "assignment_html": assignment_html, "form_html": form_html},
            )
        )

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
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
        approve_values = {
            "reviewer": request.form_value("reviewer"),
            "notes": request.form_value("notes"),
        }
        errors: dict[str, list[str]] = {}
        page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""
        if request.method == "POST":
            action = request.form_value("decision")
            result = validate_decision_form(approve_values, require_notes=action == "reject")
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
                    page_flash_html = forms.flash(
                        title="Attention",
                        body=str(exc),
                        tone="warning",
                    )
        summary_html = _governed_context_html(
            components,
            detail=detail,
            status_title=f"{detail['object']['title']} review posture",
            action_id="approve_revision",
            action_title="Review decision contract",
            show_actions=True,
        )
        decisions_html = join_html(
            [
                components.section_card(
                    title="What changed",
                    eyebrow="Review",
                    body_html=(
                        f"<p><strong>Change summary:</strong> {escape(detail['revision']['change_summary'] or 'No change summary recorded.')}</p>"
                        f"<p><strong>Changed fields:</strong> {escape(', '.join(preview.changed_fields) or 'None')}</p>"
                        f"<p><strong>Changed sections:</strong> {escape(', '.join(preview.changed_sections) or 'None')}</p>"
                    ),
                ),
                components.section_card(
                    title="Evidence and unresolved work",
                    eyebrow="Review",
                    tone="warning" if findings else "approved",
                    body_html=(
                        f"<p><strong>Supporting citations:</strong> {escape(len(detail['citations']))}</p>"
                        + (
                            render_list([escape(item) for item in findings], css_class="validation-findings")
                            if findings
                            else "<p>No unresolved validation warnings are currently recorded.</p>"
                        )
                    ),
                ),
                render_contract_status_panel(
                    components,
                    title="Writeback contract",
                    summary="Approval writeback preview",
                    operator_message=preview.operator_message,
                    source_of_truth=preview.source_of_truth,
                    transition=preview.transition,
                    invalidated_assumptions=list(preview.invalidated_assumptions),
                    required_acknowledgements=list(preview.required_acknowledgements),
                    tone="danger" if preview.conflict_detected else "context",
                    footer_html=(
                        f'<p class="section-footer">Canonical path {escape(preview.file_path)} · previous approved revision {escape(preview.previous_revision_id or "None")} · conflict {escape(preview.conflict_reason or "none")}</p>'
                    ),
                ),
                render_acknowledgement_panel(
                    components,
                    forms,
                    title="Writeback acknowledgement requirements",
                    required_acknowledgements=list(preview.required_acknowledgements),
                    selected_acknowledgements=[],
                    operator_message=preview.operator_message,
                    read_only=True,
                ),
                components.section_card(
                    title="Likely downstream effect",
                    eyebrow="Impact",
                    body_html=(
                        f"<p><strong>Impacted objects:</strong> {escape(len(impact['impacted_objects']))}</p>"
                        f"<p><strong>What to review next:</strong> {escape(' | '.join(impact['current_impact']['revalidate']))}</p>"
                    ),
                ),
                components.audit_panel(
                    title="Revision audit",
                    items=[
                        f"{escape(format_timestamp(event['occurred_at']))} · {escape(event['event_type'])} · {escape(event['actor'])}"
                        for event in detail["audit_events"]
                    ],
                    empty_label="No revision audit events recorded.",
                ),
                components.section_card(
                    title="Approve or reject",
                    eyebrow="Review",
                    body_html=(
                        '<form class="governed-form" method="post">'
                        + forms.field(field_id="reviewer", label="Reviewer", control_html=forms.input(field_id="reviewer", name="reviewer", value=approve_values["reviewer"]), errors=errors.get("reviewer"))
                        + forms.field(field_id="notes", label="Decision notes", control_html=forms.textarea(field_id="notes", name="notes", value=approve_values["notes"], rows=4), hint="Required for rejection; optional for approval. Use notes to explain the decision or the reason for a block.", errors=errors.get("notes"))
                        + '<div class="button-row">'
                        + '<button class="button button-primary" type="submit" name="decision" value="approve">Approve revision</button>'
                        + '<button class="button button-danger" type="submit" name="decision" value="reject">Reject revision</button>'
                        + "</div></form>"
                    ),
                ),
            ]
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_review_decision.html",
                page_title="Review decision",
                page_header={"headline": "Review decision"},
                active_nav="review",
                flash_html=page_flash_html,
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"summary_html": summary_html, "decisions_html": decisions_html},
            )
        )

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
        components = ComponentPresenter(runtime.template_renderer)
        filter_controls_html = (
            '<form class="filter-form" method="get" action="/activity">'
            f'<input type="text" name="object_id" placeholder="Filter object ID" value="{escape(object_id or "")}" />'
            '<select name="group">'
            f'<option value=""{" selected" if not selected_group else ""}>All activity groups</option>'
            f'<option value="service_changes"{" selected" if selected_group == "service_changes" else ""}>Service changes</option>'
            f'<option value="evidence_degradation"{" selected" if selected_group == "evidence_degradation" else ""}>Evidence degradation</option>'
            f'<option value="validation_failures"{" selected" if selected_group == "validation_failures" else ""}>Validation failures</option>'
            f'<option value="manual_suspect_marks"{" selected" if selected_group == "manual_suspect_marks" else ""}>Manual suspect marks</option>'
            "</select>"
            '<button class="button button-primary" type="submit">Show activity</button>'
            "</form>"
        )
        summary_html = components.trust_summary(
            title="Activity overview",
            badges=[
                components.badge(label="Service changes", value=sum(1 for event in structured_events if event["group"] == "service_changes"), tone="warning"),
                components.badge(label="Evidence issues", value=sum(1 for event in structured_events if event["group"] == "evidence_degradation"), tone="warning"),
                components.badge(label="Validation failures", value=sum(1 for event in structured_events if event["group"] == "validation_failures"), tone="danger"),
                components.badge(label="Suspect marks", value=sum(1 for event in structured_events if event["group"] == "manual_suspect_marks"), tone="pending"),
            ],
            summary="Activity should show consequence and next step, not raw payloads.",
        )
        audit_html = components.section_card(
            title="Governed audit trail",
            eyebrow="History",
            body_html=components.queue_table(
                headers=["Event", "Affected", "Recorded", "Details"],
                rows=[
                    [
                        components.decision_cell(
                            title_html=escape(event["event_type"]),
                            meta=[escape(event["actor"])],
                        ),
                        components.decision_cell(
                            title_html=escape(event["object_id"] or "No object"),
                            meta=[escape(event["revision_id"] or "No revision")],
                        ),
                        escape(format_timestamp(event["occurred_at"])),
                        components.decision_cell(
                            title_html=escape(", ".join(f"{key}={value}" for key, value in event["details"].items() if value) or "No extra details"),
                        ),
                    ]
                    for event in events
                ],
                table_id="audit-history",
            ),
        )
        grouped_labels = (
            ("service_changes", "Service changes"),
            ("evidence_degradation", "Evidence degradation"),
            ("validation_failures", "Validation failures"),
            ("manual_suspect_marks", "Manual suspect marks"),
            ("review_activity", "Review activity"),
            ("other", "Other activity"),
        )
        event_sections: list[str] = []
        for group_key, label in grouped_labels:
            group_events = [event for event in structured_events if event["group"] == group_key]
            if not group_events:
                continue
            event_sections.append(
                components.section_card(
                    title=label,
                    eyebrow="Activity",
                    body_html=components.queue_table(
                        headers=["What happened", "Affected", "Recorded", "Do next"],
                        rows=[
                            [
                                components.decision_cell(
                                    title_html=escape(event["what_happened"]),
                                    meta=[escape(event["actor"])],
                                ),
                                components.decision_cell(
                                    title_html=escape(f"{event['entity_type']}:{event['entity_id']}"),
                                ),
                                escape(format_timestamp(event["occurred_at"])),
                                components.decision_cell(
                                    title_html=escape(event["next_action"]),
                                ),
                            ]
                            for event in group_events
                        ],
                        table_id=f"activity-{group_key}",
                    ),
                )
            )
        event_html = join_html(event_sections) or components.empty_state(
            title="No matching activity",
            description="Adjust the activity filter or wait for the next recorded event.",
        )
        validation_html = components.section_card(
            title="Validation runs",
            eyebrow="History",
            body_html=components.queue_table(
                headers=["Run", "Status", "Findings", "Completed"],
                rows=[
                    [
                        components.decision_cell(
                            title_html=escape(run["run_type"]),
                            meta=[escape(run["run_id"])],
                        ),
                        escape(run["status"]),
                        escape(run["finding_count"]),
                        escape(format_timestamp(run["completed_at"])),
                    ]
                    for run in validation_runs[:20]
                ],
                table_id="audit-validation-runs",
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_audit.html",
                page_title="Activity / History",
                page_header={
                    "headline": "Activity",
                    "show_actor_banner": True,
                    "show_actor_links": True,
                },
                active_nav="activity",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                page_context={
                    "summary_html": summary_html,
                    "filter_bar_html": components.filter_bar(title="Activity filters", controls_html=filter_controls_html),
                    "audit_html": audit_html,
                    "event_html": event_html,
                    "validation_html": validation_html,
                },
            )
        )

    def validation_runs_page(request: Request):
        runs = validation_run_history(database_path=runtime.database_path)
        components = ComponentPresenter(runtime.template_renderer)
        add_run_html = components.action_bar(
            items=[link("Record validation run", "/manage/validation-runs/new", css_class="button button-primary")]
        )
        validation_table_html = components.section_card(
            title="Validation runs",
            eyebrow="Validation",
            body_html=components.queue_table(
                headers=["Run", "Status", "Findings", "Completed"],
                rows=[
                    [
                        components.decision_cell(
                            title_html=escape(run["run_type"]),
                            meta=[escape(run["run_id"])],
                        ),
                        escape(run["status"]),
                        escape(run["finding_count"]),
                        escape(format_timestamp(run["completed_at"])),
                    ]
                    for run in runs
                ],
                table_id="validation-runs",
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_validation_runs.html",
                page_title="Validation runs",
                page_header={
                    "headline": "Validation runs",
                    "actions_html": add_run_html,
                    "show_actor_banner": True,
                    "show_actor_links": True,
                },
                active_nav="activity",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                page_context={"validation_table_html": validation_table_html},
            )
        )

    def validation_run_new_page(request: Request):
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
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
        form_html = components.section_card(
            title="Record validation run",
            eyebrow="Validation",
            body_html=(
                '<form class="governed-form" method="post">'
                + forms.field(field_id="run_id", label="Run ID", control_html=forms.input(field_id="run_id", name="run_id", value=values["run_id"]), errors=errors.get("run_id"))
                + forms.field(field_id="run_type", label="Run type", control_html=forms.input(field_id="run_type", name="run_type", value=values["run_type"], placeholder="manual_operator_check"), errors=errors.get("run_type"))
                + forms.field(field_id="status", label="Status", control_html=forms.input(field_id="status", name="status", value=values["status"], placeholder="passed"), errors=errors.get("status"))
                + forms.field(field_id="finding_count", label="Finding count", control_html=forms.input(field_id="finding_count", name="finding_count", value=values["finding_count"], input_type="number"), errors=errors.get("finding_count"))
                + forms.field(field_id="details", label="Details", control_html=forms.textarea(field_id="details", name="details", value=values["details"], rows=4), hint="Optional operator-readable summary stored with the run.")
                + forms.button(label="Record validation run")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_validation_run_new.html",
                page_title="Record validation run",
                page_header={"headline": "Record validation run"},
                active_nav="activity",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="minimal",
                page_context={"form_html": form_html},
            )
        )

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
