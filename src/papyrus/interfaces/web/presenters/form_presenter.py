from __future__ import annotations

from dataclasses import dataclass

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link


@dataclass
class FormPresenter:
    renderer: TemplateRenderer

    def field(
        self,
        *,
        field_id: str,
        label: str,
        control_html: str,
        hint: str = "",
        errors: list[str] | None = None,
    ) -> str:
        error_html = ""
        if errors:
            error_html = join_html(
                [
                    self.renderer.render(
                        "partials/inline_validation_message.html",
                        {"message": escape(message)},
                    )
                    for message in errors
                ]
            )
        return self.renderer.render(
            "partials/form_field_group.html",
            {
                "field_id": escape(field_id),
                "field_label": escape(label),
                "field_control_html": control_html,
                "field_hint": escape(hint),
                "field_errors_html": error_html,
            },
        )

    def input(
        self,
        *,
        field_id: str,
        name: str,
        value: str,
        input_type: str = "text",
        placeholder: str = "",
        css_class: str = "text-input",
    ) -> str:
        return (
            f'<input id="{escape(field_id)}" name="{escape(name)}" type="{escape(input_type)}" '
            f'class="{escape(css_class)}" value="{escape(value)}" placeholder="{escape(placeholder)}" />'
        )

    def textarea(self, *, field_id: str, name: str, value: str, rows: int = 4, placeholder: str = "") -> str:
        return (
            f'<textarea id="{escape(field_id)}" name="{escape(name)}" rows="{rows}" '
            f'placeholder="{escape(placeholder)}">{escape(value)}</textarea>'
        )

    def checkbox(
        self,
        *,
        field_id: str,
        name: str,
        value: str,
        label: str,
        checked: bool = False,
    ) -> str:
        return (
            f'<label class="checkbox-field" for="{escape(field_id)}">'
            f'<input id="{escape(field_id)}" name="{escape(name)}" type="checkbox" value="{escape(value)}"'
            + (" checked" if checked else "")
            + " />"
            f'<span>{escape(label)}</span>'
            "</label>"
        )

    def select(
        self,
        *,
        field_id: str,
        name: str,
        value: str,
        options: list[str],
    ) -> str:
        option_html = "".join(
            f'<option value="{escape(option)}"{" selected" if option == value else ""}>{escape(option)}</option>'
            for option in options
        )
        return f'<select id="{escape(field_id)}" name="{escape(name)}">{option_html}</select>'

    def button(self, *, label: str, variant: str = "primary", button_type: str = "submit") -> str:
        return f'<button class="button button-{escape(variant)}" type="{escape(button_type)}">{escape(label)}</button>'

    def link_button(self, *, label: str, href: str, variant: str = "secondary") -> str:
        return link(label, href, css_class=f"button button-{variant}")

    def flash(self, *, title: str, body: str, tone: str = "info") -> str:
        return (
            f'<section class="flash flash-{escape(tone)}"><strong>{escape(title)}</strong>'
            f"<p>{escape(body)}</p></section>"
        )
