from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import READER_ROLE
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.urls import (
    archive_url,
    evidence_revalidation_url,
    object_url,
    review_assignment_url,
    review_decision_url,
    supersede_url,
    suspect_url,
    write_object_start_url,
    write_object_url,
    write_submit_url,
)
from papyrus.interfaces.web.view_helpers import (
    button_form,
    escape,
    join_html,
    link,
    render_definition_rows,
    render_list,
)

ACTION_AVAILABILITY_TONES = {
    "allowed": "approved",
    "no_op": "context",
    "illegal": "warning",
}

ACTION_AVAILABILITY_LABELS = {
    "allowed": "Allowed",
    "no_op": "No-op",
    "illegal": "Blocked",
}


def workflow_rows(projection: dict[str, Any] | None) -> list[dict[str, str]]:
    rows = (projection or {}).get("rows", [])
    return [
        {
            "label": str(row.get("label") or "").strip(),
            "value": str(row.get("value") or "").strip(),
        }
        for row in rows
        if isinstance(row, dict) and str(row.get("label") or "").strip()
    ]


def workflow_warnings(projection: dict[str, Any] | None) -> list[str]:
    return [str(item) for item in (projection or {}).get("warnings", []) if str(item).strip()]


def workflow_reasons(projection: dict[str, Any] | None) -> list[str]:
    return [str(item) for item in (projection or {}).get("reasons", []) if str(item).strip()]


