from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

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
    render_projection_overview_panel,
    render_projection_status_panel,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import (
    escape,
    format_timestamp,
    join_html,
    link,
    quoted_path,
    render_definition_rows,
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
    show_actor_links: bool = False,
    actions_html: str = "",
) -> dict[str, Any]:
    page = {
        "page_template": page_template,
        "page_title": page_title,
        "page_header": {
            "headline": headline,
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
    object_id = str(detail["object"]["object_id"])
    revision_record = (detail.get("revision") or detail.get("current_revision") or {})
    revision_id = str(revision_record.get("revision_id") or "").strip() or None
    panels = [
        (
            render_projection_overview_panel(
                components,
                title=status_title,
                ui_projection=detail.get("ui_projection"),
                object_id=object_id,
                revision_id=revision_id,
            )
            if show_actions
            else render_projection_status_panel(
                components,
                title=status_title,
                ui_projection=detail.get("ui_projection"),
            )
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
    return join_html(panels)


def _manage_table(
    components: ComponentPresenter,
    *,
    title: str,
    items: list[dict[str, object]],
    selected_object_id: str,
    selected_revision_id: str,
) -> str:
    rows = []
    row_attrs: list[dict[str, object]] = []
    for item in items:
        use_guidance = projection_use_guidance(item.get("ui_projection"))
        state = projection_state(item.get("ui_projection"))
        reasons = projection_reasons(item.get("ui_projection"))
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        selection_href = "/review?" + urlencode(
            {
                key: value
                for key, value in {
                    "selected_object_id": object_id,
                    "selected_revision_id": revision_id,
                }.items()
                if value
            }
        )
        rows.append(
            [
                components.decision_cell(
                    title_html=link(str(item["title"]), selection_href, css_class="selected-row-link"),
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
        row_attrs.append(
            {"aria-selected": "true", "class": "is-selected"}
            if object_id == selected_object_id and (not selected_revision_id or revision_id == selected_revision_id)
            else {}
        )
    return components.context_panel(
        title=title,
        eyebrow="Stewardship",
        body_html=(
            components.queue_table(
                headers=["Guidance", "Status", "Attention", "Steward", "Next action"],
                rows=rows,
                row_attrs=row_attrs,
                table_id=title.lower().replace(" ", "-"),
                variant="dense-table",
            )
            if rows
            else '<p class="empty-state-copy">No items in this queue.</p>'
        ),
    )


def _selected_manage_item(queue: dict[str, Any], *, selected_object_id: str, selected_revision_id: str) -> dict[str, object] | None:
    ordered_groups = (
        queue["ready_for_review"],
        queue["needs_decision"],
        queue["needs_revalidation"],
        queue["draft_items"],
        queue["recently_changed"][:10],
        queue["superseded_items"],
    )
    all_items = [item for group in ordered_groups for item in group]
    if not all_items:
        return None
    for item in all_items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        if object_id == selected_object_id and (not selected_revision_id or revision_id == selected_revision_id):
            return item
    return all_items[0]


def _manage_context_panel(components: ComponentPresenter, item: dict[str, object]) -> str:
    state = projection_state(item.get("ui_projection"))
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    reasons = projection_reasons(item.get("ui_projection"))
    return components.context_panel(
        title=str(item["title"]),
        eyebrow="Selected item",
        body_html=join_html(
            [
                f"<p><strong>{escape(use_guidance.get('summary') or 'Governed guidance unavailable')}</strong></p>",
                f"<p>{escape(use_guidance.get('detail') or 'Papyrus did not return governed detail for this queue item.')}</p>",
                render_list([escape(reason) for reason in reasons], css_class="panel-list")
                or '<p class="empty-state-copy">No explicit reasons were attached to this queue item.</p>',
                render_definition_rows(
                    [
                        ("Next action", escape(use_guidance.get("next_action") or "Review this item")),
                        ("Trust", escape(state.get("trust_state") or "unknown")),
                        ("Review", escape(state.get("revision_review_state") or "unknown")),
                        ("Owner", escape(str(item.get("owner") or "Unowned"))),
                    ]
                ),
            ]
        ),
        footer_html=join_html(
            [
                link("Open guidance", _manage_item_detail_href(item), css_class="button button-secondary"),
                _manage_item_actions(components, item),
            ],
            " ",
        ),
        variant="selected-item",
        surface="review-queue",
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
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    selected_item = _selected_manage_item(
        queue,
        selected_object_id=selected_object_id,
        selected_revision_id=selected_revision_id,
    )
    active_object_id = str((selected_item or {}).get("object_id") or "")
    active_revision_id = str((selected_item or {}).get("revision_id") or (selected_item or {}).get("current_revision_id") or "")
    cleanup_counts = queue.get("cleanup_counts") or {}

    def table_html(title: str, items: list[dict[str, Any]]) -> str:
        if not items:
            return (
                '<section class="review-lane" data-component="review-lane" data-surface="review">'
                f"<h2>{escape(title)}</h2><p class=\"review-lane-empty\">No items in this lane.</p></section>"
            )
        rows = []
        for item in items:
            object_id = str(item.get("object_id") or "")
            revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
            is_selected = object_id == active_object_id and (not active_revision_id or revision_id == active_revision_id)
            use_guidance = projection_use_guidance(item.get("ui_projection"))
            rows.append(
                (
                    f'<tr{" class=\"is-selected\"" if is_selected else ""}{" aria-selected=\"true\"" if is_selected else ""}>'
                    f'<td><a class="selected-row-link" href="/review?selected_object_id={escape(object_id)}&selected_revision_id={escape(revision_id)}">{escape(item["title"])}</a><span class="table-support">{escape(item.get("change_summary") or item.get("summary") or "")}</span></td>'
                    f'<td>{escape(str(use_guidance.get("summary") or "Review item"))}</td>'
                    f'<td>{escape(", ".join(projection_reasons(item.get("ui_projection"))) or "No explicit reasons")}</td>'
                    f'<td>{escape(str(item.get("owner") or "Unowned"))}</td>'
                    f'<td>{_manage_item_actions(components, item)}</td>'
                    "</tr>"
                )
            )
        return (
            '<section class="review-lane" data-component="review-lane" data-surface="review">'
            f"<h2>{escape(title)}</h2>"
            '<table class="workbench-table">'
            "<thead><tr><th>Guidance</th><th>Status</th><th>Why now</th><th>Owner</th><th>Action</th></tr></thead>"
            "<tbody>"
            + join_html(rows)
            + "</tbody></table></section>"
        )

    overview_html = (
        '<section class="review-workbench-hero" data-component="review-hero" data-surface="review">'
        "<h1>Make review decisions with the blocking context visible.</h1>"
        "<p>Review is a dense workbench: each lane is grouped by the decision it needs, not by decorative governance chrome.</p>"
        '<div class="review-workbench-metrics">'
        f'<article><p>{escape(len(queue["ready_for_review"]))}</p><span>Ready for review</span></article>'
        f'<article><p>{escape(len(queue["needs_decision"]))}</p><span>Needs decision</span></article>'
        f'<article><p>{escape(len(queue["needs_revalidation"]))}</p><span>Needs revalidation</span></article>'
        f'<article><p>{escape(len(queue["recently_changed"][:10]))}</p><span>Recently changed</span></article>'
        "</div></section>"
    )
    cleanup_html = (
        '<section class="review-cleanup-strip" data-component="cleanup-strip" data-surface="review">'
        f'<span>Placeholder-heavy {escape(cleanup_counts.get("placeholder-heavy", 0))}</span>'
        f'<span>Legacy fallback {escape(cleanup_counts.get("legacy-blueprint-fallback", 0))}</span>'
        f'<span>Ownership gaps {escape(cleanup_counts.get("unclear-ownership", 0))}</span>'
        f'<span>Weak evidence {escape(cleanup_counts.get("weak-evidence", 0))}</span>'
        f'<span>Migration gaps {escape(cleanup_counts.get("migration-gaps", 0))}</span>'
        "</section>"
    )
    tables_html = join_html(
        [
            cleanup_html,
            table_html("Needs decision", queue["needs_decision"]),
            table_html("Ready for review", queue["ready_for_review"]),
            table_html("Needs revalidation", queue["needs_revalidation"]),
            table_html("Drafts and rework", queue["draft_items"]),
            table_html("Recently changed", queue["recently_changed"][:10]),
        ]
    )
    return _page_definition(
        page_template="pages/manage_queue.html",
        page_title="Review / Approvals",
        headline="Review queue",
        active_nav="review",
        show_actor_links=False,
        aside_html=_manage_context_panel(components, selected_item) if selected_item is not None else "",
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
    assignment_html = components.surface_panel(
        title="Current assignments",
        eyebrow="Audit",
        body_html=components.list_body(
            items=[
                f"{escape(assignment['reviewer'])} · {escape(assignment['state'])} · assigned {escape(format_timestamp(assignment['assigned_at']))}"
                for assignment in detail["assignments"]
            ],
            empty_label="No reviewers assigned yet.",
        ),
        tone="context",
        variant="assignments",
        surface="review-assignment",
    )
    form_html = components.surface_panel(
        title="Assign reviewer",
        eyebrow="Manage",
        body_html=(
            '<form class="governed-form" method="post">'
            + forms.field(field_id="reviewer", label="Reviewer", control_html=forms.input(field_id="reviewer", name="reviewer", value=values["reviewer"]), errors=errors.get("reviewer"))
            + forms.field(field_id="due_at", label="Due date", control_html=forms.input(field_id="due_at", name="due_at", value=values["due_at"], input_type="date"), errors=errors.get("due_at"))
            + forms.field(field_id="notes", label="Assignment notes", control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=3))
            + forms.button(label="Assign reviewer", action_id="assign_reviewer")
            + "</form>"
        ),
        variant="assignment-form",
        surface="review-assignment",
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
            components.surface_panel(
                title="Revision audit",
                eyebrow="Audit",
                body_html=components.list_body(
                    items=[
                        f"{escape(format_timestamp(event['occurred_at']))} · {escape(event['event_type'])} · {escape(event['actor'])}"
                        for event in detail["audit_events"]
                    ],
                    empty_label="No revision audit events recorded.",
                ),
                tone="context",
                variant="revision-audit",
                surface="review-decision",
            ),
            components.section_card(
                title="Approve or reject",
                eyebrow="Review",
                body_html=(
                    '<form class="governed-form" method="post">'
                    + forms.field(field_id="reviewer", label="Reviewer", control_html=forms.input(field_id="reviewer", name="reviewer", value=values["reviewer"]), errors=errors.get("reviewer"))
                    + forms.field(field_id="notes", label="Decision notes", control_html=forms.textarea(field_id="notes", name="notes", value=values["notes"], rows=4), hint="Required for rejection; optional for approval. Use notes to explain the decision or the reason for a block.", errors=errors.get("notes"))
                    + '<div class="button-row">'
                    + '<button class="button button-primary" type="submit" name="decision" value="approve" data-component="button" data-action-id="approve_revision">Approve revision</button>'
                    + '<button class="button button-danger" type="submit" name="decision" value="reject" data-component="button" data-action-id="reject_revision">Reject revision</button>'
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
    del renderer
    filter_controls_html = (
        '<form class="activity-filters" method="get" action="/activity">'
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
    summary_html = (
        '<section class="activity-hero" data-component="activity-hero" data-surface="activity">'
        "<h1>See consequences before payload detail.</h1>"
        "<p>Activity is consequence-first: what changed, what it affected, and what to do next stay in the primary scan path. Raw audit payloads stay behind disclosure.</p>"
        '<div class="activity-metrics">'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "service_changes"))}</p><span>Service changes</span></article>'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "evidence_degradation"))}</p><span>Evidence issues</span></article>'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "validation_failures"))}</p><span>Validation failures</span></article>'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "manual_suspect_marks"))}</p><span>Suspect marks</span></article>'
        "</div></section>"
    )
    event_html = (
        join_html(
            [
                (
                    '<article class="activity-event" data-component="activity-event" data-surface="activity">'
                    f'<p class="activity-event-kicker">{escape(event["group"].replace("_", " "))} · {escape(format_timestamp(event["occurred_at"]))}</p>'
                    f'<h2>{escape(event["what_happened"])}</h2>'
                    f'<p class="activity-event-affected">{escape(str(event["entity_type"]) + ":" + str(event["entity_id"]))}</p>'
                    f'<p class="activity-event-next">{escape(event["next_action"])}</p>'
                    '<details class="activity-event-details"><summary>Show audit details</summary>'
                    f'<pre>{escape(", ".join(str(key) + "=" + str(value) for key, value in event["payload"].items() if value) or "No extra payload details")}</pre>'
                    "</details></article>"
                )
                for event in structured_events
            ]
        )
        if structured_events
        else '<section class="activity-empty"><h2>No matching activity</h2><p>Adjust the filter or wait for the next recorded event.</p></section>'
    )
    audit_html = (
        '<section class="activity-audit-log" data-component="audit-log" data-surface="activity">'
        "<h2>Audit log</h2>"
        '<div class="activity-audit-list">'
        + join_html(
            [
                (
                    '<article class="activity-audit-item">'
                    f'<p>{escape(event["event_type"])} · {escape(format_timestamp(event["occurred_at"]))} · {escape(event["actor"])}</p>'
                    f'<p>{escape(event["object_id"] or "No object")} · {escape(event["revision_id"] or "No revision")}</p>'
                    "</article>"
                )
                for event in events[:20]
            ]
        )
        + "</div></section>"
    )
    validation_html = (
        '<section class="activity-validation" data-component="validation-log" data-surface="activity">'
        "<h2>Validation runs</h2>"
        '<div class="activity-validation-list">'
        + join_html(
            [
                (
                    '<article class="activity-validation-item">'
                    f'<p>{escape(run["run_type"])} · {escape(run["status"])} · findings {escape(run["finding_count"])}</p>'
                    f'<p>{escape(format_timestamp(run["completed_at"]))}</p>'
                    "</article>"
                )
                for run in validation_runs[:20]
            ]
        )
        + "</div></section>"
    )
    return _page_definition(
        page_template="pages/manage_audit.html",
        page_title="Activity / History",
        headline="Activity",
        active_nav="activity",
        show_actor_links=False,
        page_context={
            "summary_html": summary_html,
            "filter_bar_html": filter_controls_html,
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
