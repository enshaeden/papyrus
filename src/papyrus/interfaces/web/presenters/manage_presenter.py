from __future__ import annotations

from typing import Any

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
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import (
    escape,
    format_timestamp,
    join_html,
    link,
    quoted_path,
    render_list,
    tone_for_review_state,
    tone_for_trust,
)


def _page_definition(
    *,
    page_template: str,
    page_title: str,
    headline: str,
    active_nav: str,
    page_context: dict[str, Any],
    aside_html: str = "",
    shell_variant: str | None = None,
    show_actor_banner: bool = False,
    show_actor_links: bool = False,
    actions_html: str = "",
) -> dict[str, Any]:
    page = {
        "page_template": page_template,
        "page_title": page_title,
        "page_header": {
            "headline": headline,
            "show_actor_banner": show_actor_banner,
            "show_actor_links": show_actor_links,
        },
        "active_nav": active_nav,
        "aside_html": aside_html,
        "page_context": page_context,
    }
    if actions_html:
        page["page_header"]["actions_html"] = actions_html
    if shell_variant is not None:
        page["shell_variant"] = shell_variant
    return page


def present_warning_flash(
    renderer: TemplateRenderer,
    *,
    title: str,
    body: str,
) -> str:
    return FormPresenter(renderer).flash(title=title, body=body, tone="warning")


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


def _manage_table(
    components: ComponentPresenter,
    *,
    title: str,
    items: list[dict[str, object]],
) -> str:
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
                    meta=[escape(str(item.get("object_id") or ""))],
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
                            label="Review",
                            value=str(state.get("revision_review_state") or "unknown"),
                            tone=tone_for_review_state(str(state.get("revision_review_state") or "unknown")),
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
                components.decision_cell(title_html=escape(str(item["owner"]))),
                _manage_item_actions(components, item),
            ]
        )
    return components.section_card(
        title=title,
        eyebrow="Stewardship",
        body_html=(
            components.queue_table(
                headers=["Guidance", "Status", "Attention", "Steward", "Next action"],
                rows=rows,
                table_id=title.lower().replace(" ", "-"),
            )
            if rows
            else '<p class="empty-state-copy">No items in this queue.</p>'
        ),
    )


def _manage_object_form_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    page_title: str,
    headline: str,
    action_id: str,
    action_title: str,
    form_title: str,
    form_eyebrow: str,
    form_body_html: str,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    summary_html = _governed_context_html(
        components,
        detail=detail,
        status_title=f"{detail['object']['title']} governed posture",
        action_id=action_id,
        action_title=action_title,
    )
    form_html = components.section_card(
        title=form_title,
        eyebrow=form_eyebrow,
        body_html=form_body_html,
    )
    return _page_definition(
        page_template="pages/manage_object_form.html",
        page_title=page_title,
        headline=headline,
        active_nav="health",
        shell_variant="minimal",
        page_context={"summary_html": summary_html, "form_html": form_html},
    )


def present_manage_queue_page(
    renderer: TemplateRenderer,
    *,
    queue: dict[str, Any],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
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
            _manage_table(components, title="Ready for review", items=queue["ready_for_review"]),
            _manage_table(components, title="Needs decision", items=queue["needs_decision"]),
            _manage_table(components, title="Needs revalidation", items=queue["needs_revalidation"]),
            _manage_table(components, title="Drafts and rework", items=queue["draft_items"]),
            _manage_table(components, title="Recently changed", items=queue["recently_changed"][:10]),
            _manage_table(components, title="Superseded or deprecated guidance", items=queue["superseded_items"]),
        ]
    )
    return _page_definition(
        page_template="pages/manage_queue.html",
        page_title="Review / Approvals",
        headline="Review queue",
        active_nav="review",
        show_actor_banner=True,
        show_actor_links=True,
        page_context={"overview_html": overview_html, "tables_html": tables_html},
    )


def present_object_supersede_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    form_body_html = (
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
    )
    return _manage_object_form_page(
        renderer,
        detail=detail,
        page_title="Supersede object",
        headline="Supersede guidance",
        action_id="supersede_object",
        action_title="Supersession contract",
        form_title="Supersede object",
        form_eyebrow="Manage",
        form_body_html=form_body_html,
    )


