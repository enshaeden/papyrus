from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.commands import approve_revision_command, assign_reviewer_command, reject_revision_command
from papyrus.application.queries import audit_view, manage_queue, review_detail, validation_run_history
from papyrus.interfaces.web.forms.review_forms import validate_assignment_form, validate_decision_form
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path


def _manage_table(components, title: str, items: list[dict[str, object]], *, show_actions: bool = False) -> str:
    rows = []
    for item in items:
        actions = ""
        if show_actions and item.get("revision_id"):
            actions = join_html(
                [
                    link("Assign", f"/manage/reviews/{quoted_path(str(item['object_id']))}/{quoted_path(str(item['revision_id']))}/assign", css_class="button button-secondary"),
                    link("Decide", f"/manage/reviews/{quoted_path(str(item['object_id']))}/{quoted_path(str(item['revision_id']))}", css_class="button button-secondary"),
                ],
                " ",
            )
        rows.append(
            [
                link(str(item["title"]), f"/objects/{quoted_path(str(item['object_id']))}"),
                escape(item["revision_state"]),
                escape(item["trust_state"]),
                escape(item["approval_state"]),
                escape(", ".join(item["reasons"])),
                escape(item["owner"]),
                actions,
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
                    object_id=object_id,
                    revision_id=revision_id,
                    reviewer=str(result.cleaned_data["reviewer"]),
                    actor="papyrus-web",
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
                        object_id=object_id,
                        revision_id=revision_id,
                        reviewer=str(result.cleaned_data["reviewer"]),
                        actor="papyrus-web",
                        notes=result.cleaned_data["notes"],
                    )
                    return redirect_response(
                        f"/objects/{quoted_path(object_id)}?notice={quote_plus('Revision approved')}"
                    )
                reject_revision_command(
                    database_path=runtime.database_path,
                    object_id=object_id,
                    revision_id=revision_id,
                    reviewer=str(result.cleaned_data["reviewer"]),
                    actor="papyrus-web",
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
        validation_runs = validation_run_history(database_path=runtime.database_path)
        components = ComponentPresenter(runtime.template_renderer)
        audit_html = components.section_card(
            title="Audit history",
            eyebrow="Manage",
            body_html=components.queue_table(
                headers=["Time", "Event", "Actor", "Object", "Revision"],
                rows=[
                    [
                        escape(format_timestamp(event["occurred_at"])),
                        escape(event["event_type"]),
                        escape(event["actor"]),
                        escape(event["object_id"] or ""),
                        escape(event["revision_id"] or ""),
                    ]
                    for event in events
                ],
                table_id="audit-history",
            ),
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
                page_context={"audit_html": audit_html, "validation_html": validation_html},
            )
        )

    def validation_runs_page(request: Request):
        runs = validation_run_history(database_path=runtime.database_path)
        components = ComponentPresenter(runtime.template_renderer)
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
                page_context={"validation_table_html": validation_table_html},
            )
        )

    router.add(["GET"], "/manage/queue", manage_queue_page)
    router.add(["GET", "POST"], "/manage/reviews/{object_id}/{revision_id}/assign", review_assignment_page)
    router.add(["GET", "POST"], "/manage/reviews/{object_id}/{revision_id}", review_decision_page)
    router.add(["GET"], "/manage/audit", audit_page)
    router.add(["GET"], "/manage/validation-runs", validation_runs_page)
