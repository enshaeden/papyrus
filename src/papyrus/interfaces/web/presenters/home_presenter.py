from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link


_BLOCK_ACTION_LABELS = {
    "do_now": "Open",
    "continue": "Continue",
    "watch": "Inspect",
    "queue_status": "Open board",
    "pending_decisions": "Review",
    "blocked_reviews": "Inspect",
    "governance_consequences": "Open activity",
    "risk_pressure": "Open board",
    "review_pressure": "Open board",
    "service_pressure": "Open service",
    "cleanup_pressure": "Inspect",
    "portfolio_trends": "Open board",
}


def _launch_item_html(item: dict[str, str], *, action_label: str) -> str:
    return (
        '<li class="launch-item">'
        '<div class="launch-item-copy">'
        f'<p class="launch-item-title">{escape(item["title"])}</p>'
        f'<p class="launch-item-detail">{escape(item["detail"])}</p>'
        "</div>"
        '<div class="launch-item-meta">'
        + (f'<p class="launch-item-metric">{escape(item["metric"])}</p>' if str(item.get("metric") or "").strip() else "")
        + link(
            str(item.get("action_label") or action_label),
            item["href"],
            css_class=f'button button-ghost launch-item-link tone-{escape(item.get("tone") or "default")}',
        )
        + "</div></li>"
    )


def _launch_block_html(block: dict[str, Any]) -> str:
    action_label = str(_BLOCK_ACTION_LABELS.get(str(block.get("block_id") or ""), "Open"))
    return (
        f'<section class="launch-block tone-{escape(block.get("tone") or "default")}" data-component="launch-block" data-surface="home">'
        '<div class="launch-block-head">'
        f'<p class="launch-block-kicker">{escape(block["block_id"].replace("_", " "))}</p>'
        f'<h2>{escape(block["title"])}</h2>'
        f'<p>{escape(block["summary"])}</p>'
        "</div>"
        '<ul class="launch-list">'
        + join_html([_launch_item_html(item, action_label=action_label) for item in block["items"]])
        + "</ul></section>"
    )


def _activity_html(activity: list[dict[str, str]]) -> str:
    if not activity:
        return ""
    return (
        '<section class="home-activity" data-component="activity-list" data-surface="home">'
        '<div class="home-activity-head">'
        "<h2>Recent activity</h2>"
        "<p>Only activity that could change today’s next step stays on this screen.</p>"
        "</div>"
        '<ul class="activity-list">'
        + join_html(
            [
                (
                    '<li class="activity-list-item">'
                    f'<p class="activity-list-title">{escape(item["title"])}</p>'
                    f'<p class="activity-list-detail">{escape(item["detail"])}</p>'
                    f'{link("Open", item["href"], css_class="button button-ghost")}'
                    "</li>"
                )
                for item in activity
            ]
        )
        + "</ul></section>"
    )


def present_home_page(renderer: TemplateRenderer, *, dashboard: dict[str, Any]) -> dict[str, Any]:
    del renderer
    return {
        "page_template": "pages/home.html",
        "page_title": "Home",
        "page_surface": "home",
        "page_header": {},
        "active_nav": "home",
        "aside_html": "",
        "page_context": {
            "hero_html": (
                '<section class="home-hero" data-component="launch-hero" data-surface="home">'
                f'<p class="home-hero-kicker">{escape(dashboard["layout_mode"].replace("-", " "))}</p>'
                f'<h1>{escape(dashboard["headline"])}</h1>'
                f'<p class="home-hero-intro">{escape(dashboard["intro"])}</p>'
                "</section>"
            ),
            "primary_blocks_html": join_html([_launch_block_html(block) for block in dashboard["primary_blocks"]]),
            "secondary_blocks_html": join_html([_launch_block_html(block) for block in dashboard["secondary_blocks"]]),
            "activity_html": _activity_html(dashboard["activity"]),
        },
    }