def present_object_suspect_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    form_body_html = (
        '<form class="governed-form" method="post">'
        + forms.field(
            field_id="changed_entity_type",
            label="Changed entity type",
            control_html=forms.input(
                field_id="changed_entity_type",
                name="changed_entity_type",
                value=values["changed_entity_type"],
                placeholder="service",
            ),
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
    )
    return _manage_object_form_page(
        renderer,
        detail=detail,
        page_title="Mark object suspect",
        headline="Mark guidance suspect",
        action_id="mark_suspect",
        action_title="Suspect contract",
        form_title="Mark object suspect",
        form_eyebrow="Manage",
        form_body_html=form_body_html,
    )


def present_object_archive_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    values: dict[str, str],
    errors: dict[str, list[str]],
    selected_acknowledgements: list[str],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    components = ComponentPresenter(renderer)
    archive_action = action_descriptor(detail.get("ui_projection"), "archive_object") or {}
    required_acknowledgements = [
        str(item)
        for item in ((archive_action.get("policy") or {}).get("required_acknowledgements") or [])
    ]
    form_body_html = (
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
    )
    return _manage_object_form_page(
        renderer,
        detail=detail,
        page_title="Archive object",
        headline="Archive guidance",
        action_id="archive_object",
        action_title="Archive contract",
        form_title="Archive object",
        form_eyebrow="Manage",
        form_body_html=form_body_html,
    )


def present_evidence_revalidation_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    values: dict[str, str],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    form_body_html = (
        '<form class="governed-form" method="post">'
        + forms.field(
            field_id="notes",
            label="Revalidation notes",
            control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=4),
            hint="Optional notes for the next reviewer or operator.",
        )
        + forms.button(label="Request evidence revalidation")
        + "</form>"
    )
    return _manage_object_form_page(
        renderer,
        detail=detail,
        page_title="Revalidate evidence",
        headline="Revalidate evidence",
        action_id="request_evidence_revalidation",
        action_title="Evidence follow-up contract",
        form_title="Revalidate evidence",
        form_eyebrow="Evidence",
        form_body_html=form_body_html,
    )


def present_review_assignment_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    components = ComponentPresenter(renderer)
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
    return _page_definition(
        page_template="pages/review_assignment.html",
        page_title="Assign reviewer",
        headline="Assign reviewer",
        active_nav="review",
        shell_variant="minimal",
        page_context={"summary_html": summary_html, "assignment_html": assignment_html, "form_html": form_html},
    )


def present_review_decision_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    impact: dict[str, Any],
    preview: Any,
    findings: list[str],
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    components = ComponentPresenter(renderer)
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
                    + forms.field(field_id="reviewer", label="Reviewer", control_html=forms.input(field_id="reviewer", name="reviewer", value=values["reviewer"]), errors=errors.get("reviewer"))
                    + forms.field(field_id="notes", label="Decision notes", control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=4), hint="Required for rejection; optional for approval. Use notes to explain the decision or the reason for a block.", errors=errors.get("notes"))
                    + '<div class="button-row">'
                    + '<button class="button button-primary" type="submit" name="decision" value="approve">Approve revision</button>'
                    + '<button class="button button-danger" type="submit" name="decision" value="reject">Reject revision</button>'
                    + "</div></form>"
                ),
            ),
        ]
    )
    return _page_definition(
        page_template="pages/manage_review_decision.html",
        page_title="Review decision",
        headline="Review decision",
        active_nav="review",
        shell_variant="minimal",
        page_context={"summary_html": summary_html, "decisions_html": decisions_html},
    )


def present_audit_page(
    renderer: TemplateRenderer,
    *,
    events: list[dict[str, Any]],
    structured_events: list[dict[str, Any]],
    validation_runs: list[dict[str, Any]],
    object_id: str | None,
    selected_group: str,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
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
    return _page_definition(
        page_template="pages/manage_audit.html",
        page_title="Activity / History",
        headline="Activity",
        active_nav="activity",
        show_actor_banner=True,
        show_actor_links=True,
        page_context={
            "summary_html": summary_html,
            "filter_bar_html": components.filter_bar(title="Activity filters", controls_html=filter_controls_html),
            "audit_html": audit_html,
            "event_html": event_html,
            "validation_html": validation_html,
        },
    )


def present_validation_runs_page(
    renderer: TemplateRenderer,
    *,
    runs: list[dict[str, Any]],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
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
    return _page_definition(
        page_template="pages/manage_validation_runs.html",
        page_title="Validation runs",
        headline="Validation runs",
        active_nav="activity",
        show_actor_banner=True,
        show_actor_links=True,
        actions_html=add_run_html,
        page_context={"validation_table_html": validation_table_html},
    )


def present_validation_run_new_page(
    renderer: TemplateRenderer,
    *,
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    components = ComponentPresenter(renderer)
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
    return _page_definition(
        page_template="pages/manage_validation_run_new.html",
        page_title="Record validation run",
        headline="Record validation run",
        active_nav="activity",
        shell_variant="minimal",
        page_context={"form_html": form_html},
    )
