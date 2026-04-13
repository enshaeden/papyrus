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
    render_projection_overview_panel,
    render_projection_status_panel,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import review_queue_url
from papyrus.interfaces.web.view_helpers import (
    escape,
    format_timestamp,
    join_html,
    link,
    render_definition_rows,
    render_list,
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


def _review_item_detail_href(item: dict[str, object], *, role: str) -> str:
    return primary_surface_href(
        role=role,
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip()
        or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _review_item_actions(
    components: ComponentPresenter, item: dict[str, object], *, role: str
) -> str:
    return compact_action_menu_html(
        components,
        role=role,
        ui_projection=item.get("ui_projection"),
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip()
        or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
    )


def _governed_context_html(
    components: ComponentPresenter,
    *,
    role: str,
    detail: dict[str, object],
    status_title: str,
    action_id: str | None = None,
    action_title: str | None = None,
    show_actions: bool = False,
) -> str:
    object_id = str(detail["object"]["object_id"])
    revision_record = detail.get("revision") or detail.get("current_revision") or {}
    revision_id = str(revision_record.get("revision_id") or "").strip() or None
    panels = [
        (
            render_projection_overview_panel(
                components,
                role=role,
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


def render_review_cleanup_strip(*, cleanup_counts: dict[str, object]) -> str:
    return (
        '<section class="review-cleanup-strip" data-component="review-cleanup-strip" data-surface="review">'
        f"<span>Placeholder-heavy {escape(cleanup_counts.get('placeholder-heavy', 0))}</span>"
        f"<span>Legacy fallback {escape(cleanup_counts.get('legacy-blueprint-fallback', 0))}</span>"
        f"<span>Ownership gaps {escape(cleanup_counts.get('unclear-ownership', 0))}</span>"
        f"<span>Weak evidence {escape(cleanup_counts.get('weak-evidence', 0))}</span>"
        f"<span>Migration gaps {escape(cleanup_counts.get('migration-gaps', 0))}</span>"
        "</section>"
    )


def render_review_lane(
    *,
    role: str,
    title: str,
    items: list[dict[str, Any]],
    active_object_id: str,
    active_revision_id: str,
    action_html_resolver,
) -> str:
    if not items:
        return (
            '<section class="review-lane" data-component="review-lane" data-surface="review">'
            f'<h2>{escape(title)}</h2><p class="review-lane-empty">No items in this lane.</p></section>'
        )
    rows = []
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        is_selected = object_id == active_object_id and (
            not active_revision_id or revision_id == active_revision_id
        )
        use_guidance = projection_use_guidance(item.get("ui_projection"))
        rows.append(
            f"<tr{' class=\"is-selected\"' if is_selected else ''}{' aria-selected=\"true\"' if is_selected else ''}>"
            f'<td><a class="selected-row-link" href="{escape(review_queue_url(role))}?selected_object_id={escape(object_id)}&selected_revision_id={escape(revision_id)}">{escape(item["title"])}</a><span class="table-support">{escape(item.get("change_summary") or item.get("summary") or "")}</span></td>'
            f"<td>{escape(str(use_guidance.get('summary') or 'Review item'))}</td>"
            f"<td>{escape(', '.join(projection_reasons(item.get('ui_projection'))) or 'No explicit reasons')}</td>"
            f"<td>{escape(str(item.get('owner') or 'Unowned'))}</td>"
            f"<td>{action_html_resolver(item)}</td>"
            "</tr>"
        )
    return (
        '<section class="review-lane" data-component="review-lane" data-surface="review">'
        f"<h2>{escape(title)}</h2>"
        '<table class="workbench-table">'
        "<thead><tr><th>Guidance</th><th>Status</th><th>Why now</th><th>Owner</th><th>Action</th></tr></thead>"
        "<tbody>" + join_html(rows) + "</tbody></table></section>"
    )


def _selected_review_item(
    queue: dict[str, Any], *, selected_object_id: str, selected_revision_id: str
) -> dict[str, object] | None:
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
        if object_id == selected_object_id and (
            not selected_revision_id or revision_id == selected_revision_id
        ):
            return item
    return all_items[0]


def _review_context_panel(
    components: ComponentPresenter, item: dict[str, object], *, role: str
) -> str:
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
                        (
                            "Next action",
                            escape(use_guidance.get("next_action") or "Review this item"),
                        ),
                        ("Trust", escape(state.get("trust_state") or "unknown")),
                        ("Review", escape(state.get("revision_review_state") or "unknown")),
                        ("Owner", escape(str(item.get("owner") or "Unowned"))),
                    ]
                ),
            ]
        ),
        footer_html=join_html(
            [
                link(
                    "Open guidance",
                    _review_item_detail_href(item, role=role),
                    css_class="button button-secondary",
                ),
                _review_item_actions(components, item, role=role),
            ],
            " ",
        ),
        variant="selected-item",
        surface="review-queue",
    )


