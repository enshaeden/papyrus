from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from typing import Iterable

from papyrus.interfaces.web.route_utils import WEB_ACTOR_OPTIONS, actor_home_path, actor_shell_for_id
from papyrus.interfaces.web.view_helpers import escape, join_html, link


PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


class TemplateRenderer:
    def __init__(self, template_root: Path):
        self.template_root = template_root

    def render(self, template_name: str, context: dict[str, object]) -> str:
        template_path = self.template_root / template_name
        text = template_path.read_text(encoding="utf-8")

        def replacement(match: re.Match[str]) -> str:
            key = match.group(1)
            return str(context.get(key, ""))

        return PLACEHOLDER_PATTERN.sub(replacement, text)


class PageRenderer:
    def __init__(self, package_root: Path):
        self.package_root = package_root
        self.template_renderer = TemplateRenderer(package_root / "templates")
        self.static_root = package_root / "static"

    def render_page(
        self,
        *,
        page_template: str,
        page_title: str,
        headline: str,
        kicker: str,
        intro: str,
        active_nav: str,
        search_value: str = "",
        flash_html: str = "",
        header_detail_html: str = "",
        action_bar_html: str = "",
        aside_html: str = "",
        scripts: Iterable[str] = (),
        page_context: dict[str, object] | None = None,
        actor_id: str = "",
        current_path: str = "",
        shell_variant: str = "default",
        header_mode: str = "default",
        header_context_html: str = "",
    ) -> str:
        role_config = actor_shell_for_id(actor_id)
        actor_class = role_config.actor.actor_id.replace(".", "-")
        content_html = self.template_renderer.render(page_template, page_context or {})
        topbar_html = self.template_renderer.render(
            "partials/topbar.html",
            {
                "search_value": escape(search_value),
                "actor_options_html": "\n".join(
                    f'<option value="{escape(actor.actor_id)}" data-home="{escape(actor_home_path(actor.actor_id))}">{escape(actor.display_name)}</option>'
                    for actor in WEB_ACTOR_OPTIONS
                ),
            },
        )
        nav_items = []
        seen_nav_keys: set[str] = set()
        for section in role_config.nav_sections:
            for item in section.items:
                if item.key in seen_nav_keys:
                    continue
                seen_nav_keys.add(item.key)
                nav_items.append(item)
        nav_links_html = join_html(
            [
                link(
                    item.label,
                    item.href,
                    css_class="sidebar-link is-active" if self._nav_item_is_active(item, active_nav=active_nav, current_path=current_path) else "sidebar-link",
                )
                for item in nav_items
            ]
        )
        sidebar_block_html = ""
        if shell_variant != "focus":
            sidebar_block_html = self.template_renderer.render(
                "partials/sidebar.html",
                {
                    "actor_role_summary": escape(role_config.summary),
                    "nav_links_html": nav_links_html,
                },
            )
        aside_block_html = (
            f'<aside class="context-column">{aside_html}</aside>'
            if shell_variant != "focus" and aside_html.strip()
            else ""
        )
        shell_columns_classes = ["shell-columns", f"shell-columns-{escape(shell_variant)}"]
        if sidebar_block_html.strip():
            shell_columns_classes.append("has-sidebar")
        if aside_block_html.strip():
            shell_columns_classes.append("has-aside")
        scripts_html = join_html(
            [f'<script src="{escape(path)}" defer></script>' for path in scripts],
            "\n",
        )
        actor_indicator_html = (
            f'<div class="actor-indicator actor-indicator-{escape(actor_class)}">'
            '<span class="actor-indicator-label">Actor</span>'
            f'<strong class="actor-indicator-name">{escape(role_config.actor.display_name)}</strong>'
            f'<span class="actor-indicator-summary">{escape(role_config.summary)}</span>'
            "</div>"
        )
        return self.template_renderer.render(
            "base.html",
            {
                "page_title": escape(page_title),
                "headline": escape(headline),
                "kicker": escape(kicker),
                "intro": escape(intro),
                "header_detail_html": header_detail_html,
                "header_context_html": actor_indicator_html + header_context_html,
                "topbar_html": topbar_html,
                "sidebar_block_html": sidebar_block_html,
                "flash_html": flash_html,
                "action_bar_html": action_bar_html,
                "content_html": content_html,
                "aside_block_html": aside_block_html,
                "scripts_html": scripts_html,
                "shell_variant_class": escape(f"shell-{shell_variant} actor-{actor_class}"),
                "shell_columns_class": escape(" ".join(shell_columns_classes)),
                "page_header_class": escape(f"page-header-{header_mode}"),
            },
        )

    def load_static_asset(self, relative_path: str) -> tuple[bytes, str] | None:
        asset_path = (self.static_root / relative_path).resolve()
        try:
            asset_path.relative_to(self.static_root.resolve())
        except ValueError:
            return None
        if not asset_path.exists() or not asset_path.is_file():
            return None
        content_type, _ = mimetypes.guess_type(str(asset_path))
        return asset_path.read_bytes(), content_type or "application/octet-stream"

    @staticmethod
    def _nav_item_is_active(item, *, active_nav: str, current_path: str) -> bool:
        if current_path:
            prefixes = item.match_prefixes or (item.href,)
            if any(PageRenderer._path_matches(current_path, prefix) for prefix in prefixes):
                return True
        return item.key == active_nav

    @staticmethod
    def _path_matches(current_path: str, prefix: str) -> bool:
        if prefix.endswith("/"):
            return current_path.startswith(prefix)
        return current_path == prefix or current_path.startswith(prefix + "/")
