from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import (
    escape,
    join_html,
    render_definition_rows,
    render_list,
    render_table,
)


def _data_token(value: object, *, fallback: str = "default") -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return normalized or fallback


_CONTEXT_PANEL_TOKENS = (
    "metadata",
    "governance",
    "filter",
    "progress",
    "support",
    "validation",
    "context",
    "evidence",
    "audit",
    "relationship",
    "cleanup",
    "contract",
    "posture",
    "status",
)


@dataclass
class ComponentPresenter:
    renderer: TemplateRenderer

    def list_body(
        self,
        *,
        items: list[str],
        empty_label: str,
        css_class: str = "panel-list",
    ) -> str:
        return (
            render_list(items, css_class=css_class)
            or f'<p class="empty-state-copy">{escape(empty_label)}</p>'
        )

    def surface_panel(
        self,
        *,
        title: str,
        body_html: str,
        eyebrow: str = "",
        footer_html: str = "",
        tone: str = "default",
        summary: str = "",
        css_class: str = "",
        body_class: str = "section-card-body",
        variant: str = "",
        surface: str = "",
        panel_role: str = "content-section",
    ) -> str:
        normalized_variant = _data_token(variant or tone)
        normalized_surface = _data_token(surface or eyebrow or title)
        return self.renderer.render(
            "partials/section_card.html",
            {
                "title": escape(title),
                "eyebrow": escape(eyebrow),
                "summary_html": (
                    f'<p class="governed-panel-summary">{escape(summary)}</p>'
                    if str(summary).strip()
                    else ""
                ),
                "body_html": body_html,
                "body_class": escape(body_class),
                "footer_html": footer_html,
                "tone": escape(tone),
                "css_class": escape(css_class),
                "component_variant": escape(normalized_variant),
                "component_surface": escape(normalized_surface),
                "panel_role": escape(panel_role),
            },
        )

    def content_section(self, **kwargs) -> str:
        return self.surface_panel(panel_role="content-section", **kwargs)

    def context_panel(self, **kwargs) -> str:
        return self.surface_panel(panel_role="context-panel", **kwargs)

    def section_card(self, **kwargs) -> str:
        tone = str(kwargs.get("tone") or "default").strip().lower()
        variant = str(kwargs.get("variant") or "")
        surface = str(kwargs.get("surface") or "")
        body_class = str(kwargs.get("body_class") or "")
        css_class = str(kwargs.get("css_class") or "")
        combined = " ".join((variant, surface, body_class, css_class)).lower()
        if tone != "default" or any(token in combined for token in _CONTEXT_PANEL_TOKENS):
            return self.context_panel(**kwargs)
        return self.content_section(**kwargs)

    def badge(self, *, label: str, value: object, tone: str) -> str:
        return self.renderer.render(
            "partials/badges.html",
            {
                "badge_label": escape(label),
                "badge_value": escape(value),
                "badge_tone": escape(tone),
            },
        )

    def summary_strip(
        self,
        *,
        title: str,
        badges: Iterable[str],
        summary: str = "",
        surface: str = "",
        variant: str = "default",
    ) -> str:
        return self.renderer.render(
            "partials/trust_summary.html",
            {
                "title": escape(title),
                "badges_html": join_html(list(badges), " "),
                "summary": escape(summary),
                "component_surface": escape(_data_token(surface or title)),
                "component_variant": escape(_data_token(variant)),
            },
        )

    def trust_summary(self, **kwargs) -> str:
        return self.summary_strip(**kwargs)

    def metadata_list(
        self,
        *,
        title: str,
        rows: list[tuple[str, str]],
        surface: str = "metadata",
    ) -> str:
        return self.context_panel(
            title=title,
            eyebrow="Metadata",
            body_html=render_definition_rows(rows),
            tone="context",
            variant="metadata",
            surface=surface,
        )

    def table(
        self,
        *,
        headers: list[str],
        rows: list[list[str]],
        row_attrs: list[dict[str, object] | None] | None = None,
        table_id: str,
        surface: str = "table",
        variant: str = "default",
    ) -> str:
        return self.renderer.render(
            "partials/queue_table.html",
            {
                "table_html": render_table(headers, rows, table_id=table_id, row_attrs=row_attrs),
                "component_surface": escape(_data_token(surface)),
                "component_variant": escape(_data_token(variant)),
            },
        )

    def queue_table(self, **kwargs) -> str:
        return self.table(**kwargs)

    def decision_cell(
        self,
        *,
        title_html: str,
        supporting_html: str = "",
        meta: Iterable[str] = (),
        badges: Iterable[str] = (),
        extra_html: str = "",
    ) -> str:
        badge_items = [item for item in badges if item]
        meta_items = [item for item in meta if item]
        return (
            '<div class="decision-cell" data-component="decision-cell">'
            + f'<div class="decision-primary">{title_html}</div>'
            + (
                '<div class="decision-badges">' + join_html(badge_items, " ") + "</div>"
                if badge_items
                else ""
            )
            + (
                f'<div class="decision-supporting">{supporting_html}</div>'
                if supporting_html
                else ""
            )
            + (
                '<div class="decision-meta-group">'
                + join_html([f'<p class="decision-meta">{item}</p>' for item in meta_items])
                + "</div>"
                if meta_items
                else ""
            )
            + extra_html
            + "</div>"
        )

    def decision_card(
        self,
        *,
        title_html: str,
        summary: str = "",
        detail: str = "",
        meta: Iterable[str] = (),
        badges: Iterable[str] = (),
        next_action: str = "",
        actions_html: str = "",
        tone: str = "default",
        surface: str = "decision",
    ) -> str:
        meta_items = [item for item in meta if item]
        badge_items = [item for item in badges if item]
        return (
            f'<article class="decision-card decision-card-{escape(tone)}"'
            f' data-component="decision-card" data-variant="{escape(_data_token(tone))}"'
            f' data-surface="{escape(_data_token(surface))}">'
            '<div class="decision-card-header">'
            '<div class="decision-card-heading">'
            f"<h3>{title_html}</h3>"
            + (f'<p class="decision-card-summary">{escape(summary)}</p>' if summary else "")
            + "</div>"
            + (f'<div class="badge-row">{join_html(badge_items, " ")}</div>' if badge_items else "")
            + "</div>"
            + (f'<p class="decision-card-detail">{escape(detail)}</p>' if detail else "")
            + (
                '<div class="decision-card-meta">'
                + join_html([f"<span>{item}</span>" for item in meta_items])
                + "</div>"
                if meta_items
                else ""
            )
            + (
                f'<p class="decision-card-next"><strong>Next:</strong> {escape(next_action)}</p>'
                if next_action
                else ""
            )
            + (f'<div class="decision-card-actions">{actions_html}</div>' if actions_html else "")
            + "</article>"
        )

    def inline_disclosure(self, *, label: str, body_html: str) -> str:
        return (
            '<details class="inline-disclosure" data-component="inline-disclosure">'
            f"<summary>{escape(label)}</summary>"
            f'<div class="inline-disclosure-body">{body_html}</div>'
            "</details>"
        )

    def object_header(
        self,
        *,
        object_type: str,
        object_id: str,
        title: str,
        summary: str,
        badges: Iterable[str],
        actions_html: str = "",
    ) -> str:
        return self.renderer.render(
            "partials/object_header.html",
            {
                "object_type": escape(object_type),
                "object_id": escape(object_id),
                "title": escape(title),
                "summary": escape(summary),
                "badges_html": join_html(list(badges), " "),
                "actions_html": actions_html,
            },
        )

    def empty_state(
        self,
        *,
        title: str,
        description: str,
        action_html: str = "",
        surface: str = "empty",
        variant: str = "default",
    ) -> str:
        return self.renderer.render(
            "partials/empty_state.html",
            {
                "title": escape(title),
                "description": escape(description),
                "action_html": action_html,
                "component_surface": escape(_data_token(surface or title)),
                "component_variant": escape(_data_token(variant)),
            },
        )

    def action_bar(
        self,
        *,
        items: list[str],
        surface: str = "actions",
        variant: str = "default",
    ) -> str:
        return self.renderer.render(
            "partials/action_bar.html",
            {
                "items_html": join_html(items),
                "component_surface": escape(_data_token(surface)),
                "component_variant": escape(_data_token(variant)),
            },
        )

    def filter_bar(
        self,
        *,
        title: str,
        controls_html: str,
        surface: str = "filters",
        variant: str = "default",
    ) -> str:
        return self.renderer.render(
            "partials/filter_bar.html",
            {
                "title": escape(title),
                "controls_html": controls_html,
                "component_surface": escape(_data_token(surface or title)),
                "component_variant": escape(_data_token(variant)),
            },
        )
