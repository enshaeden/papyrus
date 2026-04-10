from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import approval_status, escape, format_timestamp, freshness_status, join_html, link, risk_status


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
        "approval_state": str(state.get("approval_state") or item.get("approval_state") or "unknown"),
    }


def _dashboard_bucket(item: dict[str, Any]) -> str:
    state = _dashboard_state(item)
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    trust_state = state["trust_state"]
    approval_state = state["approval_state"]
    safe_to_use = bool(use_guidance.get("safe_to_use"))
    if trust_state == "suspect" or approval_state == "rejected":
        return "attention"
    if not safe_to_use or approval_state != "approved" or trust_state in {"weak_evidence", "stale"}:
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
    approval_label, approval_tone = approval_status(state["approval_state"])
    return join_html(
        [
            components.badge(label="Risk", value=risk_label, tone=risk_tone),
            components.badge(label="Freshness", value=freshness_label, tone=freshness_tone),
            components.badge(label="Approval", value=approval_label, tone=approval_tone),
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
    return (
        f'<article class="decision-card decision-card-{escape(bucket)}">'
        '<div class="decision-card-header">'
        '<div class="decision-card-heading">'
        f'<h3>{link(item["title"], _dashboard_item_href(item))}</h3>'
        f'<p class="decision-card-summary">{escape(_dashboard_why_now(item))}</p>'
        "</div>"
        f'<div class="badge-row">{_dashboard_status_badges_html(components, item)}</div>'
        "</div>"
        f'<p class="decision-card-detail">{escape(_dashboard_next_action(item))}</p>'
        f'<div class="decision-card-meta"><span>{escape(item["object_id"])}</span></div>'
        f'<div class="decision-card-actions">{link(_dashboard_decision_action_label(bucket), _dashboard_item_href(item), css_class="button button-primary" if bucket != "safe" else "button button-secondary")}</div>'
        "</article>"
    )


def _validation_run_bucket(status: str) -> str:
    normalized = str(status or "").lower()
    if normalized == "passed":
        return "safe"
    if normalized in {"warning", "degraded"}:
        return "review"
    return "attention"
def present_trust_dashboard(renderer: TemplateRenderer, *, dashboard: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    summary_cards_html = join_html(
        [
            components.section_card(
                title="Knowledge in scope",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['object_count'])}</p><p>Operational knowledge objects currently in the runtime.</p>",
                footer_html=link("Find guidance", "/read", css_class="button button-secondary"),
            ),
            components.section_card(
                title="Review pressure",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['approval_counts'].get('in_review', 0))}</p><p>Revisions currently waiting on a review decision.</p>",
                footer_html=link("Review decisions", "/review", css_class="button button-primary"),
                tone="warning" if dashboard["approval_counts"].get("in_review", 0) else "approved",
            ),
            components.section_card(
                title="Needs revalidation",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['trust_counts'].get('stale', 0) + dashboard['trust_counts'].get('weak_evidence', 0) + dashboard['trust_counts'].get('suspect', 0))}</p><p>Guidance that needs evidence, freshness, or trust follow-up.</p>",
                footer_html=link("Resolve risk", "/health", css_class="button button-secondary"),
                tone="warning" if (dashboard["trust_counts"].get("stale", 0) + dashboard["trust_counts"].get("weak_evidence", 0) + dashboard["trust_counts"].get("suspect", 0)) else "approved",
            ),
            components.section_card(
                title="Evidence posture",
                eyebrow="Health",
                body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["evidence_counts"].items()))) + "</p>",
                footer_html=link("See history", "/activity", css_class="button button-secondary"),
            ),
        ]
    )
    grouped_items: dict[str, list[dict[str, Any]]] = {"safe": [], "review": [], "attention": []}
    for item in dashboard["queue"]:
        grouped_items[_dashboard_bucket(item)].append(item)
    group_config = {
        "attention": ("Requires attention", "Resolve the highest-risk items first.", "danger"),
        "review": ("Needs review", "Check these items before relying on them.", "warning"),
        "safe": ("Safe", "These items are the strongest current answers.", "approved"),
    }
    grouped_sections = []
    for group_key in ("attention", "review", "safe"):
        group_items = grouped_items[group_key]
        if not group_items:
            continue
        title, description, tone = group_config[group_key]
        grouped_sections.append(
            components.section_card(
                title=title,
                eyebrow="Health",
                tone=tone,
                body_html=f'<p class="decision-group-summary">{escape(description)}</p>' + join_html(
                    [_dashboard_decision_card_html(components, item) for item in group_items]
                ),
            )
        )
    primary_html = components.section_card(
        title="Needs attention",
        eyebrow="Health",
        body_html=join_html(grouped_sections),
    )
    secondary_html = components.section_card(
        title="Recent validation runs",
        eyebrow="Activity",
        body_html=(
            f'<p class="decision-group-summary">{escape(dashboard["validation_posture"]["summary"])}: {escape(dashboard["validation_posture"]["detail"])}</p>'
            + join_html(
                [
                    (
                        f'<article class="decision-card decision-card-{escape(_validation_run_bucket(run["status"]))}">'
                        '<div class="decision-card-header">'
                        '<div class="decision-card-heading">'
                        f'<h3>{escape(run["run_type"])}</h3>'
                        f'<p class="decision-card-summary">Completed {escape(format_timestamp(run["completed_at"]))}</p>'
                        "</div>"
                        "</div>"
                        f'<div class="decision-card-meta"><span>Status {escape(run["status"])}</span><span>Findings recorded: {escape(run["finding_count"])}</span></div>'
                        '<p class="decision-card-next"><strong>Next:</strong> Inspect the recorded run if it affects approval or revalidation work.</p>'
                        "</article>"
                    )
                    for run in dashboard["validation_runs"]
                ]
            )
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
