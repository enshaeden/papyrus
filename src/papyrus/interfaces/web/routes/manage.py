from __future__ import annotations

import json
from urllib.parse import quote_plus

from papyrus.application.commands import (
    approve_revision_command,
    assign_reviewer_command,
    mark_object_suspect_due_to_change_command,
    request_evidence_revalidation_command,
    record_validation_run_command,
    reject_revision_command,
    supersede_object_command,
)
from papyrus.application.queries import audit_view, event_history, knowledge_object_detail, manage_queue, review_detail, validation_run_history
from papyrus.interfaces.web.forms.review_forms import (
    validate_assignment_form,
    validate_decision_form,
    validate_suspect_form,
    validate_supersede_form,
    validate_validation_run_form,
)
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path, tone_for_approval, tone_for_trust


def _manage_item_detail_href(item: dict[str, object]) -> str:
    current_revision_id = str(item.get("current_revision_id") or "").strip()
    revision_state = str(item.get("revision_state") or "")
    if not current_revision_id or revision_state in {"draft", "rejected"}:
        return f"/write/objects/{quoted_path(str(item['object_id']))}/revisions/new#revision-form"
    if revision_state == "in_review" and item.get("revision_id"):
        return f"/manage/reviews/{quoted_path(str(item['object_id']))}/{quoted_path(str(item['revision_id']))}"
    return f"/objects/{quoted_path(str(item['object_id']))}"


def _manage_item_actions(item: dict[str, object]) -> str:
    object_id = quoted_path(str(item["object_id"]))
    revision_id = str(item.get("revision_id") or "").strip()
    current_revision_id = str(item.get("current_revision_id") or "").strip()
    revision_state = str(item.get("revision_state") or "")
    actions: list[str] = []

    if not current_revision_id:
        actions.append(link("Draft first revision", f"/write/objects/{object_id}/revisions/new#revision-form", css_class="button button-primary"))
    elif revision_state in {"draft", "rejected"}:
        actions.append(link("Continue draft", f"/write/objects/{object_id}/revisions/new#revision-form", css_class="button button-primary"))
        if revision_id:
            actions.append(link("Submit for review", f"/write/objects/{object_id}/submit?revision_id={quoted_path(revision_id)}", css_class="button button-secondary"))
    elif revision_state == "in_review" and revision_id:
        actions.append(link("Assign reviewer", f"/manage/reviews/{object_id}/{quoted_path(revision_id)}/assign", css_class="button button-secondary"))
        actions.append(link("Review decision", f"/manage/reviews/{object_id}/{quoted_path(revision_id)}", css_class="button button-primary"))

    actions.extend(
        [
            link("Mark suspect", f"/manage/objects/{object_id}/suspect", css_class="button button-secondary"),
            link("Supersede", f"/manage/objects/{object_id}/supersede", css_class="button button-secondary"),
        ]
    )
    return join_html(actions, " ")


def _manage_table(components, title: str, items: list[dict[str, object]], *, show_actions: bool = False) -> str:
    del show_actions
    rows = []
    for item in items:
        rows.append(
            [
                link(str(item["title"]), _manage_item_detail_href(item)),
                escape(item["revision_state"]),
                f'{escape(item["trust_state"])}<p class="cell-meta">{escape(item["posture"]["trust_summary"])}</p>',
                f'{escape(item["approval_state"])}<p class="cell-meta">{escape(item["posture"]["approval"]["summary"])}</p>',
                escape(", ".join(item["reasons"])),
                escape(item["owner"]),
                _manage_item_actions(item),
            ]
        )
    return components.section_card(
        title=title,
        eyebrow="Manage",
        body_html=components.queue_table(
            headers=["Title", "Revision", "Trust", "Approval", "Reasons", "Owner", "Actions"],
            rows=rows,
            table_id=title.lower().replace(" ", "-"),
        ) if rows else '<p class="empty-state-copy">No items in this queue.</p>',
    )


