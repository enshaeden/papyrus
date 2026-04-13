from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.governed_presenter import (
    primary_surface_href,
    projection_state,
    projection_use_guidance,
)
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def item_href(item: dict[str, Any], *, role: str) -> str:
    return primary_surface_href(
        role=role,
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip()
        or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def intervention_groups(queue: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups = {
        "trust_debt": [],
        "review_backlog": [],
        "ownership_gaps": [],
        "stable_watch": [],
    }
    for item in queue:
        state = projection_state(item.get("ui_projection"))
        trust_state = str(state.get("trust_state") or item.get("trust_state") or "unknown")
        review_state = str(
            state.get("revision_review_state") or item.get("revision_review_state") or "unknown"
        )
        if trust_state in {"suspect", "stale", "weak_evidence"}:
            groups["trust_debt"].append(item)
        elif review_state in {"in_review", "rejected", "draft"}:
            groups["review_backlog"].append(item)
        elif not str(item.get("owner") or "").strip() or int(item.get("ownership_rank") or 0) > 0:
            groups["ownership_gaps"].append(item)
        else:
            groups["stable_watch"].append(item)
    return groups


def render_health_column(
    title: str, summary: str, items: list[dict[str, Any]], *, role: str, tone: str
) -> str:
    body = (
        join_html(
            [
                (
                    '<article class="health-board__card" data-component="health-card" data-surface="knowledge-health">'
                    f'<p class="health-board__card-kicker">{escape(str(item.get("object_type") or "").replace("_", " "))} · {escape(item["object_id"])}</p>'
                    f"<h3>{link(item['title'], item_href(item, role=role))}</h3>"
                    f"<p>{escape(str(projection_use_guidance(item.get('ui_projection')).get('summary') or item.get('summary') or 'No summary recorded.'))}</p>"
                    f'<p class="health-board__card-next">{escape(str(projection_use_guidance(item.get("ui_projection")).get("next_action") or "Inspect article"))}</p>'
                    f"{link('Open', item_href(item, role=role), css_class='button button-ghost', attrs={'data-action-id': 'open-primary-surface'})}"
                    "</article>"
                )
                for item in items[:6]
            ]
        )
        if items
        else '<p class="health-board__empty">No items in this intervention group.</p>'
    )
    return (
        f'<section class="health-board__column tone-{escape(tone)}" data-component="health-column" data-surface="knowledge-health">'
        f"<h2>{escape(title)}</h2>"
        f'<p class="health-board__summary">{escape(summary)}</p>'
        f"{body}</section>"
    )


def render_health_board(*, role: str, queue: list[dict[str, Any]]) -> str:
    groups = intervention_groups(queue)
    return (
        '<section class="health-board" data-component="health-board" data-surface="knowledge-health">'
        '<div class="health-board__grid">'
        + render_health_column(
            "Trust debt",
            "Weak, stale, or suspect guidance that changes whether operators should trust the surface.",
            groups["trust_debt"],
            role=role,
            tone="danger",
        )
        + render_health_column(
            "Review backlog",
            "Guidance waiting on explicit governance decisions.",
            groups["review_backlog"],
            role=role,
            tone="warning",
        )
        + render_health_column(
            "Ownership gaps",
            "Articles that need clearer stewardship before they age into drift.",
            groups["ownership_gaps"],
            role=role,
            tone="brand",
        )
        + render_health_column(
            "Stable watch",
            "Items worth monitoring without immediate intervention.",
            groups["stable_watch"],
            role=role,
            tone="default",
        )
        + "</div></section>"
    )
