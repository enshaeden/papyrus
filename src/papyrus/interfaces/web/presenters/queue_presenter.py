from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import approval_status, escape, freshness_status, join_html, link, quoted_path, risk_status


def _queue_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _use_when_text(item: dict[str, Any]) -> str:
    summary = str(item.get("summary") or "").strip()
    if summary:
        return summary
    object_type = str(item.get("object_type") or "")
    if object_type == "runbook":
        return "Use when you need a step-by-step operational procedure."
    if object_type == "known_error":
        return "Use when you need symptom-driven troubleshooting guidance."
    if object_type == "service_record":
        return "Use when you need service context, dependencies, or support ownership."
    if object_type == "policy":
        return "Use when you need governed controls, scope, and exception handling."
    if object_type == "system_design":
        return "Use when you need architecture, interfaces, and operational design context."
    return "Use when this item is the best available operational fit."


def _next_action_text(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("next_action")
        or use_guidance.get("detail")
        or "Papyrus did not return a next action for this result."
    )


def _status_detail_text(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("detail")
        or use_guidance.get("summary")
        or "Papyrus did not return governed detail for this result."
    )


def _queue_state(item: dict[str, Any]) -> dict[str, str]:
    state = projection_state(item.get("ui_projection"))
    return {
        "trust_state": str(state.get("trust_state") or item.get("trust_state") or "unknown"),
        "approval_state": str(state.get("approval_state") or item.get("approval_state") or "unknown"),
    }


