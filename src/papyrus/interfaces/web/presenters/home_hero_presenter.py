from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE, OPERATOR_ROLE, READER_ROLE
from papyrus.interfaces.web.view_helpers import escape


_HOME_HERO_COPY = {
    READER_ROLE: {
        "headline": "Start from current guidance.",
        "intro": "Reader browse stays content-first so you can find the right document without stepping into draft, review, or control-plane workflows.",
    },
    OPERATOR_ROLE: {
        "headline": "Start from the article, not the audit trail.",
        "intro": "Home is a launch surface for today’s work: open the safest guidance, continue drafts, and watch the few items that could block operators.",
    },
    ADMIN_ROLE: {
        "headline": "Control-plane pressure before item detail.",
        "intro": "Admin overview surfaces governance pressure, review backlog, service impact, and audit follow-up without blending in authoring routes.",
    },
}


def render_home_hero(*, dashboard: dict[str, Any]) -> str:
    hero_copy = _HOME_HERO_COPY.get(str(dashboard.get("role") or ""), _HOME_HERO_COPY[OPERATOR_ROLE])
    layout_mode = str(dashboard.get("layout_mode") or "workshop").replace("-", " ")
    return (
        '<section class="home-hero" data-component="home-hero" data-surface="home">'
        f'<p class="home-hero__kicker">{escape(layout_mode)}</p>'
        f'<h1>{escape(hero_copy["headline"])}</h1>'
        f'<p class="home-hero__intro">{escape(hero_copy["intro"])}</p>'
        "</section>"
    )
