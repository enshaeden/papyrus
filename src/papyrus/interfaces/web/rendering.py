from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from papyrus.interfaces.web.route_utils import WEB_ACTOR_OPTIONS
from papyrus.interfaces.web.view_helpers import escape, join_html, link


PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    href: str


NAV_ITEMS = (
    NavItem("read", "Read", "/queue"),
    NavItem("write", "Write", "/write/objects/new"),
    NavItem("manage", "Manage", "/dashboard/trust"),
    NavItem("queue", "Queue", "/manage/queue"),
    NavItem("services", "Services", "/services"),
    NavItem("validation", "Validation", "/manage/validation-runs"),
)

QUICK_LINKS = (
    ("Trust Dashboard", "/dashboard/trust"),
    ("Audit Trail", "/manage/audit"),
    ("New Revision", "/write/objects/new"),
)


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
    ) -> str:
        content_html = self.template_renderer.render(page_template, page_context or {})
        quick_links_html = join_html(
            [
                link(label, href, css_class="quick-link")
                for label, href in QUICK_LINKS
            ]
        )
        topbar_html = self.template_renderer.render(
            "partials/topbar.html",
            {
                "quick_links_html": quick_links_html,
                "search_value": escape(search_value),
                "actor_options_html": "\n".join(
                    f'<option value="{escape(actor.actor_id)}">{escape(actor.display_name)}</option>'
                    for actor in WEB_ACTOR_OPTIONS
                ),
            },
        )
        nav_links_html = join_html(
            [
                link(
                    item.label,
                    item.href,
                    css_class="sidebar-link is-active" if item.key == active_nav else "sidebar-link",
                )
                for item in NAV_ITEMS
            ]
        )
        sidebar_html = self.template_renderer.render(
            "partials/sidebar.html",
            {"nav_links_html": nav_links_html},
        )
        scripts_html = join_html(
            [f'<script src="{escape(path)}" defer></script>' for path in scripts],
            "\n",
        )
        return self.template_renderer.render(
            "base.html",
            {
                "page_title": escape(page_title),
                "headline": escape(headline),
                "kicker": escape(kicker),
                "intro": escape(intro),
                "header_detail_html": header_detail_html,
                "topbar_html": topbar_html,
                "sidebar_html": sidebar_html,
                "flash_html": flash_html,
                "action_bar_html": action_bar_html,
                "content_html": content_html,
                "aside_html": aside_html,
                "scripts_html": scripts_html,
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