def _review_object_form_page(
    renderer: TemplateRenderer,
    *,
    role: str,
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
        role=role,
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
        active_nav="oversight",
        shell_variant="minimal",
        page_context={"summary_html": summary_html, "form_html": form_html},
    )


def present_review_queue_page(
    renderer: TemplateRenderer,
    *,
    role: str,
    queue: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    selected_item = _selected_review_item(
        queue,
        selected_object_id=selected_object_id,
        selected_revision_id=selected_revision_id,
    )
    active_object_id = str((selected_item or {}).get("object_id") or "")
    active_revision_id = str(
        (selected_item or {}).get("revision_id")
        or (selected_item or {}).get("current_revision_id")
        or ""
    )
    cleanup_counts = queue.get("cleanup_counts") or {}

    def lane_html(title: str, items: list[dict[str, Any]]) -> str:
        return render_review_lane(
            role=role,
            title=title,
            items=items,
            active_object_id=active_object_id,
            active_revision_id=active_revision_id,
            action_html_resolver=lambda item: _review_item_actions(components, item, role=role),
        )

    tables_html = join_html(
        [
            render_review_cleanup_strip(cleanup_counts=cleanup_counts),
            lane_html("Needs decision", queue["needs_decision"]),
            lane_html("Ready for review", queue["ready_for_review"]),
            lane_html("Needs revalidation", queue["needs_revalidation"]),
            lane_html("Drafts and rework", queue["draft_items"]),
            lane_html("Recently changed", queue["recently_changed"][:10]),
        ]
    )
    return _page_definition(
        page_template="pages/manage_queue.html",
        page_title="Review",
        headline="Review",
        active_nav="review",
        show_actor_links=False,
        aside_html=_review_context_panel(components, selected_item, role=role)
        if selected_item is not None
        else "",
        page_context={"tables_html": tables_html},
    )


def present_object_supersede_page(
    renderer: TemplateRenderer,
    *,
    role: str,
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
            control_html=forms.input(
                field_id="replacement_object_id",
                name="replacement_object_id",
                value=values["replacement_object_id"],
            ),
            hint="Use the governed object ID that replaces this content.",
            errors=errors.get("replacement_object_id"),
        )
        + forms.field(
            field_id="notes",
            label="Supersession rationale",
            control_html=forms.textarea(
                field_id="notes", name="notes", value=values["notes"], rows=4
            ),
            hint="Required. Explain why operators should stop relying on this object.",
            errors=errors.get("notes"),
        )
        + forms.button(label="Set replacement")
        + "</form>"
    )
    return _review_object_form_page(
        renderer,
        role=role,
        detail=detail,
        page_title="Supersede object",
        headline="Supersede guidance",
        action_id="supersede_object",
        action_title="Supersession contract",
        form_title="Supersede object",
        form_eyebrow="Oversight",
        form_body_html=form_body_html,
    )


def present_object_suspect_page(
    renderer: TemplateRenderer,
    *,
    role: str,
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
            control_html=forms.input(
                field_id="changed_entity_id",
                name="changed_entity_id",
                value=values["changed_entity_id"],
            ),
            hint="Optional identifier for the specific changed dependency.",
            errors=errors.get("changed_entity_id"),
        )
        + forms.field(
            field_id="reason",
            label="Suspect rationale",
            control_html=forms.textarea(
                field_id="reason", name="reason", value=values["reason"], rows=4
            ),
            hint="Required. Make the degradation legible to future operators and reviewers.",
            errors=errors.get("reason"),
        )
        + forms.button(label="Flag for review")
        + "</form>"
    )
    return _review_object_form_page(
        renderer,
        role=role,
        detail=detail,
        page_title="Mark object suspect",
        headline="Mark guidance suspect",
        action_id="mark_suspect",
        action_title="Suspect contract",
        form_title="Mark object suspect",
        form_eyebrow="Oversight",
        form_body_html=form_body_html,
    )


