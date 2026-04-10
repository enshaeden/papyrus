from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, render_definition_rows, render_list, render_table


@dataclass
class ComponentPresenter:
    renderer: TemplateRenderer

    def _list_panel(
        self,
        *,
        title: str,
        eyebrow: str,
        items: list[str],
        empty_label: str,
        tone: str = "default",
    ) -> str:
        body_html = render_list(items, css_class="panel-list") or f'<p class="empty-state-copy">{escape(empty_label)}</p>'
        return self.section_card(
            title=title,
            eyebrow=eyebrow,
            body_html=body_html,
            tone=tone,
        )

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
        return self._list_panel(
            title=title,
            eyebrow="Evidence",
            items=items,
            empty_label=empty_label,
            tone="context",
        )

    def relationships_panel(self, *, title: str, items: list[str], empty_label: str) -> str:
        return self._list_panel(
            title=title,
            eyebrow="Relationships",
            items=items,
            empty_label=empty_label,
        )

    def audit_panel(self, *, title: str, items: list[str], empty_label: str) -> str:
        return self._list_panel(
            title=title,
            eyebrow="Audit",
            items=items,
            empty_label=empty_label,
            tone="context",
        )

    def queue_table(self, *, headers: list[str], rows: list[list[str]], table_id: str) -> str:
        return self.renderer.render(
            "partials/queue_table.html",
            {
                "table_html": render_table(headers, rows, table_id=table_id),
            },
        )

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
            '<div class="decision-cell">'
            + f'<div class="decision-primary">{title_html}</div>'
            + (
                '<div class="decision-badges">'
                + join_html(badge_items, " ")
                + "</div>"
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

    def inline_disclosure(self, *, label: str, body_html: str) -> str:
        return (
            '<details class="inline-disclosure">'
            f"<summary>{escape(label)}</summary>"
            f'<div class="inline-disclosure-body">{body_html}</div>'
            "</details>"
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

    def governed_status_panel(
        self,
        *,
        title: str,
        summary: str,
        body_html: str,
        eyebrow: str = "Governance",
        footer_html: str = "",
        tone: str = "context",
    ) -> str:
        return self.renderer.render(
            "partials/governed_status_panel.html",
            {
                "title": escape(title),
                "summary": escape(summary),
                "body_html": body_html,
                "eyebrow": escape(eyebrow),
                "footer_html": footer_html,
                "tone": escape(tone),
            },
        )

    def governed_action_panel(
        self,
        *,
        title: str,
        body_html: str,
        eyebrow: str = "Actions",
        footer_html: str = "",
        tone: str = "context",
    ) -> str:
        return self.renderer.render(
            "partials/governed_action_panel.html",
            {
                "title": escape(title),
                "body_html": body_html,
                "eyebrow": escape(eyebrow),
                "footer_html": footer_html,
                "tone": escape(tone),
            },
        )

    def governed_acknowledgement_panel(
        self,
        *,
        title: str,
        summary: str,
        body_html: str,
        eyebrow: str = "Acknowledgements",
        footer_html: str = "",
        tone: str = "warning",
    ) -> str:
        return self.renderer.render(
            "partials/governed_acknowledgement_panel.html",
            {
                "title": escape(title),
                "summary": escape(summary),
                "body_html": body_html,
                "eyebrow": escape(eyebrow),
                "footer_html": footer_html,
                "tone": escape(tone),
            },
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
