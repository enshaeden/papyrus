from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, tone_for_approval, tone_for_trust


def _dashboard_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _dashboard_safe_now_html(components: ComponentPresenter, item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    state = projection_state(item.get("ui_projection"))
    return join_html(
        [
            components.badge(
                label="Use",
                value="Safe now" if bool(use_guidance.get("safe_to_use")) else "Review first",
                tone="approved" if bool(use_guidance.get("safe_to_use")) else "warning",
            ),
            components.badge(
                label="Approval",
                value=str(state.get("approval_state") or "unknown"),
                tone="approved" if str(state.get("approval_state") or "") == "approved" else "pending",
            ),
            components.badge(
                label="Trust",
                value=str(state.get("trust_state") or "unknown"),
                tone="approved" if str(state.get("trust_state") or "") == "trusted" else "warning",
            ),
        ],
        " ",
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


def _dashboard_action_label(item: dict[str, Any]) -> str:
    state = projection_state(item.get("ui_projection"))
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    if bool(use_guidance.get("safe_to_use")):
        return "Use guidance"
    if str(state.get("approval_state") or "") == "in_review":
        return "Review decision"
    if str(state.get("trust_state") or "") in {"suspect", "stale", "weak_evidence"}:
        return "Review risk"
    return "Inspect guidance"


def _dashboard_status_cell(components: ComponentPresenter, item: dict[str, Any]) -> str:
    state = projection_state(item.get("ui_projection"))
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return components.decision_cell(
        title_html=escape(use_guidance.get("summary") or "Status unavailable"),
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
        ],
        supporting_html=escape(_dashboard_why_now(item)),
    )


def present_trust_dashboard(renderer: TemplateRenderer, *, dashboard: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    summary_cards_html = join_html(
        [
            components.section_card(
                title="Knowledge in scope",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['object_count'])}</p><p>Operational knowledge objects currently in the runtime.</p>",
                footer_html=link("Read guidance", "/read", css_class="button button-secondary"),
            ),
            components.section_card(
                title="Review pressure",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['approval_counts'].get('in_review', 0))}</p><p>Revisions currently waiting on a review decision.</p>",
                footer_html=link("Review queue", "/review", css_class="button button-primary"),
                tone="warning" if dashboard["approval_counts"].get("in_review", 0) else "approved",
            ),
            components.section_card(
                title="Needs revalidation",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['trust_counts'].get('stale', 0) + dashboard['trust_counts'].get('weak_evidence', 0) + dashboard['trust_counts'].get('suspect', 0))}</p><p>Guidance that needs evidence, freshness, or trust follow-up.</p>",
                footer_html=link("Review risks", "/health", css_class="button button-secondary"),
                tone="warning" if (dashboard["trust_counts"].get("stale", 0) + dashboard["trust_counts"].get("weak_evidence", 0) + dashboard["trust_counts"].get("suspect", 0)) else "approved",
            ),
            components.section_card(
                title="Evidence posture",
                eyebrow="Health",
                body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["evidence_counts"].items()))) + "</p>",
                footer_html=link("Inspect activity", "/activity", css_class="button button-secondary"),
            ),
        ]
    )
    primary_html = components.section_card(
        title="Needs attention",
        eyebrow="Health",
        body_html=components.queue_table(
            headers=["Guidance", "Status", "What needs attention", "Do next"],
            rows=[
                [
                    components.decision_cell(
                        title_html=link(item["title"], _dashboard_item_href(item)),
                        meta=[escape(str(item.get("object_id") or ""))],
                    ),
                    _dashboard_status_cell(components, item),
                    components.decision_cell(
                        title_html=escape(_dashboard_next_action(item)),
                        supporting_html=escape(_dashboard_why_now(item)),
                    ),
                    link(_dashboard_action_label(item), _dashboard_item_href(item), css_class="button button-primary"),
                ]
                for item in dashboard["queue"]
            ],
            table_id="knowledge-health-queue",
        ),
    )
    secondary_html = components.section_card(
        title="Recent validation runs",
        eyebrow="Activity",
        body_html=components.queue_table(
            headers=["Completed", "Run type", "Status", "Findings", "Next action"],
            rows=[
                [
                    escape(format_timestamp(run["completed_at"])),
                    escape(run["run_type"]),
                    escape(run["status"]),
                    escape(run["finding_count"]),
                    escape("Inspect the recorded run if this affects approval or revalidation work."),
                ]
                for run in dashboard["validation_runs"]
            ],
            table_id="dashboard-validation-runs",
        ),
    )
    return {
        "page_template": "pages/dashboard_trust.html",
        "page_title": "Knowledge Health",
        "headline": "Knowledge Health",
        "kicker": "Health",
        "intro": "See what needs review or revalidation next.",
        "active_nav": "health",
        "aside_html": "",
        "page_context": {
            "summary_cards_html": summary_cards_html,
            "primary_html": primary_html,
            "secondary_html": secondary_html,
        },
    }
