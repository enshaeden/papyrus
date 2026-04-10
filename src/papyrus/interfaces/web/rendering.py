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
        normalized_shell_variant = shell_variant if shell_variant in {"normal", "focus", "minimal"} else "normal"
        actor_class = role_config.actor.actor_id.replace(".", "-")
        content_html = self.template_renderer.render(page_template, page_context or {})
        has_aside = bool(str(aside_html).strip()) and normalized_shell_variant == "normal"
        active_item = self._active_nav_item(role_config.nav_sections, active_nav=active_nav, current_path=current_path)
        topbar_html = self.template_renderer.render(
            "partials/topbar.html",
            {
                "search_value": escape(search_value),
                "topbar_menu_html": self._topbar_menu_html(
                    role_config=role_config,
                    active_item=active_item,
                    active_nav=active_nav,
                    current_path=current_path,
                    page_title=page_title,
                    shell_variant=normalized_shell_variant,
                    page_header=page_header or {},
                ),
            },
        )
        nav_sections_html = join_html(
            [
                (
                    '<div class="sidebar-block">'
                    f'<p class="sidebar-label">{escape(section.title)}</p>'
                    + (
                        f'<p class="sidebar-copy">{escape(section.description)}</p>'
                        if section.description
                        else ""
                    )
                    + join_html(
                        [
                            link(
                                item.label,
                                item.href,
                                css_class="sidebar-link is-active" if self._nav_item_is_active(item, active_nav=active_nav, current_path=current_path) else "sidebar-link",
                            )
                            for item in section.items
                        ]
                    )
                    + "</div>"
                )
                for section in role_config.nav_sections
            ]
        )
        sidebar_html = ""
        if normalized_shell_variant == "normal":
            sidebar_html = self.template_renderer.render(
                "partials/sidebar.html",
                {
                    "nav_sections_html": nav_sections_html,
                },
            )
        page_header_html = self._page_header_html(
            role_config=role_config,
            active_item=active_item,
            active_nav=active_nav,
            current_path=current_path,
            page_title=page_title,
            shell_variant=normalized_shell_variant,
            page_header=page_header or {},
        )
        aside_column_html = (
            f'<aside class="context-column">{aside_html}</aside>'
            if has_aside
            else ""
        )
        shell_columns_classes = ["shell-columns", f"shell-columns-{escape(normalized_shell_variant)}"]
        if sidebar_html.strip():
            shell_columns_classes.append("has-sidebar")
        if aside_column_html.strip():
            shell_columns_classes.append("has-aside")
        scripts_html = join_html(
            [f'<script src="{escape(path)}" defer></script>' for path in scripts],
            "\n",
        )
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
                "shell_variant_class": escape(f"shell-{normalized_shell_variant} actor-{actor_class}"),
                "shell_columns_class": escape(" ".join(shell_columns_classes)),
                "page_surface": escape(page_surface or active_nav or page_title),
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
    def _role_hint_label(role_hint: str) -> str:
        mapping = {
            "reader_writer": "Reader / Writer",
            "reviewer": "Reviewer",
            "manager": "Manager",
        }
        return mapping.get(str(role_hint), str(role_hint).replace("_", " ").title())

    @staticmethod
    def _path_matches(current_path: str, prefix: str) -> bool:
        if prefix.endswith("/"):
            return current_path.startswith(prefix)
        return current_path == prefix or current_path.startswith(prefix + "/")

    def _page_header_html(
        self,
        *,
        role_config,
        active_item,
        active_nav: str,
        current_path: str,
        page_title: str,
        shell_variant: str,
        page_header: dict[str, object],
    ) -> str:
        headline = str(page_header.get("headline") or "").strip()
        kicker = str(page_header.get("kicker") or "").strip()
        intro = str(page_header.get("intro") or "").strip()
        context_html = str(page_header.get("context_html") or "").strip()
        detail_html = str(page_header.get("detail_html") or "").strip()
        actions_html = str(page_header.get("actions_html") or "").strip()
        actor_banner_html = ""

        fragments = [
            actor_banner_html,
            f'<p class="page-kicker">{escape(kicker)}</p>' if kicker else "",
            f"<h1>{escape(headline)}</h1>" if headline else "",
            f'<p class="page-intro">{escape(intro)}</p>' if intro else "",
            context_html,
            detail_html,
            f'<div class="page-header-actions">{actions_html}</div>' if actions_html else "",
        ]
        header_body = join_html([fragment for fragment in fragments if str(fragment).strip()])
        if not header_body:
            return ""
        header_classes = ["page-header", f"page-header-{escape(shell_variant)}"]
        if actor_banner_html:
            header_classes.append("has-actor-banner")
        if intro:
            header_classes.append("has-intro")
        if actions_html:
            header_classes.append("has-actions")
        return f'<header class="{" ".join(header_classes)}">{header_body}</header>'

    def _topbar_menu_html(
        self,
        *,
        role_config,
        active_item,
        active_nav: str,
        current_path: str,
        page_title: str,
        shell_variant: str,
        page_header: dict[str, object],
    ) -> str:
        if shell_variant != "normal" or not bool(page_header.get("show_actor_banner")):
            return ""

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
        menu_items = [
            '<span class="topbar-menu-label">Working as</span>',
            actor_form_html,
        ]
        if bool(page_header.get("show_actor_links")):
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
        return '<nav class="topbar-menu" aria-label="Actor and quick navigation">' + join_html(menu_items) + "</nav>"
