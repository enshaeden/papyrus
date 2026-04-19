from __future__ import annotations

import mimetypes
import re
from collections.abc import Iterable
from pathlib import Path

from papyrus.interfaces.web.experience import experience_for_role
from papyrus.interfaces.web.urls import home_url, search_url
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
        role_id: str = "",
        current_path: str = "",
        shell_variant: str = "normal",
        header_variant: str | None = None,
        page_surface: str = "",
    ) -> str:
        page_context_dict = page_context or {}
        header_kicker = str(page_context_dict.get("action_kicker") or "").strip()
        role_config = experience_for_role(role_id or "operator")
        surface_id = str(page_surface or active_nav or page_title).strip()
        page_config = role_config.page_config(surface_id)
        page_behavior = role_config.page_behavior(surface_id)
        normalized_shell_variant = (
            shell_variant
            if shell_variant in {"normal", "focus", "minimal"}
            else page_config.shell_variant
        )
        content_html = self.template_renderer.render(page_template, page_context or {})
        active_item = self._active_nav_item(
            role_config.nav_sections, active_nav=active_nav, current_path=current_path
        )
        has_aside = bool(str(aside_html).strip()) and normalized_shell_variant == "normal"
        topbar_html = self.template_renderer.render(
            "partials/topbar.html",
            {
                "home_href": escape(home_url(role_config.role)),
                "search_action": escape(search_url(role_config.role)),
                "search_value": escape(search_value),
                "topbar_menu_html": self._topbar_menu_html(
                    role_config=role_config,
                    active_nav=active_nav,
                    show_quick_links=page_config.show_quick_links,
                ),
            },
        )
        sidebar_html = ""
        if normalized_shell_variant in {"normal", "minimal"}:
            nav_sections_html = join_html(
                [
                    (
                        '<section class="sidebar-group">'
                        f'<p class="sidebar-label">{escape(section.title)}</p>'
                        + '<ul class="sidebar-nav">'
                        + join_html(
                            [
                                '<li class="sidebar-item">'
                                + f'<a class="{"sidebar-link is-active" if self._nav_item_is_active(item, active_nav=active_nav, current_path=current_path) else "sidebar-link"}" href="{escape(item.href)}">'
                                + f"{escape(item.label)}"
                                + "</a>"
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
                },
            )
        page_header_html = self._page_header_html(
            page_header=page_header or {},
            header_variant=header_variant or page_config.header_variant,
            kicker_override=header_kicker,
        )
        if (header_variant or page_config.header_variant) == "article":
            aside_column_html = ""
            shell_columns_classes = ["shell-columns", "shell-columns-minimal"]
            if sidebar_html.strip():
                shell_columns_classes.append("has-sidebar")
        else:
            aside_column_html = (
                f'<aside class="context-column">{aside_html}</aside>' if has_aside else ""
            )
            shell_columns_classes = [
                "shell-columns",
                f"shell-columns-{escape(normalized_shell_variant)}",
            ]
            if sidebar_html.strip():
                shell_columns_classes.append("has-sidebar")
            if aside_column_html.strip():
                shell_columns_classes.append("has-aside")
        scripts_html = join_html(
            [f'<script src="{escape(path)}" defer></script>' for path in scripts], "\n"
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
                "shell_variant_class": escape(
                    " ".join(
                        [
                            f"shell-{normalized_shell_variant}",
                            f"role-{role_config.role}",
                            f"surface-mode-{(page_behavior.mode if page_behavior is not None else 'default').replace('_', '-')}",
                            f"surface-density-{(page_behavior.density if page_behavior is not None else 'comfortable').replace('_', '-')}",
                            f"surface-columns-{(page_behavior.columns if page_behavior is not None else 'single').replace('_', '-')}",
                        ]
                    )
                ),
                "shell_columns_class": escape(" ".join(shell_columns_classes)),
                "page_surface": escape(surface_id),
                "page_mode": escape(page_behavior.mode if page_behavior is not None else "default"),
                "page_density": escape(
                    page_behavior.density if page_behavior is not None else "comfortable"
                ),
                "role_id": escape(role_config.role),
                "content_layout_class": escape(
                    f"content-layout-{(page_behavior.columns if page_behavior is not None else 'single').replace('_', '-')}"
                ),
                "active_nav": escape(
                    active_item.key if active_item is not None else active_nav or ""
                ),
                "is_luxury": (header_variant or page_config.header_variant) == "article",
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
            prefixes = item.match_prefixes if item.match_prefixes is not None else (item.href,)
            if any(PageRenderer._path_matches(current_path, prefix) for prefix in prefixes):
                return True
        return item.key == active_nav

    @staticmethod
    def _active_nav_item(nav_sections, *, active_nav: str, current_path: str):
        for section in nav_sections:
            for item in section.items:
                if PageRenderer._nav_item_is_active(
                    item, active_nav=active_nav, current_path=current_path
                ):
                    return item
        return None

    @staticmethod
    def _path_matches(current_path: str, prefix: str) -> bool:
        if prefix == "/":
            return current_path == "/"
        if prefix.endswith("/"):
            return current_path.startswith(prefix)
        return current_path == prefix or current_path.startswith(prefix + "/")

    def _page_header_html(
        self, *, page_header: dict[str, object], header_variant: str, kicker_override: str = ""
    ) -> str:
        headline = str(page_header.get("headline") or "").strip()
        kicker = str(page_header.get("kicker") or "").strip()
        context_html = str(page_header.get("context_html") or "").strip()
        detail_html = str(page_header.get("detail_html") or "").strip()
        actions_html = str(page_header.get("actions_html") or "").strip()
        if not any((headline, kicker, context_html, detail_html, actions_html)):
            return ""

        if header_variant == "article":
            return (
                '<div class="article-header" data-component="article-header">'
                + '<a href="javascript:history.back()" class="article-back-link"><i data-lucide="arrow-left"></i> Back</a>'
                + f'<p class="article-kicker">{escape(kicker_override or "Governance")}</p>'
                + f"<h1>{escape(page_header.get('headline', ''))}</h1>"
                + '<div class="article-meta-row">'
                + '<div class="article-author">'
                + '<div class="user-avatar user-avatar-operator">JS</div>'
                + '<div class="article-author-info">'
                + '<span class="article-author-name">Justin Sadow</span>'
                + '<span class="article-author-role">Platform Operator</span>'
                + "</div></div>"
                + '<div class="article-meta-item"><i data-lucide="clock"></i> 4 min read</div>'
                + '<div class="article-meta-item"><i data-lucide="shield-check"></i> Verified</div>'
                + "</div></div>"
            )

        fragments = [
            f'<p class="page-kicker">{escape(kicker)}</p>' if kicker else "",
            f"<h1>{escape(headline)}</h1>" if headline else "",
            context_html,
            detail_html,
            f'<div class="page-header-actions" data-component="action-cluster">{actions_html}</div>'
            if actions_html
            else "",
        ]
        return (
            f'<header class="page-header page-header-{escape(header_variant)}">'
            + join_html([fragment for fragment in fragments if fragment])
            + "</header>"
        )

    def _topbar_menu_html(
        self,
        *,
        role_config,
        active_nav: str,
        show_quick_links: bool,
    ) -> str:
        menu_items = [
            f'<span class="topbar-menu-chip is-active topbar-menu-role">{escape(role_config.label)}</span>'
        ]
        if show_quick_links:
            menu_items.extend(
                link(
                    item.label,
                    item.href,
                    css_class=(
                        "topbar-menu-chip is-active"
                        if self._nav_item_is_active(item, active_nav=active_nav, current_path="")
                        else "topbar-menu-chip"
                    ),
                )
                for item in role_config.quick_links
            )
        return (
            '<nav class="topbar-menu" aria-label="System controls">'
            + join_html(menu_items)
            + "</nav>"
        )
