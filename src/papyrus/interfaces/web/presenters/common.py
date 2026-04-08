from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, render_definition_rows, render_list, render_table


@dataclass
class ComponentPresenter:
    renderer: TemplateRenderer

    def section_card(
        self,
        *,
        title: str,
        body_html: str,
        eyebrow: str = "",
        footer_html: str = "",
        tone: str = "default",
    ) -> str:
        return self.renderer.render(
            "partials/section_card.html",
            {
                "title": escape(title),
                "eyebrow": escape(eyebrow),
                "body_html": body_html,
                "footer_html": footer_html,
                "tone": escape(tone),
            },
        )

    def badge(self, *, label: str, value: object, tone: str) -> str:
        return self.renderer.render(
            "partials/badges.html",
            {
                "badge_label": escape(label),
                "badge_value": escape(value),
                "badge_tone": escape(tone),
            },
        )

    def trust_summary(self, *, title: str, badges: Iterable[str], summary: str = "") -> str:
        return self.renderer.render(
            "partials/trust_summary.html",
            {
                "title": escape(title),
                "badges_html": join_html(list(badges), " "),
                "summary": escape(summary),
            },
        )

    def metadata_list(self, *, title: str, rows: list[tuple[str, str]]) -> str:
        return self.renderer.render(
            "partials/metadata_list.html",
            {
                "title": escape(title),
                "rows_html": render_definition_rows(rows),
            },
        )

    def citations_panel(self, *, title: str, items: list[str], empty_label: str) -> str:
        body_html = render_list(items, css_class="panel-list") or f'<p class="empty-state-copy">{escape(empty_label)}</p>'
        return self.renderer.render(
            "partials/citations_panel.html",
            {
                "title": escape(title),
                "items_html": body_html,
            },
        )

    def relationships_panel(self, *, title: str, items: list[str], empty_label: str) -> str:
        body_html = render_list(items, css_class="panel-list") or f'<p class="empty-state-copy">{escape(empty_label)}</p>'
        return self.renderer.render(
            "partials/relationships_panel.html",
            {
                "title": escape(title),
                "items_html": body_html,
            },
        )

    def audit_panel(self, *, title: str, items: list[str], empty_label: str) -> str:
        body_html = render_list(items, css_class="panel-list") or f'<p class="empty-state-copy">{escape(empty_label)}</p>'
        return self.renderer.render(
            "partials/audit_panel.html",
            {
                "title": escape(title),
                "items_html": body_html,
            },
        )

    def queue_table(self, *, headers: list[str], rows: list[list[str]], table_id: str) -> str:
        return self.renderer.render(
            "partials/queue_table.html",
            {
                "table_html": render_table(headers, rows, table_id=table_id),
            },
        )

    def validation_summary(self, *, title: str, findings: list[str], empty_label: str = "No validation findings.") -> str:
        body_html = render_list(findings, css_class="validation-findings") or f'<p class="empty-state-copy">{escape(empty_label)}</p>'
        return self.renderer.render(
            "partials/validation_summary.html",
            {
                "title": escape(title),
                "items_html": body_html,
            },
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

    def empty_state(self, *, title: str, description: str, action_html: str = "") -> str:
        return self.renderer.render(
            "partials/empty_state.html",
            {
                "title": escape(title),
                "description": escape(description),
                "action_html": action_html,
            },
        )

    def action_bar(self, *, items: list[str]) -> str:
        return self.renderer.render(
            "partials/action_bar.html",
            {"items_html": join_html(items)},
        )

    def filter_bar(self, *, title: str, controls_html: str) -> str:
        return self.renderer.render(
            "partials/filter_bar.html",
            {
                "title": escape(title),
                "controls_html": controls_html,
            },
        )

    def validation_findings(self, *, title: str, items: list[str], tone: str = "warning") -> str:
        return self.renderer.render(
            "partials/validation_findings_list.html",
            {
                "title": escape(title),
                "tone": escape(tone),
                "items_html": render_list(items, css_class="validation-findings") or "",
            },
        )