def present_object_archive_page(
    renderer: TemplateRenderer,
    *,
    role: str,
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
            control_html=forms.textarea(
                field_id="retirement_reason",
                name="retirement_reason",
                value=values["retirement_reason"],
                rows=4,
            ),
            hint="Required. State why operators should no longer treat this as active guidance.",
            errors=errors.get("retirement_reason"),
        )
        + forms.field(
            field_id="notes",
            label="Operator notes",
            control_html=forms.textarea(
                field_id="notes", name="notes", value=values["notes"], rows=3
            ),
            hint="Optional notes stored with the archive audit event.",
        )
        + render_acknowledgement_panel(
            components,
            forms,
            title="Required acknowledgements",
            required_acknowledgements=required_acknowledgements,
            selected_acknowledgements=selected_acknowledgements,
            operator_message=str(
                archive_action.get("detail")
                or "Review the required acknowledgements before continuing."
            ),
            errors=errors.get("acknowledgements"),
        )
        + forms.button(label="Archive guidance")
        + "</form>"
    )
    return _review_object_form_page(
        renderer,
        role=role,
        detail=detail,
        page_title="Archive object",
        headline="Archive guidance",
        action_id="archive_object",
        action_title="Archive contract",
        form_title="Archive object",
        form_eyebrow="Oversight",
        form_body_html=form_body_html,
    )


def present_evidence_revalidation_page(
    renderer: TemplateRenderer,
    *,
    role: str,
    detail: dict[str, Any],
    values: dict[str, str],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    form_body_html = (
        '<form class="governed-form" method="post">'
        + forms.field(
            field_id="notes",
            label="Revalidation notes",
            control_html=forms.textarea(
                field_id="notes", name="notes", value=values["notes"], rows=4
            ),
            hint="Optional notes for the next reviewer or operator.",
        )
        + forms.button(label="Request evidence revalidation")
        + "</form>"
    )
    return _review_object_form_page(
        renderer,
        role=role,
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
    role: str,
    detail: dict[str, Any],
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    components = ComponentPresenter(renderer)
    summary_html = _governed_context_html(
        components,
        role=role,
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
        eyebrow="Oversight",
        body_html=(
            '<form class="governed-form" method="post">'
            + forms.field(
                field_id="reviewer",
                label="Reviewer",
                control_html=forms.input(
                    field_id="reviewer", name="reviewer", value=values["reviewer"]
                ),
                errors=errors.get("reviewer"),
            )
            + forms.field(
                field_id="due_at",
                label="Due date",
                control_html=forms.input(
                    field_id="due_at", name="due_at", value=values["due_at"], input_type="date"
                ),
                errors=errors.get("due_at"),
            )
            + forms.field(
                field_id="notes",
                label="Assignment notes",
                control_html=forms.textarea(
                    field_id="notes", name="notes", value=values["notes"], rows=3
                ),
            )
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
        page_context={
            "summary_html": summary_html,
            "assignment_html": assignment_html,
            "form_html": form_html,
        },
    )


def present_review_decision_page(
    renderer: TemplateRenderer,
    *,
    role: str,
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
        role=role,
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
                        render_list(
                            [escape(item) for item in findings], css_class="validation-findings"
                        )
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
                    + forms.field(
                        field_id="reviewer",
                        label="Reviewer",
                        control_html=forms.input(
                            field_id="reviewer", name="reviewer", value=values["reviewer"]
                        ),
                        errors=errors.get("reviewer"),
                    )
                    + forms.field(
                        field_id="notes",
                        label="Decision notes",
                        control_html=forms.textarea(
                            field_id="notes", name="notes", value=values["notes"], rows=4
                        ),
                        hint="Required for rejection; optional for approval. Use notes to explain the decision or the reason for a block.",
                        errors=errors.get("notes"),
                    )
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