def register(router, runtime) -> None:
    def manage_queue_page(request: Request):
        queue = manage_queue(database_path=runtime.database_path)
        components = ComponentPresenter(runtime.template_renderer)
        overview_html = components.trust_summary(
            title="Manage queue posture",
            badges=[
                components.badge(label="Review required", value=len(queue["review_required"]), tone="pending"),
                components.badge(label="Stale", value=len(queue["stale_items"]), tone="warning"),
                components.badge(label="Weak evidence", value=len(queue["weak_evidence_items"]), tone="warning"),
                components.badge(label="Ownership gaps", value=len(queue["ownership_items"]), tone="danger"),
            ],
            summary="Review work, evidence weakness, stale content, and ownership ambiguity are grouped for direct action.",
        )
        tables_html = join_html(
            [
                _manage_table(components, "Review required", queue["review_required"], show_actions=True),
                _manage_table(components, "Drafts and rejected", queue["draft_items"]),
                _manage_table(components, "Stale items", queue["stale_items"]),
                _manage_table(components, "Weak evidence", queue["weak_evidence_items"]),
                _manage_table(components, "Ownership gaps", queue["ownership_items"]),
            ]
        )
        body = runtime.template_renderer.render(
            "pages/manage_queue.html",
            {"overview_html": overview_html, "tables_html": tables_html},
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_queue.html",
                page_title="Manage queue",
                headline="Review Queue",
                kicker="Manage",
                intro="Governance work is grouped by review state, staleness, evidence weakness, and ownership ambiguity.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
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
        summary_html = components.section_card(
            title="Supersession context",
            eyebrow="Manage",
            body_html=(
                f"<p><strong>{escape(detail['object']['title'])}</strong></p>"
                f"<p>Trust: {escape(detail['object']['trust_state'])} · Approval: {escape(detail['object']['approval_state'] or 'unknown')}</p>"
                f"<p>{escape(detail['posture']['trust_detail'])}</p>"
            ),
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
                + forms.button(label="Supersede object")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_object_form.html",
                page_title="Supersede object",
                headline="Supersede Object",
                kicker="Manage",
                intro="Supersession is a governed action. Capture the replacement and rationale so operators can follow the transition safely.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
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
        summary_html = components.section_card(
            title="Suspect posture context",
            eyebrow="Manage",
            body_html=(
                f"<p><strong>{escape(detail['object']['title'])}</strong></p>"
                f"<p>{escape(detail['posture']['trust_detail'])}</p>"
            ),
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
                + forms.button(label="Mark object suspect")
                + "</form>"
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_object_form.html",
                page_title="Mark object suspect",
                headline="Mark Object Suspect",
                kicker="Manage",
                intro="Use suspect posture when a dependency or upstream change may invalidate the guidance before a full revision is ready.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
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
        summary_html = components.section_card(
            title="Evidence status context",
            eyebrow="Evidence",
            body_html=(
                f"<p><strong>{escape(detail['object']['title'])}</strong></p>"
                f"<p>{escape(detail['evidence_status']['summary'])}</p>"
            ),
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
                headline="Revalidate Evidence",
                kicker="Evidence",
                intro="Request explicit evidence follow-up when snapshots, expiry windows, or supporting proofs need confirmation.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
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
        summary_html = components.section_card(
            title="Revision review context",
            eyebrow="Manage",
            body_html=(
                f"<p><strong>{escape(detail['object']['title'])}</strong> · revision #{escape(detail['revision']['revision_number'])}</p>"
                f"<p>State: {escape(detail['revision']['revision_state'])} · citations: {escape(len(detail['citations']))}</p>"
            ),
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
                headline="Review Assignment",
                kicker="Manage",
                intro="Inspect revision metadata and trust posture before sending review work to a specific operator.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
                page_context={"summary_html": summary_html, "assignment_html": assignment_html, "form_html": form_html},
            )
        )

    def review_decision_page(request: Request):
        object_id = request.route_value("object_id")
        revision_id = request.route_value("revision_id")
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        forms = FormPresenter(runtime.template_renderer)
        components = ComponentPresenter(runtime.template_renderer)
        approve_values = {
            "reviewer": request.form_value("reviewer"),
            "notes": request.form_value("notes"),
        }
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            action = request.form_value("decision")
            result = validate_decision_form(approve_values, require_notes=action == "reject")
            if result.is_valid:
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
            errors = result.errors
        summary_html = components.section_card(
            title="Decision context",
            eyebrow="Manage",
            body_html=(
                f"<p><strong>{escape(detail['object']['title'])}</strong> · revision #{escape(detail['revision']['revision_number'])}</p>"
                f"<p>Current state: {escape(detail['revision']['revision_state'])}</p>"
                f"<p>Assignments: {escape(len(detail['assignments']))} · citations: {escape(len(detail['citations']))}</p>"
            ),
        )
        decisions_html = join_html(
            [
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
                    eyebrow="Manage",
                    body_html=(
                        '<form class="governed-form" method="post">'
                        + forms.field(field_id="reviewer", label="Reviewer", control_html=forms.input(field_id="reviewer", name="reviewer", value=approve_values["reviewer"]), errors=errors.get("reviewer"))
                        + forms.field(field_id="notes", label="Decision notes", control_html=forms.textarea(field_id="notes", name="notes", value=approve_values["notes"], rows=4), hint="Required for rejection; optional for approval.", errors=errors.get("notes"))
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
                headline="Approval And Rejection",
                kicker="Manage",
                intro="Action consequences stay explicit: reviewers decide with audit context, assignment state, and evidence posture in view.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
                page_context={"summary_html": summary_html, "decisions_html": decisions_html},
            )
        )

    def audit_page(request: Request):
        object_id = request.query_value("object_id") or None
        events = audit_view(object_id=object_id, database_path=runtime.database_path)
        structured_events = event_history(
            entity_id=object_id,
            limit=20,
            database_path=runtime.database_path,
        )
        validation_runs = validation_run_history(database_path=runtime.database_path)
        components = ComponentPresenter(runtime.template_renderer)
        audit_html = components.section_card(
            title="Audit history",
            eyebrow="Manage",
            body_html=components.queue_table(
                headers=["Time", "Event", "Actor", "Object", "Revision", "Details"],
                rows=[
                    [
                        escape(format_timestamp(event["occurred_at"])),
                        escape(event["event_type"]),
                        escape(event["actor"]),
                        escape(event["object_id"] or ""),
                        escape(event["revision_id"] or ""),
                        escape(", ".join(f"{key}={value}" for key, value in event["details"].items() if value)),
                    ]
                    for event in events
                ],
                table_id="audit-history",
            ),
        )
        event_html = components.section_card(
            title="Structured events",
            eyebrow="Events",
            body_html=components.queue_table(
                headers=["Time", "Type", "Entity", "Actor", "Source", "Summary"],
                rows=[
                    [
                        escape(format_timestamp(event["occurred_at"])),
                        escape(event["event_type"]),
                        escape(f"{event['entity_type']}:{event['entity_id']}"),
                        escape(event["actor"]),
                        escape(event["source"]),
                        escape(
                            str(
                                event["payload"].get("summary")
                                or event["payload"].get("reason")
                                or event["payload"].get("trust_state")
                                or ""
                            )
                        ),
                    ]
                    for event in structured_events
                ],
                table_id="structured-events",
            ) if structured_events else '<p class="empty-state-copy">No structured events recorded.</p>',
        )
        validation_html = components.section_card(
            title="Validation runs",
            eyebrow="Manage",
            body_html=components.queue_table(
                headers=["Completed", "Run type", "Status", "Findings", "Run ID"],
                rows=[
                    [
                        escape(format_timestamp(run["completed_at"])),
                        escape(run["run_type"]),
                        escape(run["status"]),
                        escape(run["finding_count"]),
                        escape(run["run_id"]),
                    ]
                    for run in validation_runs[:20]
                ],
                table_id="audit-validation-runs",
            ),
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/manage_audit.html",
                page_title="Audit and governance",
                headline="Audit And Governance",
                kicker="Manage",
                intro="Governance-relevant history and validation outcomes are available without dropping to a CLI workflow.",
                active_nav="manage",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
                page_context={"audit_html": audit_html, "event_html": event_html, "validation_html": validation_html},
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
                headers=["Completed", "Run type", "Status", "Findings", "Run ID"],
                rows=[
                    [
                        escape(format_timestamp(run["completed_at"])),
                        escape(run["run_type"]),
                        escape(run["status"]),
                        escape(run["finding_count"]),
                        escape(run["run_id"]),
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
                headline="Validation Runs",
                kicker="Validation",
                intro="Recent validation outcomes stay accessible inside the operator shell for traceable governance review.",
                active_nav="validation",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
                action_bar_html=add_run_html,
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
                headline="Record Validation Run",
                kicker="Validation",
                intro="Validation outcomes are governance events too. Record what ran, what it found, and when it happened.",
                active_nav="validation",
                flash_html=flash_html_for_request(runtime, request),
                aside_html="",
                page_context={"form_html": form_html},
            )
        )

    router.add(["GET"], "/manage/queue", manage_queue_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/supersede", object_supersede_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/suspect", object_suspect_page)
    router.add(["GET", "POST"], "/manage/objects/{object_id}/evidence/revalidate", evidence_revalidation_page)
    router.add(["GET", "POST"], "/manage/reviews/{object_id}/{revision_id}/assign", review_assignment_page)
    router.add(["GET", "POST"], "/manage/reviews/{object_id}/{revision_id}", review_decision_page)
    router.add(["GET"], "/manage/audit", audit_page)
    router.add(["GET"], "/manage/validation-runs", validation_runs_page)
    router.add(["GET", "POST"], "/manage/validation-runs/new", validation_run_new_page)
