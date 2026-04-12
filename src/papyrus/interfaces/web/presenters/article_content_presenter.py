from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.view_helpers import escape, join_html


def render_article_block(block: dict[str, Any]) -> str:
    kind = str(block.get("kind") or "")
    title = str(block.get("title") or "").strip()
    title_html = f'<p class="article-block-title">{escape(title)}</p>' if title else ""
    if kind == "paragraph":
        return f'<div class="article-block article-block-paragraph">{title_html}<p>{escape(block["text"])}</p></div>'
    if kind == "list":
        return (
            f'<div class="article-block article-block-list">{title_html}<ul class="article-list">'
            + join_html([f"<li>{escape(item)}</li>" for item in block["items"]])
            + "</ul></div>"
        )
    if kind == "facts":
        return (
            f'<div class="article-block article-block-facts">{title_html}<dl class="article-facts">'
            + join_html([f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>" for label, value in block["rows"]])
            + "</dl></div>"
        )
    return ""
