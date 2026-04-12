from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from typing import Iterable

from papyrus.interfaces.web.route_utils import WEB_ACTOR_OPTIONS, actor_home_path, actor_page_behavior, actor_page_config, actor_shell_for_id
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
        active_nav: str,
        page_header: dict[str, object] | None = None,
        search_value: str = "",
        flash_html: str = "",
        aside_html: str = "",
        scripts: Iterable[str] = (),
        page_context: dict[str, object] | None = None,
        actor_id: str = "",
        current_path: str = "",
        shell_variant: str = "normal",
        page_surface: str = "",
    ) -> str:
        role_config = actor_shell_for_id(actor_id)
        surface_id = str(page_surface or active_nav or page_title).strip()
        page_config = actor_page_config(actor_id, surface_id)
        page_behavior = actor_page_behavior(actor_id, surface_id)
        normalized_shell_variant = shell_variant if shell_variant in {"normal", "focus", "minimal"} else page_config.shell_variant
        content_html = self.template_renderer.render(page_template, page_context or {})
        active_item = self._active_nav_item(role_config.nav_sections, active_nav=active_nav, current_path=current_path)
        has_aside = bool(str(aside_html).strip()) and normalized_shell_variant == "normal"
        topbar_html = self.template_renderer.render(
            "partials/topbar.html",
            {
                "search_value": escape(search_value),
                "topbar_menu_html": self._topbar_menu_html(
                    role_config=role_config,
                    active_nav=active_nav,
                    current_path=current_path,
                    show_quick_links=page_config.show_quick_links,
                ),
            },
        )
        sidebar_html = ""
        if normalized_shell_variant == "normal":
            nav_sections_html = join_html(
                [
                    (
                        '<section class="sidebar-group">'
                        f'<p class="sidebar-label">{escape(section.title)}</p>'
                        + (f'<p class="sidebar-copy">{escape(section.description)}</p>' if section.description else "")
                        + '<ul class="sidebar-nav">'
                        + join_html(
                            [
                                "<li class=\"sidebar-item\">"
                                + link(
                                    item.label,
                                    item.href,
                                    css_class="sidebar-link is-active" if self._nav_item_is_active(item, active_nav=active_nav, current_path=current_path) else "sidebar-link",
                                )
                                + "</li>"
                                for item in section.items
                            ]
                        )
                        + "</ul></section>"
                    )
                    for section in role_config.nav_sections
                ]
            )
            sidebar_html = self.template_renderer.render(
                "partials/sidebar.html",
                {
                    "nav_sections_html": nav_sections_html,
                    "actor_name": escape(role_config.actor.display_name),
                    "actor_summary": escape(role_config.banner_summary),
                },
            )
        page_header_html = self._page_header_html(page_header=page_header or {}, header_variant=page_config.header_variant)
        aside_column_html = f'<aside class="context-column">{aside_html}</aside>' if has_aside else ""
        shell_columns_classes = ["shell-columns", f"shell-columns-{escape(normalized_shell_variant)}"]
        if sidebar_html.strip():
            shell_columns_classes.append("has-sidebar")
        if aside_column_html.strip():
            shell_columns_classes.append("has-aside")
        scripts_html = join_html([f'<script src="{escape(path)}" defer></script>' for path in scripts], "\n")
        return self.template_renderer.render(
            "base.html",
            {
                "page_title": escape(page_title),
                "page_header_html": page_header_html,
                "topbar_html": topbar_html,
                "sidebar_html": sidebar_html,
                "flash_html": flash_html,
                "content_html": content_html,
                "aside_column_html": aside_column_html,
                "scripts_html": scripts_html,
                "shell_variant_class": escape(
                    " ".join(
                        [
                            f"shell-{normalized_shell_variant}",
                            f"actor-{role_config.actor.actor_id.replace('.', '-')}",
                            f"surface-mode-{(page_behavior.mode if page_behavior is not None else 'default').replace('_', '-')}",
                            f"surface-density-{(page_behavior.density if page_behavior is not None else 'comfortable').replace('_', '-')}",
                            f"surface-columns-{(page_behavior.columns if page_behavior is not None else 'single').replace('_', '-')}",
                        ]
                    )
                ),
                "shell_columns_class": escape(" ".join(shell_columns_classes)),
                "page_surface": escape(surface_id),
                "page_mode": escape(page_behavior.mode if page_behavior is not None else "default"),
                "page_density": escape(page_behavior.density if page_behavior is not None else "comfortable"),
                "actor_id": escape(role_config.actor.actor_id),
                "content_layout_class": escape(f"content-layout-{(page_behavior.columns if page_behavior is not None else 'single').replace('_', '-')}"),
                "active_nav": escape(active_item.key if active_item is not None else active_nav or ""),
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
    def _active_nav_item(nav_sections, *, active_nav: str, current_path: str):
        for section in nav_sections:
            for item in section.items:
                if PageRenderer._nav_item_is_active(item, active_nav=active_nav, current_path=current_path):
                    return item
        return None

    @staticmethod
    def _path_matches(current_path: str, prefix: str) -> bool:
        if prefix == "/":
            return current_path == "/"
        if prefix.endswith("/"):
            return current_path.startswith(prefix)
        return current_path == prefix or current_path.startswith(prefix + "/")

    def _page_header_html(self, *, page_header: dict[str, object], header_variant: str) -> str:
        headline = str(page_header.get("headline") or "").strip()
        kicker = str(page_header.get("kicker") or "").strip()
        intro = str(page_header.get("intro") or "").strip()
        context_html = str(page_header.get("context_html") or "").strip()
        detail_html = str(page_header.get("detail_html") or "").strip()
        actions_html = str(page_header.get("actions_html") or "").strip()
        if not any((headline, kicker, intro, context_html, detail_html, actions_html)):
            return ""
        fragments = [
            f'<p class="page-kicker">{escape(kicker)}</p>' if kicker else "",
            f"<h1>{escape(headline)}</h1>" if headline else "",
            f'<p class="page-intro">{escape(intro)}</p>' if intro else "",
            context_html,
            detail_html,
            f'<div class="page-header-actions">{actions_html}</div>' if actions_html else "",
        ]
        return f'<header class="page-header page-header-{escape(header_variant)}">' + join_html([fragment for fragment in fragments if fragment]) + "</header>"

    def _topbar_menu_html(
        self,
        *,
        role_config,
        active_nav: str,
        current_path: str,
        show_quick_links: bool,
    ) -> str:
        actor_options_html = "\n".join(
            (
                f'<option value="{escape(actor.actor_id)}" data-home="{escape(actor_home_path(actor.actor_id))}"'
                + (' selected="selected"' if actor.actor_id == role_config.actor.actor_id else "")
                + f">{escape(actor.display_name)}</option>"
            )
            for actor in WEB_ACTOR_OPTIONS
        )
        actor_form_html = (
            '<form class="topbar-menu-form topbar-actor" action="/actor/select" method="post">'
            '<label class="sr-only" for="actor-select">Current actor</label>'
            '<input type="hidden" name="next_path" value="" data-current-path />'
            '<select id="actor-select" name="actor" data-actor-select>'
            f"{actor_options_html}"
            "</select>"
            "</form>"
        )
        menu_items = [actor_form_html]
        if show_quick_links:
            menu_items.extend(
                link(
                    item.label,
                    item.href,
                    css_class=(
                        "topbar-menu-chip is-active"
                        if self._nav_item_is_active(item, active_nav=active_nav, current_path=current_path)
                        else "topbar-menu-chip"
                    ),
                )
                for item in role_config.quick_links
            )
        return '<nav class="topbar-menu" aria-label="Actor controls">' + join_html(menu_items) + "</nav>"
