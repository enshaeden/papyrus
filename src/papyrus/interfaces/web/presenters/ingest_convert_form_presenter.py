from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.view_helpers import escape, slugify


def render_ingest_convert_form(
    *,
    forms: FormPresenter,
    detail: dict[str, object],
    errors: list[str] | None,
    taxonomies: dict[str, Any],
) -> str:
    error_html = (
        '<div class="ingest-convert-form__errors">'
        + "".join(f"<p>{escape(item)}</p>" for item in errors or [])
        + "</div>"
        if errors
        else ""
    )
    slug = slugify(str(detail["normalized_content"].get("title") or detail["filename"]))
    return (
        '<section class="ingest-convert-form" data-component="ingest-convert-form" data-surface="ingest-review">'
        '<p class="ingest-convert-form__kicker">Import</p>'
        "<h2>Create draft</h2>"
        f"{error_html}"
        '<form id="convert-to-draft-form" class="governed-form" method="post">'
        + forms.field(
            field_id="title",
            label="Title",
            control_html=forms.input(
                field_id="title",
                name="title",
                value=str(detail["normalized_content"].get("title") or detail["filename"]),
            ),
        )
        + forms.field(field_id="owner", label="Owner", control_html=forms.input(field_id="owner", name="owner", value=""))
        + forms.field(
            field_id="team",
            label="Team",
            control_html=forms.select(
                field_id="team",
                name="team",
                value="",
                options=taxonomies["teams"]["allowed_values"],
            ),
        )
        + forms.field(
            field_id="review_cadence",
            label="Review cadence",
            control_html=forms.select(
                field_id="review_cadence",
                name="review_cadence",
                value="",
                options=taxonomies["review_cadences"]["allowed_values"],
            ),
        )
        + forms.field(
            field_id="status",
            label="Status",
            control_html=forms.select(
                field_id="status",
                name="status",
                value="draft",
                options=taxonomies["statuses"]["allowed_values"],
            ),
        )
        + forms.field(
            field_id="audience",
            label="Audience",
            control_html=forms.select(
                field_id="audience",
                name="audience",
                value="",
                options=taxonomies["audiences"]["allowed_values"],
            ),
        )
        + '<section class="form-section"><h3>Publishing details</h3><p class="section-intro">Keep the new draft traceable and ready to publish.</p>'
        + forms.field(
            field_id="object_id",
            label="Reference code",
            control_html=forms.input(
                field_id="object_id",
                name="object_id",
                value=f"kb-{slug}",
            ),
            hint="Use lowercase words separated by hyphens. This stays with the guidance in links and search.",
        )
        + forms.field(
            field_id="canonical_path",
            label="Publishing location",
            control_html=forms.input(
                field_id="canonical_path",
                name="canonical_path",
                value=f"knowledge/imported/{slug}.md",
            ),
            hint="Where the published source will live in the knowledge library.",
        )
        + "</section>"
        + forms.button(label="Create draft", action_id="convert_ingestion_to_draft")
        + "</form></section>"
    )