def _decision_summary_text(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(use_guidance.get("summary") or _use_when_text(item))


def _decision_bucket(item: dict[str, Any]) -> str:
    state = _queue_state(item)
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    trust_state = state["trust_state"]
    approval_state = state["approval_state"]
    safe_to_use = bool(use_guidance.get("safe_to_use"))
    if trust_state == "suspect" or approval_state == "rejected":
        return "attention"
    if not safe_to_use or approval_state != "approved" or trust_state in {"weak_evidence", "stale"}:
        return "review"
    return "safe"


def _decision_status_badges_html(components: ComponentPresenter, item: dict[str, Any]) -> str:
    state = _queue_state(item)
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


def _decision_action_label(bucket: str) -> str:
    if bucket == "safe":
        return "Use guidance"
    if bucket == "review":
        return "Review item"
    return "Resolve issue"


def _decision_card_html(components: ComponentPresenter, item: dict[str, Any]) -> str:
    bucket = _decision_bucket(item)
    linked_services_html = (
        ", ".join(
            link(service["service_name"], f"/services/{quoted_path(service['service_id'])}")
            for service in item["linked_services"]
        )
        if item["linked_services"]
        else "No linked service context."
    )
    return (
        f'<article class="decision-card decision-card-{escape(bucket)}">'
        '<div class="decision-card-header">'
        '<div class="decision-card-heading">'
        f'<h3>{link(item["title"], _queue_item_href(item))}</h3>'
        f'<p class="decision-card-summary">{escape(_decision_summary_text(item))}</p>'
        "</div>"
        f'<div class="badge-row">{_decision_status_badges_html(components, item)}</div>'
        "</div>"
        f'<p class="decision-card-detail">{escape(_status_detail_text(item))}</p>'
        '<div class="decision-card-meta">'
        f'<span>{escape(item["object_type"])} · {escape(item["object_id"])}</span>'
        f'<span>Last reviewed {escape(item.get("last_reviewed") or "unknown")} · cadence {escape(item.get("review_cadence") or "unknown")}</span>'
        f"<span>Services: {linked_services_html}</span>"
        "</div>"
        f'<p class="decision-card-next"><strong>Next:</strong> {escape(_next_action_text(item))}</p>'
        f'<div class="decision-card-actions">{link(_decision_action_label(bucket), _queue_item_href(item), css_class="button button-secondary")}</div>'
        "</article>"
    )


def present_queue_page(
    renderer: TemplateRenderer,
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_approval: str,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    normalized_items = []
    for item in items:
        normalized = dict(item)
        normalized.setdefault("linked_services", [])
        normalized_items.append(normalized)
    grouped_items: dict[str, list[dict[str, Any]]] = {"safe": [], "review": [], "attention": []}
    for item in normalized_items:
        grouped_items[_decision_bucket(item)].append(item)
    summary_html = components.trust_summary(
        title="Decision view",
        badges=[
            components.badge(label="Safe", value=len(grouped_items["safe"]), tone="approved"),
            components.badge(label="Needs review", value=len(grouped_items["review"]), tone="warning"),
            components.badge(label="Requires attention", value=len(grouped_items["attention"]), tone="danger"),
        ],
        summary="Papyrus groups guidance by decision urgency so the next click is driven by risk, freshness, and approval state.",
    )
    filter_controls_html = (
        '<form class="filter-form" method="get" action="/read">'
        f'<input type="search" name="query" placeholder="Search guidance" value="{escape(query)}" data-filter-input="true" />'
        '<select name="object_type">'
        f'<option value=""{" selected" if not selected_type else ""}>All types</option>'
        f'<option value="runbook"{" selected" if selected_type == "runbook" else ""}>Runbooks</option>'
        f'<option value="known_error"{" selected" if selected_type == "known_error" else ""}>Known errors</option>'
        f'<option value="service_record"{" selected" if selected_type == "service_record" else ""}>Service records</option>'
        f'<option value="policy"{" selected" if selected_type == "policy" else ""}>Policies</option>'
        f'<option value="system_design"{" selected" if selected_type == "system_design" else ""}>System designs</option>'
        "</select>"
        '<select name="trust">'
        f'<option value=""{" selected" if not selected_trust else ""}>All trust</option>'
        f'<option value="trusted"{" selected" if selected_trust == "trusted" else ""}>Trusted</option>'
        f'<option value="weak_evidence"{" selected" if selected_trust == "weak_evidence" else ""}>Weak evidence</option>'
        f'<option value="stale"{" selected" if selected_trust == "stale" else ""}>Stale</option>'
        f'<option value="suspect"{" selected" if selected_trust == "suspect" else ""}>Suspect</option>'
        "</select>"
        '<select name="approval">'
        f'<option value=""{" selected" if not selected_approval else ""}>All approval</option>'
        f'<option value="approved"{" selected" if selected_approval == "approved" else ""}>Approved</option>'
        f'<option value="in_review"{" selected" if selected_approval == "in_review" else ""}>In review</option>'
        f'<option value="draft"{" selected" if selected_approval == "draft" else ""}>Draft</option>'
        f'<option value="rejected"{" selected" if selected_approval == "rejected" else ""}>Rejected</option>'
        "</select>"
        '<button class="button button-primary" type="submit">Show best matches</button>'
        "</form>"
    )
    group_config = {
        "safe": ("Safe", "Approved guidance you can use with the current guardrails.", "approved"),
        "review": ("Needs review", "Guidance that needs verification before you rely on it.", "warning"),
        "attention": ("Requires attention", "Guidance blocked by higher-risk trust or approval signals.", "danger"),
    }
    group_sections = []
    for group_key in ("attention", "review", "safe"):
        group_items = grouped_items[group_key]
        if not group_items:
            continue
        title, description, tone = group_config[group_key]
        group_sections.append(
            components.section_card(
                title=title,
                eyebrow="Read",
                tone=tone,
                body_html=f'<p class="decision-group-summary">{escape(description)}</p>' + join_html(
                    [_decision_card_html(components, item) for item in group_items]
                ),
            )
        )
    queue_html = (
        join_html(group_sections)
        if group_sections
        else components.empty_state(
            title="No matching guidance",
            description="Adjust filters or search terms to widen the read scope.",
        )
    )
    return {
        "page_template": "pages/queue.html",
        "page_title": "Read Guidance",
        "headline": "Read Operational Guidance",
        "kicker": "Read",
        "intro": "Find the right guidance and see the next step immediately.",
        "active_nav": "read",
        "aside_html": "",
        "page_context": {
            "filter_bar_html": components.filter_bar(title="Read filters", controls_html=filter_controls_html),
            "summary_html": summary_html,
            "queue_html": queue_html,
            "secondary_html": "",
        },
    }
