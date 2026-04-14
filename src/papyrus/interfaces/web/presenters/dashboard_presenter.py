from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.governed_presenter import (
    primary_surface_href,
    projection_state,
    projection_use_guidance,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
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


def render_oversight_column(
    title: str, summary: str, items: list[dict[str, Any]], *, role: str, tone: str
) -> str:
    count_label = f"{len(items)} item" if len(items) == 1 else f"{len(items)} items"
    body = (
        join_html(
            [
                (
                    '<article class="oversight-board__card" data-component="oversight-card" data-surface="oversight">'
                    f'<p class="oversight-board__card-kicker">{escape(str(item.get("object_type") or "").replace("_", " "))} · {escape(item["object_id"])}</p>'
                    f"<h3>{link(item['title'], item_href(item, role=role))}</h3>"
                    f"<p>{escape(str(projection_use_guidance(item.get('ui_projection')).get('summary') or item.get('summary') or 'No summary recorded.'))}</p>"
                    f'<p class="oversight-board__card-next">{escape(str(projection_use_guidance(item.get("ui_projection")).get("next_action") or "Inspect article"))}</p>'
                    f"{link('Open', item_href(item, role=role), css_class='button button-ghost', attrs={'data-action-id': 'open-primary-surface'})}"
                    "</article>"
                )
                for item in items[:6]
            ]
        )
        if items
        else '<p class="oversight-board__empty">No items in this intervention group.</p>'
    )
    return (
        f'<section class="oversight-board__column tone-{escape(tone)}" data-component="oversight-column" data-surface="oversight">'
        '<div class="oversight-board__head">'
        + f'<p class="oversight-board__count">{escape(count_label)}</p>'
        + f"<h2>{escape(title)}</h2>"
        + f'<p class="oversight-board__summary">{escape(summary)}</p>'
        + "</div>"
        f"{body}</section>"
    )


def render_oversight_board(*, role: str, queue: list[dict[str, Any]]) -> str:
    groups = intervention_groups(queue)
    return (
        '<section class="oversight-board" data-component="oversight-board" data-surface="oversight">'
        '<div class="oversight-board__grid">'
        + render_oversight_column(
            "Trust debt",
            "Weak, stale, or suspect guidance that changes whether operators should trust the surface.",
            groups["trust_debt"],
            role=role,
            tone="danger",
        )
        + render_oversight_column(
            "Review backlog",
            "Content waiting on explicit review decisions.",
            groups["review_backlog"],
            role=role,
            tone="warning",
        )
        + render_oversight_column(
            "Ownership gaps",
            "Articles that need clearer ownership before they age into drift.",
            groups["ownership_gaps"],
            role=role,
            tone="brand",
        )
        + render_oversight_column(
            "Stable watch",
            "Items worth monitoring without immediate intervention.",
            groups["stable_watch"],
            role=role,
            tone="default",
        )
        + "</div></section>"
    )


def render_oversight_cleanup_board(*, cleanup_counts: dict[str, object]) -> str:
    return (
        '<section class="oversight-cleanup-board" data-component="oversight-cleanup-board" data-surface="oversight">'
        "<h2>Cleanup and trust debt</h2>"
        '<div class="oversight-cleanup-board__grid">'
        f'<article><p class="oversight-cleanup-board__metric">{escape(cleanup_counts.get("placeholder-heavy", 0))}</p><p>Placeholder-heavy</p></article>'
        f'<article><p class="oversight-cleanup-board__metric">{escape(cleanup_counts.get("legacy-blueprint-fallback", 0))}</p><p>Legacy fallback</p></article>'
        f'<article><p class="oversight-cleanup-board__metric">{escape(cleanup_counts.get("unclear-ownership", 0))}</p><p>Ownership gaps</p></article>'
        f'<article><p class="oversight-cleanup-board__metric">{escape(cleanup_counts.get("weak-evidence", 0))}</p><p>Weak evidence</p></article>'
        f'<article><p class="oversight-cleanup-board__metric">{escape(cleanup_counts.get("migration-gaps", 0))}</p><p>Migration gaps</p></article>'
        "</div></section>"
    )


def render_oversight_validation_board(*, validation_posture: dict[str, str]) -> str:
    return (
        '<section class="oversight-validation-board" data-component="oversight-validation-board" data-surface="oversight">'
        "<h2>Validation posture</h2>"
        f"<p>{escape(validation_posture['summary'])}</p>"
        f"<p>{escape(validation_posture['detail'])}</p>"
        "</section>"
    )


def present_oversight_dashboard(
    renderer: TemplateRenderer,
    *,
    role: str,
    dashboard: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer, selected_object_id, selected_revision_id
    return {
        "page_template": "pages/dashboard_oversight.html",
        "page_title": "Oversight",
        "page_header": {
            "headline": "Oversight",
            "intro": "See which content needs intervention, which items are simply worth watching, and where cleanup debt is accumulating.",
        },
        "active_nav": "oversight",
        "aside_html": "",
        "page_context": {
            "board_html": render_oversight_board(role=role, queue=dashboard["queue"]),
            "cleanup_html": render_oversight_cleanup_board(
                cleanup_counts=dashboard.get("cleanup_counts") or {}
            ),
            "validation_html": render_oversight_validation_board(
                validation_posture=dashboard["validation_posture"]
            ),
        },
        "page_surface": "oversight",
    }
