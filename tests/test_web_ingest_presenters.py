from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.ingest_presenter import (
    present_ingest_list_page,
    present_ingestion_detail_page,
    present_mapping_review_page,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


DETAIL = {
    "ingestion_id": "ing-1",
    "filename": "vpn.md",
    "ingestion_state": "mapped",
    "media_type": "text/markdown",
    "parser_name": "markdown",
    "normalized_content": {
        "title": "VPN Guide",
        "headings": ["Use"],
        "paragraphs": ["One"],
        "lists": [],
        "tables": [],
        "links": [],
        "parser_warnings": ["Weak heading"],
        "degradation_notes": [],
        "extraction_quality": {"state": "degraded", "score": 0.8, "summary": "Some structure was weak."},
    },
    "classification": {"blueprint_id": "runbook", "confidence": 0.95},
    "mapping_result": {
        "sections": {
            "use_when": {
                "match": {"heading": "Use"},
                "provenance": {"source_fragment_id": "f-1", "source_heading": "Use"},
                "confidence": 0.9,
                "conflict_state": "clear",
            }
        },
        "missing_sections": ["verification"],
        "low_confidence": [],
        "conflicts": [],
        "unmapped_content": [],
    },
    "workflow_projection": {
        "summary": "Review the mapping",
        "detail": "Mapping has gaps to close.",
        "actions": [{"action_id": "review_ingestion_mapping", "label": "Review mapping", "availability": "allowed"}],
    },
}

TAXONOMIES = {
    "teams": {"allowed_values": ["IT Operations"]},
    "review_cadences": {"allowed_values": ["quarterly"]},
    "statuses": {"allowed_values": ["draft", "active"]},
    "audiences": {"allowed_values": ["operator"]},
}


class IngestPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_ingest_list_presenter_assembles_upload_and_list_component_owners(self) -> None:
        page = present_ingest_list_page(
            TEMPLATE_RENDERER,
            ingestions=[
                {
                    "ingestion_id": "ing-1",
                    "filename": "vpn.md",
                    "ingestion_state": "mapped",
                    "blueprint_id": "runbook",
                    "updated_at": "2026-04-10",
                }
            ],
            errors=["Choose a file first."],
            allow_web_ingest_local_paths=True,
        )

        self.assert_component(page["page_context"]["upload_html"], "ingest-upload")
        self.assert_component(page["page_context"]["ingestions_html"], "ingest-list")

    def test_ingestion_detail_presenter_assembles_progress_stage_and_parsed_content_components(self) -> None:
        page = present_ingestion_detail_page(TEMPLATE_RENDERER, detail=DETAIL)

        page_html = page["page_context"]["progress_html"] + page["page_context"]["stage_html"] + page["page_context"]["detail_html"] + page["aside_html"]
        self.assert_component(page_html, "ingest-progress")
        self.assert_component(page_html, "ingest-stage-board")
        self.assert_component(page_html, "ingest-stage-card")
        self.assert_component(page_html, "ingest-parsed-content")
        self.assert_component(page_html, "ingest-parser-assessment")

    def test_mapping_review_presenter_assembles_local_mapping_and_conversion_components(self) -> None:
        page = present_mapping_review_page(
            TEMPLATE_RENDERER,
            detail=DETAIL,
            mapping=DETAIL["mapping_result"],
            errors=["Owner is required."],
            taxonomies=TAXONOMIES,
        )

        page_html = page["page_context"]["mapping_html"] + page["page_context"]["gaps_html"] + page["page_context"]["convert_html"]
        self.assert_component(page_html, "ingest-mapping-table")
        self.assert_component(page_html, "ingest-mapping-gaps")
        self.assert_component(page_html, "ingest-mapping-gap")
        self.assert_component(page_html, "ingest-convert-form")