def workflow_actions(projection: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [
        dict(action) for action in (projection or {}).get("actions", []) if isinstance(action, dict)
    ]


def projection_state(ui_projection: dict[str, Any] | None) -> dict[str, Any]:
    return dict((ui_projection or {}).get("state") or {})


def projection_use_guidance(ui_projection: dict[str, Any] | None) -> dict[str, Any]:
    return dict((ui_projection or {}).get("use_guidance") or {})


def projection_reasons(ui_projection: dict[str, Any] | None) -> list[str]:
    return [str(item) for item in (ui_projection or {}).get("reasons", [])]


def projection_actions(ui_projection: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [
        dict(action)
        for action in (ui_projection or {}).get("actions", [])
        if isinstance(action, dict)
    ]


def action_descriptor(
    ui_projection: dict[str, Any] | None, action_id: str
) -> dict[str, Any] | None:
    for action in projection_actions(ui_projection):
        if str(action.get("action_id") or "") == action_id:
            return action
    return None


def authoring_entry_label(
    *,
    ui_projection: dict[str, Any] | None,
    current_revision_id: str | None,
) -> str | None:
    state = projection_state(ui_projection)
    revision_state = str(state.get("revision_review_state") or "").strip()
    if not str(current_revision_id or "").strip():
        return "Draft first revision"
    if revision_state in {"in_progress", "rejected"}:
        return "Continue draft"
    return None


def authoring_entry_href(
    *,
    role: str,
    object_id: str,
    ui_projection: dict[str, Any] | None,
    current_revision_id: str | None,
) -> str | None:
    state = projection_state(ui_projection)
    revision_state = str(state.get("revision_review_state") or "").strip()
    if revision_state not in {"in_progress", "rejected"} or not str(current_revision_id or "").strip():
        return None
    return write_object_url(object_id, revision_id=str(current_revision_id)) + "#revision-form"


def authoring_entry_start_action(
    *,
    object_id: str,
    ui_projection: dict[str, Any] | None,
    current_revision_id: str | None,
) -> str | None:
    if str(current_revision_id or "").strip():
        return None
    if (
        authoring_entry_label(ui_projection=ui_projection, current_revision_id=current_revision_id)
        is None
    ):
        return None
    return write_object_start_url(object_id)


def authoring_entry_html(
    *,
    role: str,
    object_id: str,
    ui_projection: dict[str, Any] | None,
    current_revision_id: str | None,
    label_override: str | None = None,
    allow_start_when_not_in_draft_state: bool = False,
) -> str | None:
    state = projection_state(ui_projection)
    revision_state = str(state.get("revision_review_state") or "").strip()
    if str(current_revision_id or "").strip() and revision_state in {"in_progress", "rejected"}:
        return link(
            label_override or "Continue draft",
            authoring_entry_href(
                role=role,
                object_id=object_id,
                ui_projection=ui_projection,
                current_revision_id=current_revision_id,
            )
            or "#",
            css_class="button button-primary",
            attrs={
                "data-component": "action-link",
                "data-action-id": "authoring_entry",
            },
        )
    if not str(current_revision_id or "").strip() or allow_start_when_not_in_draft_state:
        return button_form(
            action=write_object_start_url(object_id),
            label=label_override
            or authoring_entry_label(
                ui_projection=ui_projection, current_revision_id=current_revision_id
            )
            or "Start draft",
            css_class="button button-primary",
            button_attrs={"data-action-id": "authoring_entry"},
        )
    return None


def action_href(
    *,
    role: str,
    action_id: str,
    object_id: str,
    revision_id: str | None,
) -> str | None:
    if action_id == "submit_for_review" and revision_id:
        return write_submit_url(object_id, revision_id)
    if action_id == "assign_reviewer" and revision_id:
        return review_assignment_url(object_id, revision_id)
    if action_id == "review_decision" and revision_id:
        return review_decision_url(object_id, revision_id)
    if action_id == "mark_suspect":
        return suspect_url(object_id)
    if action_id == "supersede_object":
        return supersede_url(object_id)
    if action_id == "archive_object":
        return archive_url(object_id)
    if action_id == "request_evidence_revalidation":
        return evidence_revalidation_url(object_id)
    return None


def primary_surface_href(
    *,
    role: str,
    object_id: str,
    revision_id: str | None,
    current_revision_id: str | None,
    ui_projection: dict[str, Any] | None,
) -> str:
    if role == READER_ROLE:
        return object_url(object_id)
    authoring_href = authoring_entry_href(
        role=role,
        object_id=object_id,
        ui_projection=ui_projection,
        current_revision_id=current_revision_id,
    )
    if authoring_href is not None:
        return authoring_href
    for action in projection_actions(ui_projection):
        if str(action.get("availability") or "") != "allowed":
            continue
        href = action_href(
            role=role,
            action_id=str(action.get("action_id") or ""),
            object_id=object_id,
            revision_id=revision_id,
        )
        if href is not None:
            return href
    return object_url(object_id)


def compact_action_menu_html(
    components: ComponentPresenter,
    *,
    role: str,
    ui_projection: dict[str, Any] | None,
    object_id: str,
    revision_id: str | None,
    current_revision_id: str | None,
) -> str:
    links: list[str] = []
    authoring_action_html = authoring_entry_html(
        role=role,
        object_id=object_id,
        ui_projection=ui_projection,
        current_revision_id=current_revision_id,
    )
    if authoring_action_html:
        links.append(authoring_action_html)

    for action in projection_actions(ui_projection):
        action_id = str(action.get("action_id") or "")
        if str(action.get("availability") or "") != "allowed":
            continue
        href = action_href(
            role=role,
            action_id=action_id,
            object_id=object_id,
            revision_id=revision_id,
        )
        if href is None:
            continue
        links.append(
            link(
                str(action.get("label") or action.get("action_id") or "Open action"),
                href,
                css_class="button button-secondary",
                attrs={
                    "data-component": "action-link",
                    "data-action-id": action_id,
                },
            )
        )

    if not links:
        return '<span class="cell-meta">No governed actions available from this surface.</span>'
    return join_html(links, " ")


def _transition_summary(transition: dict[str, Any] | None) -> str:
    if not transition:
        return "No transition recorded."
    from_state = (
        str(transition.get("from_state") or transition.get("state") or "").strip() or "unknown"
    )
    to_state = str(transition.get("to_state") or transition.get("state") or "").strip() or "unknown"
    semantics = str(transition.get("semantics") or "").strip()
    if from_state == to_state or not semantics:
        return f"{from_state} -> {to_state}"
    return f"{from_state} -> {to_state} ({semantics})"


def _humanize_token(token: str) -> str:
    return token.replace("_", " ").strip()


def render_workflow_projection_panel(
    components: ComponentPresenter,
    *,
    title: str,
    projection: dict[str, Any] | None,
    footer_html: str = "",
) -> str:
    data = dict(projection or {})
    rows = workflow_rows(data)
    warnings = workflow_warnings(data)
    reasons = workflow_reasons(data)
    detail = str(data.get("detail") or "Papyrus did not return a workflow detail for this screen.")
    operator_message = str(data.get("operator_message") or detail)
    body_parts = [
        f'<p class="governed-summary"><strong>{escape(data.get("summary") or "Backend workflow guidance unavailable")}</strong></p>',
        f"<p>{escape(detail)}</p>",
    ]
    if operator_message != detail:
        body_parts.append(f"<p>{escape(operator_message)}</p>")
    if rows:
        body_parts.append(
            render_definition_rows(
                [(row["label"], escape(row["value"] or "unknown")) for row in rows]
            )
        )
    if warnings:
        body_parts.append(
            '<div class="governed-reasons">'
            '<p class="governed-list-label">Warnings</p>'
            + render_list([escape(item) for item in warnings], css_class="validation-findings")
            + "</div>"
        )
    if reasons:
        body_parts.append(
            '<div class="governed-reasons">'
            '<p class="governed-list-label">Why Papyrus says this now</p>'
            + render_list([escape(item) for item in reasons], css_class="panel-list")
            + "</div>"
        )
    return components.context_panel(
        title=title,
        eyebrow="Workflow",
        summary=str(data.get("summary") or "Backend workflow guidance unavailable"),
        body_html=join_html(body_parts),
        tone=str(data.get("tone") or "context"),
        footer_html=footer_html,
        variant="workflow",
        surface="workflow",
    )


def render_projection_status_panel(
    components: ComponentPresenter,
    *,
    title: str,
    ui_projection: dict[str, Any] | None,
    footer_html: str = "",
) -> str:
    state = projection_state(ui_projection)
    use_guidance = projection_use_guidance(ui_projection)
    reasons = projection_reasons(ui_projection)
    body_html = join_html(
        [
            f'<p class="governed-summary"><strong>{escape(use_guidance.get("summary") or "Backend guidance unavailable")}</strong></p>',
            f"<p>{escape(use_guidance.get('detail') or 'Papyrus did not return a governed use-guidance detail for this view.')}</p>",
            render_definition_rows(
                [
                    (
                        "Next action",
                        escape(
                            use_guidance.get("next_action")
                            or "Papyrus did not return a next action for this view."
                        ),
                    ),
                    ("Lifecycle", escape(state.get("object_lifecycle_state") or "unknown")),
                    ("Review state", escape(state.get("revision_review_state") or "unknown")),
                    ("Draft progress", escape(state.get("draft_progress_state") or "unknown")),
                    ("Source sync", escape(state.get("source_sync_state") or "unknown")),
                    ("Trust", escape(state.get("trust_state") or "unknown")),
                ]
            ),
            (
                '<div class="governed-reasons">'
                '<p class="governed-list-label">Why Papyrus says this now</p>'
                + (
                    render_list([escape(item) for item in reasons], css_class="panel-list")
                    or '<p class="empty-state-copy">No explicit reasons were attached to this projection.</p>'
                )
                + "</div>"
            ),
        ]
    )
    return components.context_panel(
        title=title,
        eyebrow="Governance",
        summary=str(use_guidance.get("summary") or "Backend guidance unavailable"),
        body_html=body_html,
        tone="approved" if bool(use_guidance.get("safe_to_use")) else "context",
        footer_html=footer_html,
        variant="posture",
        surface="posture",
    )


def render_projection_overview_panel(
    components: ComponentPresenter,
    *,
    role: str,
    title: str,
    ui_projection: dict[str, Any] | None,
    object_id: str,
    revision_id: str | None,
    current_revision_id: str | None = None,
    footer_html: str = "",
) -> str:
    state = projection_state(ui_projection)
    use_guidance = projection_use_guidance(ui_projection)
    reasons = projection_reasons(ui_projection)
    body_parts = [
        f'<p class="governed-summary"><strong>{escape(use_guidance.get("summary") or "Backend guidance unavailable")}</strong></p>',
        f"<p>{escape(use_guidance.get('detail') or 'Papyrus did not return a governed use-guidance detail for this view.')}</p>",
        render_definition_rows(
            [
                (
                    "Next action",
                    escape(
                        use_guidance.get("next_action")
                        or "Papyrus did not return a next action for this view."
                    ),
                ),
                ("Lifecycle", escape(state.get("object_lifecycle_state") or "unknown")),
                ("Review state", escape(state.get("revision_review_state") or "unknown")),
                ("Draft progress", escape(state.get("draft_progress_state") or "unknown")),
                ("Source sync", escape(state.get("source_sync_state") or "unknown")),
                ("Trust", escape(state.get("trust_state") or "unknown")),
            ]
        ),
    ]
    if reasons:
        body_parts.append(
            '<div class="governed-reasons">'
            '<p class="governed-list-label">Why Papyrus says this now</p>'
            + (
                render_list([escape(item) for item in reasons], css_class="panel-list")
                or '<p class="empty-state-copy">No explicit reasons were attached to this projection.</p>'
            )
            + "</div>"
        )
    action_html = compact_action_menu_html(
        components,
        role=role,
        ui_projection=ui_projection,
        object_id=object_id,
        revision_id=revision_id,
        current_revision_id=current_revision_id,
    )
    body_parts.append(
        f'<div class="governed-action-cta" data-component="action-cluster">{action_html}</div>'
    )
    return components.context_panel(
        title=title,
        eyebrow="Current posture",
        summary=str(use_guidance.get("summary") or "Backend guidance unavailable"),
        body_html=join_html(body_parts),
        tone="approved" if bool(use_guidance.get("safe_to_use")) else "context",
        footer_html=footer_html,
        variant="projection-overview",
        surface="posture",
    )


def render_contract_status_panel(
    components: ComponentPresenter,
    *,
    title: str,
    summary: str,
    operator_message: str,
    source_of_truth: str | None = None,
    transition: dict[str, Any] | None = None,
    invalidated_assumptions: list[str] | tuple[str, ...] | None = None,
    acknowledgements: list[str] | tuple[str, ...] | None = None,
    required_acknowledgements: list[str] | tuple[str, ...] | None = None,
    tone: str = "context",
    footer_html: str = "",
) -> str:
    invalidated = [str(item) for item in invalidated_assumptions or []]
    required = [str(item) for item in required_acknowledgements or []]
    provided = [str(item) for item in acknowledgements or []]
    body_parts = [
        f'<p class="governed-summary"><strong>{escape(summary)}</strong></p>',
        f"<p>{escape(operator_message or summary)}</p>",
        render_definition_rows(
            [
                ("Source of truth", escape(source_of_truth or "unknown")),
                ("Transition", escape(_transition_summary(transition))),
                (
                    "Required acknowledgements",
                    escape(", ".join(_humanize_token(item) for item in required) or "None"),
                ),
                (
                    "Recorded acknowledgements",
                    escape(", ".join(_humanize_token(item) for item in provided) or "None"),
                ),
            ]
        ),
    ]
    if invalidated:
        body_parts.append(
            '<div class="governed-reasons">'
            '<p class="governed-list-label">Invalidated assumptions</p>'
            + (
                render_list([escape(item) for item in invalidated], css_class="panel-list")
                or '<p class="empty-state-copy">No invalidated assumptions were recorded.</p>'
            )
            + "</div>"
        )
    return components.context_panel(
        title=title,
        eyebrow="Contract",
        summary=summary,
        body_html=join_html(body_parts),
        tone=tone,
        footer_html=footer_html,
        variant="contract",
        surface="contract",
    )


def render_action_contract_panel(
    components: ComponentPresenter,
    *,
    title: str,
    action: dict[str, Any] | None,
    tone: str = "context",
    footer_html: str = "",
) -> str:
    if action is None:
        return render_contract_status_panel(
            components,
            title=title,
            summary="Backend action contract unavailable",
            operator_message="Papyrus did not return an action contract for this screen.",
            tone="warning",
            footer_html=footer_html,
        )
    policy = dict(action.get("policy") or {})
    return render_contract_status_panel(
        components,
        title=title,
        summary=str(action.get("summary") or action.get("label") or "Governed action"),
        operator_message=str(
            action.get("detail")
            or policy.get("operator_message")
            or "No operator message returned."
        ),
        source_of_truth=str(policy.get("source_of_truth") or "gate"),
        transition=dict(policy.get("transition") or {}),
        required_acknowledgements=[
            str(item) for item in policy.get("required_acknowledgements", [])
        ],
        tone=tone if action.get("availability") != "illegal" else "warning",
        footer_html=footer_html,
    )


def render_action_descriptor_panel(
    components: ComponentPresenter,
    *,
    title: str,
    actions: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    href_resolver=None,
    show_ctas: bool = True,
) -> str:
    items_html = []
    for action in actions:
        action_id = str(action.get("action_id") or "")
        availability = str(action.get("availability") or "illegal")
        tone = ACTION_AVAILABILITY_TONES.get(availability, "warning")
        policy = dict(action.get("policy") or {})
        required_acknowledgements = [
            str(item) for item in policy.get("required_acknowledgements", [])
        ]
        href = href_resolver(action) if href_resolver is not None else None
        cta_html = ""
        if show_ctas and availability == "allowed" and href is not None:
            cta_html = link(
                str(action.get("label") or action.get("action_id") or "Open action"),
                href,
                css_class="button button-secondary",
                attrs={
                    "data-component": "action-link",
                    "data-action-id": action_id,
                },
            )
        items_html.append(
            f'<article class="governed-action-item" data-component="action-descriptor" data-action-id="{escape(action_id or "unknown")}" data-variant="{escape(tone)}">'
            + f'<div class="governed-action-heading"><h3>{escape(action.get("label") or action.get("action_id") or "Action")}</h3>'
            + components.badge(
                label="Availability",
                value=ACTION_AVAILABILITY_LABELS.get(availability, availability),
                tone=tone,
            )
            + "</div>"
            + f'<p class="governed-action-summary">{escape(action.get("summary") or action.get("label") or "")}</p>'
            + f"<p>{escape(action.get('detail') or 'No operator detail was supplied for this action.')}</p>"
            + (
                render_definition_rows(
                    [
                        ("Source of truth", escape(policy.get("source_of_truth") or "gate")),
                        ("Transition", escape(_transition_summary(policy.get("transition")))),
                        (
                            "Acknowledgements",
                            escape(
                                ", ".join(
                                    _humanize_token(item) for item in required_acknowledgements
                                )
                                or "None"
                            ),
                        ),
                    ]
                )
                if policy
                else ""
            )
            + (f'<div class="governed-action-cta">{cta_html}</div>' if cta_html else "")
            + "</article>"
        )
    return components.context_panel(
        title=title,
        eyebrow="Actions",
        body_html=join_html(items_html)
        or '<p class="empty-state-copy">No actions were returned for this screen.</p>',
        tone="context",
        variant="actions",
        surface="actions",
        body_class="section-card-body governed-action-list",
    )


def render_acknowledgement_panel(
    components: ComponentPresenter,
    forms: FormPresenter,
    *,
    title: str,
    required_acknowledgements: list[str] | tuple[str, ...],
    selected_acknowledgements: list[str] | tuple[str, ...],
    operator_message: str,
    errors: list[str] | None = None,
    read_only: bool = False,
) -> str:
    required = [str(item) for item in required_acknowledgements]
    selected = {str(item) for item in selected_acknowledgements}
    items: list[str] = []
    for token in required:
        label = _humanize_token(token)
        if read_only:
            state_label = "Recorded" if token in selected else "Required"
            items.append(f"{escape(label)} ({escape(state_label)})")
            continue
        items.append(
            forms.checkbox(
                field_id=f"acknowledgement_{token}",
                name="acknowledgements",
                value=token,
                label=label,
                checked=token in selected,
            )
        )
    body_html = join_html(
        [
            f'<p class="governed-summary"><strong>{escape(operator_message or "Review the required acknowledgements before continuing.")}</strong></p>',
            (
                ('<div class="governed-acknowledgement-list">' + join_html(items) + "</div>")
                if items
                else '<p class="empty-state-copy">No acknowledgements are required.</p>'
                if not read_only
                else (
                    render_list([escape(item) for item in items], css_class="panel-list")
                    or '<p class="empty-state-copy">No acknowledgements are required.</p>'
                )
            ),
            (
                render_list(
                    [escape(item) for item in errors or []], css_class="validation-findings"
                )
                if errors
                else ""
            ),
        ]
    )
    return components.context_panel(
        title=title,
        eyebrow="Acknowledgements",
        summary=operator_message or "Review the required acknowledgements before continuing.",
        body_html=body_html,
        tone="warning" if required else "context",
        variant="acknowledgements",
        surface="acknowledgements",
    )
