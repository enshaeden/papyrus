from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, join_html


def render_article_hero(*, hero: dict[str, str], actions: list[str]) -> str:
    return (
        '<section class="article-hero" data-component="article-hero" data-surface="object-detail">'
        f'<p class="article-hero__kicker">{escape(hero["eyebrow"])}</p>'
        f'<h1>{escape(hero["title"])}</h1>'
        f'<p class="article-hero__summary">{escape(hero["summary"])}</p>'
        + (
            f'<p class="article-hero__use-now">{escape(hero["use_now"])}</p>'
            if str(hero.get("use_now") or "").strip()
            else ""
        )
        + f'<div class="article-hero__actions" data-component="action-cluster">{join_html([action for action in actions if action])}</div>'
        + "</section>"
    )
