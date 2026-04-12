from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.view_helpers import escape


_HOME_HERO_COPY = {
    "local.operator": {
        "headline": "Start from the article, not the audit trail.",
        "intro": "Home is a launch surface for today’s work: open the safest guidance, continue drafts, and watch the few items that could block operators.",
    },
    "local.reviewer": {
        "headline": "Work the queue with decision context visible.",
        "intro": "Reviewer home is a workbench: pending decisions, blocked reviews, and trust exceptions are surfaced directly instead of being routed through generic launch cards.",
    },
    "local.manager": {
        "headline": "Portfolio pressure before item detail.",
        "intro": "Manager home is a pressure board: risk, review, service, and cleanup views are surfaced as portfolio signals rather than operator tasks.",
    },
}


def render_home_hero(*, dashboard: dict[str, Any]) -> str:
    hero_copy = _HOME_HERO_COPY.get(str(dashboard.get("actor_id") or ""), _HOME_HERO_COPY["local.operator"])
    layout_mode = str(dashboard.get("layout_mode") or "launchpad").replace("-", " ")
    return (
        '<section class="home-hero" data-component="home-hero" data-surface="home">'
        f'<p class="home-hero__kicker">{escape(layout_mode)}</p>'
        f'<h1>{escape(hero_copy["headline"])}</h1>'
        f'<p class="home-hero__intro">{escape(hero_copy["intro"])}</p>'
        "</section>"
    )
