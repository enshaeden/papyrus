from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.view_helpers import escape, join_html

from .article_content_presenter import render_article_block


def render_article_section(*, section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    body_html = (
        join_html([render_article_block(block) for block in blocks])
        if blocks
        else f'<p class="article-empty">{escape(section.get("empty") or "No article content recorded.")}</p>'
    )
    return (
        '<section class="article-section" data-component="article-section" data-surface="object-detail">'
        f'<p class="article-section__kicker">{escape(section["eyebrow"])}</p>'
        f"<h2>{escape(section['title'])}</h2>"
        f"{body_html}</section>"
    )
