from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, freshness_status, join_html, link, render_definition_rows, review_state_status, risk_status


def _dashboard_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _dashboard_why_now(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("summary")
        or use_guidance.get("detail")
        or "Papyrus did not return governed summary for this queue item."
    )


def _dashboard_next_action(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("next_action")
        or use_guidance.get("detail")
        or "Papyrus did not return a next action for this queue item."
    )

def _dashboard_state(item: dict[str, Any]) -> dict[str, str]:
    state = projection_state(item.get("ui_projection"))
    return {
        "trust_state": str(state.get("trust_state") or item.get("trust_state") or "unknown"),
        "revision_review_state": str(state.get("revision_review_state") or item.get("revision_review_state") or "unknown"),
    }


def _dashboard_bucket(item: dict[str, Any]) -> str:
    state = _dashboard_state(item)
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    trust_state = state["trust_state"]
    revision_review_state = state["revision_review_state"]
    safe_to_use = bool(use_guidance.get("safe_to_use"))
    if trust_state == "suspect" or revision_review_state == "rejected":
        return "attention"
    if not safe_to_use or revision_review_state != "approved" or trust_state in {"weak_evidence", "stale"}:
        return "review"
    return "safe"


def _dashboard_status_badges_html(components: ComponentPresenter, item: dict[str, Any]) -> str:
    state = _dashboard_state(item)
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    risk_label, risk_tone = risk_status(
        trust_state=state["trust_state"],
        safe_to_use=bool(use_guidance.get("safe_to_use")),
    )
    freshness_label, freshness_tone = freshness_status(int(item.get("freshness_rank") or 0))
    review_label, review_tone = review_state_status(state["revision_review_state"])
    return join_html(
        [
            components.badge(label="Risk", value=risk_label, tone=risk_tone),
            components.badge(label="Freshness", value=freshness_label, tone=freshness_tone),
            components.badge(label="Review", value=review_label, tone=review_tone),
        ],
        " ",
    )


def _dashboard_decision_action_label(bucket: str) -> str:
    if bucket == "safe":
        return "Use guidance"
    if bucket == "review":
        return "Review item"
    return "Resolve issue"


def _dashboard_decision_card_html(components: ComponentPresenter, item: dict[str, Any]) -> str:
    bucket = _dashboard_bucket(item)
    return components.decision_card(
        title_html=link(item["title"], _dashboard_item_href(item)),
        summary=_dashboard_why_now(item),
        detail=_dashboard_next_action(item),
        meta=[escape(item["object_id"])],
        badges=[_dashboard_status_badges_html(components, item)],
        actions_html=link(
            _dashboard_decision_action_label(bucket),
            _dashboard_item_href(item),
            css_class="button button-secondary",
            attrs={"data-component": "action-link", "data-action-id": "open-primary-surface"},
        ),
        tone=bucket,
        surface="knowledge-health",
    )


def _dashboard_selection_href(object_id: str, revision_id: str = "") -> str:
    return "/health?" + urlencode(
        {
            key: value
            for key, value in {
                "selected_object_id": object_id,
                "selected_revision_id": revision_id,
            }.items()
            if value
        }
    )


def _selected_dashboard_item(
    items: list[dict[str, Any]],
    *,
    selected_object_id: str,
    selected_revision_id: str,
) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        if object_id == selected_object_id and (not selected_revision_id or revision_id == selected_revision_id):
            return item
    return items[0]


def _dashboard_table_html(
    components: ComponentPresenter,
    *,
    items: list[dict[str, Any]],
    selected_item: dict[str, Any] | None,
) -> str:
    rows: list[list[str]] = []
    row_attrs: list[dict[str, object]] = []
    for item in items:
        object_id = str(item["object_id"])
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        is_selected = (
            selected_item is not None
            and str(selected_item.get("object_id") or "") == object_id
            and str(selected_item.get("revision_id") or selected_item.get("current_revision_id") or "") == revision_id
        )
        rows.append(
            [
                components.decision_cell(
                    title_html=link(str(item["title"]), _dashboard_selection_href(object_id, revision_id), css_class="selected-row-link"),
                    supporting_html=escape(_dashboard_why_now(item)),
                    meta=[escape(object_id)],
                ),
                components.decision_cell(
                    title_html=escape(_dashboard_next_action(item)),
                    badges=[_dashboard_status_badges_html(components, item)],
                ),
                components.decision_cell(title_html=escape(_dashboard_bucket(item).title())),
                link(
                    "Open",
                    _dashboard_item_href(item),
                    css_class="button button-secondary",
                    attrs={"data-component": "action-link", "data-action-id": "open-primary-surface"},
                ),
            ]
        )
        row_attrs.append({"aria-selected": "true", "class": "is-selected"} if is_selected else {})
    return components.queue_table(
        headers=["Guidance", "Next action", "Risk bucket", "Open"],
        rows=rows,
        row_attrs=row_attrs,
        table_id="knowledge-health-queue",
        surface="knowledge-health",
        variant="dense-table",
    )


