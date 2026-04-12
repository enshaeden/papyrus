from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    render_action_descriptor_panel,
    render_workflow_projection_panel,
    workflow_actions,
)
from papyrus.interfaces.web.presenters.ingest_convert_form_presenter import render_ingest_convert_form
from papyrus.interfaces.web.presenters.ingest_list_presenter import render_ingest_list
from papyrus.interfaces.web.presenters.ingest_mapping_gaps_presenter import render_ingest_mapping_gaps
from papyrus.interfaces.web.presenters.ingest_mapping_table_presenter import render_ingest_mapping_table
from papyrus.interfaces.web.presenters.ingest_parsed_content_presenter import render_ingest_parsed_content
from papyrus.interfaces.web.presenters.ingest_parser_assessment_presenter import render_ingest_parser_assessment
from papyrus.interfaces.web.presenters.ingest_progress_presenter import render_ingest_progress
from papyrus.interfaces.web.presenters.ingest_stage_board_presenter import render_ingest_stage_board
from papyrus.interfaces.web.presenters.ingest_upload_presenter import render_ingest_upload
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import join_html, quoted_path


def _ingestion_action_href(*, detail: dict[str, object], action: dict[str, object]) -> str | None:
    ingestion_id = quoted_path(str(detail["ingestion_id"]))
    action_id = str(action.get("action_id") or "")
    if action_id == "review_ingestion_mapping":
        return f"/ingest/{ingestion_id}/review"
    if action_id == "convert_ingestion_to_draft":
        return f"/ingest/{ingestion_id}/review#convert-to-draft-form"
    if action_id == "open_converted_draft" and detail.get("converted_object_id") and detail.get("converted_revision_id"):
        return (
            f"/write/objects/{quoted_path(str(detail['converted_object_id']))}/revisions/new"
            f"?revision_id={quoted_path(str(detail['converted_revision_id']))}"
        )
    return None


def _ingest_aside_html(components: ComponentPresenter, *, detail: dict[str, object], surface: str) -> str:
    return join_html(
        [
            render_workflow_projection_panel(
                components,
                title="Import workflow contract",
                projection=detail.get("workflow_projection"),
            ),
            render_action_descriptor_panel(
                components,
                title="Import workflow actions",
                actions=workflow_actions(detail.get("workflow_projection")),
                href_resolver=lambda action: _ingestion_action_href(detail=detail, action=action),
            ),
            render_ingest_parser_assessment(detail=detail, surface=surface),
        ]
    )


def present_ingest_list_page(
    renderer: TemplateRenderer,
    *,
    ingestions: list[dict[str, object]],
    errors: list[str] | None,
    allow_web_ingest_local_paths: bool,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    forms = FormPresenter(renderer)
    return {
        "page_template": "pages/ingest_list.html",
        "page_title": "Import workbench",
        "page_header": {
            "headline": "Import workbench",
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": "",
        "page_context": {
            "upload_html": render_ingest_upload(
                components=components,
                forms=forms,
                errors=errors,
                allow_web_ingest_local_paths=allow_web_ingest_local_paths,
            ),
            "ingestions_html": render_ingest_list(
                components=components,
                ingestions=ingestions,
                allow_web_ingest_local_paths=allow_web_ingest_local_paths,
            ),
        },
        "page_surface": "ingest",
    }


def present_ingestion_detail_page(renderer: TemplateRenderer, *, detail: dict[str, object]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    return {
        "page_template": "pages/ingest_detail.html",
        "page_title": f"Ingestion {detail['filename']}",
        "page_header": {
            "headline": detail["filename"],
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": _ingest_aside_html(components, detail=detail, surface="ingest-detail"),
        "page_context": {
            "progress_html": render_ingest_progress(renderer, detail=detail, surface="ingest-detail"),
            "stage_html": render_ingest_stage_board(detail=detail),
            "detail_html": render_ingest_parsed_content(normalized=detail["normalized_content"], surface="ingest-detail"),
        },
        "page_surface": "ingest-detail",
    }


def present_mapping_review_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, object],
    mapping: dict[str, object],
    errors: list[str] | None,
    taxonomies: dict[str, Any],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    forms = FormPresenter(renderer)
    return {
        "page_template": "pages/ingest_mapping_review.html",
        "page_title": f"Review mapping for {detail['filename']}",
        "page_header": {
            "headline": f"Review mapping for {detail['filename']}",
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": _ingest_aside_html(components, detail=detail, surface="ingest-review"),
        "page_context": {
            "progress_html": render_ingest_progress(renderer, detail=detail, surface="ingest-review"),
            "mapping_html": render_ingest_mapping_table(components=components, mapping=mapping),
            "gaps_html": render_ingest_mapping_gaps(mapping=mapping),
            "convert_html": render_ingest_convert_form(
                forms=forms,
                detail=detail,
                errors=errors,
                taxonomies=taxonomies,
            ),
        },
        "page_surface": "ingest-review",
    }
