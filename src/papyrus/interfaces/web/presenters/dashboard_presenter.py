from __future__ import annotations

from typing import Any

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
            components.surface_panel(
                title="Knowledge in scope",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['object_count'])}</p><p>Operational knowledge objects currently in the runtime.</p>",
                footer_html=link("Find guidance", "/read", css_class="button button-secondary"),
                variant="knowledge-in-scope",
                surface="knowledge-health",
            ),
            components.surface_panel(
                title="Review pressure",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['review_counts'].get('in_review', 0))}</p><p>Revisions currently waiting on a review decision.</p>",
                footer_html=link("Review decisions", "/review", css_class="button button-primary"),
                tone="warning" if dashboard["review_counts"].get("in_review", 0) else "approved",
                variant="review-pressure",
                surface="knowledge-health",
            ),
            components.surface_panel(
                title="Needs revalidation",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['trust_counts'].get('stale', 0) + dashboard['trust_counts'].get('weak_evidence', 0) + dashboard['trust_counts'].get('suspect', 0))}</p><p>Guidance that needs evidence, freshness, or trust follow-up.</p>",
                footer_html=link("Resolve risk", "/health", css_class="button button-secondary"),
                tone="warning" if (dashboard["trust_counts"].get("stale", 0) + dashboard["trust_counts"].get("weak_evidence", 0) + dashboard["trust_counts"].get("suspect", 0)) else "approved",
                variant="needs-revalidation",
                surface="knowledge-health",
            ),
            components.surface_panel(
                title="Evidence posture",
                eyebrow="Health",
                body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["evidence_counts"].items()))) + "</p>",
                footer_html=link("See history", "/activity", css_class="button button-secondary"),
                variant="evidence-posture",
                surface="knowledge-health",
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
            components.surface_panel(
                title=title,
                eyebrow="Health",
                tone=tone,
                body_html=f'<p class="decision-group-summary">{escape(description)}</p>' + join_html(
                    [_dashboard_decision_card_html(components, item) for item in group_items]
                ),
                variant=group_key,
                surface="knowledge-health",
            )
        )
    cleanup_counts = dashboard.get("cleanup_counts") or {}
    primary_html = components.surface_panel(
        title="Needs attention",
        eyebrow="Health",
        body_html=join_html(grouped_sections),
        variant="triage",
        surface="knowledge-health",
    )
    validation_runs_html = join_html(
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
    secondary_html = join_html(
        [
            components.surface_panel(
                title="Recent validation runs",
                eyebrow="Activity",
                body_html=(
                    f'<p class="decision-group-summary">{escape(dashboard["validation_posture"]["summary"])}: {escape(dashboard["validation_posture"]["detail"])}</p>'
                    + validation_runs_html
                ),
                variant="validation-runs",
                surface="knowledge-health",
            ),
            components.surface_panel(
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
        "aside_html": "",
        "page_context": {
            "summary_cards_html": summary_cards_html,
            "primary_html": primary_html,
            "secondary_html": secondary_html,
        },
        "page_surface": "knowledge-health",
    }