def _dashboard_context_panel(components: ComponentPresenter, item: dict[str, Any]) -> str:
    return components.context_panel(
        title=str(item["title"]),
        eyebrow="Selected item",
        body_html=join_html(
            [
                f"<p><strong>{escape(_dashboard_why_now(item))}</strong></p>",
                f"<p>{escape(_dashboard_next_action(item))}</p>",
                f'<div class="badge-row">{_dashboard_status_badges_html(components, item)}</div>',
            ]
        ),
        footer_html=link(
            "Open guidance",
            _dashboard_item_href(item),
            css_class="button button-secondary",
            attrs={"data-component": "action-link", "data-action-id": "open-primary-surface"},
        ),
        variant="selected-item",
        surface="knowledge-health",
    )


def _validation_run_bucket(status: str) -> str:
    normalized = str(status or "").lower()
    if normalized == "passed":
        return "safe"
    if normalized in {"warning", "degraded"}:
        return "review"
    return "attention"


def present_trust_dashboard(
    renderer: TemplateRenderer,
    *,
    dashboard: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    selected_item = _selected_dashboard_item(
        dashboard["queue"],
        selected_object_id=selected_object_id,
        selected_revision_id=selected_revision_id,
    )
    summary_cards_html = components.summary_strip(
        title="Knowledge pressure",
        badges=[
            components.badge(label="In scope", value=dashboard["object_count"], tone="brand"),
            components.badge(label="Review pressure", value=dashboard["review_counts"].get("in_review", 0), tone="pending"),
            components.badge(
                label="Needs revalidation",
                value=dashboard["trust_counts"].get("stale", 0) + dashboard["trust_counts"].get("weak_evidence", 0) + dashboard["trust_counts"].get("suspect", 0),
                tone="warning",
            ),
            components.badge(label="Evidence counts", value=len(dashboard["evidence_counts"]), tone="context"),
        ],
        summary="Use the selected row to inspect the next highest-value governance action.",
        surface="knowledge-health",
        variant="overview",
    )
    primary_html = (
        _dashboard_table_html(components, items=dashboard["queue"], selected_item=selected_item)
        if dashboard["queue"]
        else components.empty_state(
            title="No governance items",
            description="The health queue is currently empty.",
        )
    )
    cleanup_counts = dashboard.get("cleanup_counts") or {}
    aside_html = join_html(
        [
            _dashboard_context_panel(components, selected_item) if selected_item is not None else "",
            components.context_panel(
                title="Recent validation runs",
                eyebrow="Activity",
                body_html=(
                    f'<p>{escape(dashboard["validation_posture"]["summary"])}: {escape(dashboard["validation_posture"]["detail"])}</p>'
                    + join_html(
                        [
                            components.decision_card(
                                title_html=escape(run["run_type"]),
                                summary=f"Completed {format_timestamp(run['completed_at'])}",
                                meta=[
                                    escape(f"Status {run['status']}"),
                                    escape(f"Findings recorded: {run['finding_count']}"),
                                ],
                                next_action="Inspect the recorded run if it affects approval or revalidation work.",
                                tone=_validation_run_bucket(run["status"]),
                                surface="knowledge-health",
                            )
                            for run in dashboard["validation_runs"]
                        ]
                    )
                ),
                variant="validation-runs",
                surface="knowledge-health",
            ),
            components.context_panel(
                title="Operational usefulness cleanup",
                eyebrow="Cleanup",
                body_html=render_definition_rows(
                    [
                        ("Placeholder-heavy", escape(cleanup_counts.get("placeholder-heavy", 0))),
                        ("Legacy blueprint fallback", escape(cleanup_counts.get("legacy-blueprint-fallback", 0))),
                        ("Unclear ownership", escape(cleanup_counts.get("unclear-ownership", 0))),
                        ("Weak evidence", escape(cleanup_counts.get("weak-evidence", 0))),
                        ("Migration gaps", escape(cleanup_counts.get("migration-gaps", 0))),
                    ]
                ),
                summary="Use these counts to prioritize cleanup work that most affects operational usefulness.",
                tone="context",
                variant="cleanup",
                surface="knowledge-health",
            ),
        ]
    )
    return {
        "page_template": "pages/dashboard_trust.html",
        "page_title": "Knowledge Health",
        "page_header": {
            "headline": "Knowledge health",
            "show_actor_links": True,
        },
        "active_nav": "health",
        "aside_html": aside_html,
        "page_context": {
            "summary_cards_html": summary_cards_html,
            "primary_html": primary_html,
        },
        "page_surface": "knowledge-health",
    }
