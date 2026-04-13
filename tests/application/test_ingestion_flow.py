from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import (
    ingest_file,
    ingestion_detail,
    mark_ingestion_converted,
    update_ingestion_mapping,
)
from papyrus.application.mapping_flow import map_to_blueprint


def governed_ingest_path(temp_dir: str, filename: str) -> tuple[Path, Path]:
    source_root = Path(temp_dir) / "repo"
    source_path = source_root / "build" / "local-ingest" / filename
    source_path.parent.mkdir(parents=True, exist_ok=True)
    return source_root, source_path


class IngestionFlowTests(unittest.TestCase):
    def test_markdown_ingestion_is_classified_before_mapping_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n- Reconnect client\n\n## Verification\n\n- Confirm tunnel\n",
                encoding="utf-8",
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )

            self.assertEqual(detail["filename"], "sample.md")
            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(detail["mapping_result"], {})
            self.assertEqual(detail["normalized_content"]["title"], "VPN Recovery")
            artifact_types = {artifact["artifact_type"] for artifact in detail["artifacts"]}
            self.assertTrue(
                {
                    "uploaded",
                    "parsed",
                    "normalized",
                    "classified",
                    "sections",
                    "stage_progress",
                }.issubset(artifact_types)
            )
            stage_progress = next(
                artifact["content"]
                for artifact in detail["artifacts"]
                if artifact["artifact_type"] == "stage_progress"
            )
            self.assertEqual(stage_progress["completed_stages"], ["upload", "parse", "classify"])
            self.assertEqual(stage_progress["current_stage"], "map")

    def test_ingestion_detail_exposes_workflow_projection_and_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n- Reconnect client\n\n## Verification\n\n- Confirm tunnel\n",
                encoding="utf-8",
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            classified_actions = {
                action["action_id"]: action for action in detail["workflow_projection"]["actions"]
            }
            self.assertEqual(detail["workflow_projection"]["summary"], "Generate mapping review")
            self.assertEqual(
                classified_actions["review_ingestion_mapping"]["availability"], "allowed"
            )
            self.assertEqual(
                classified_actions["convert_ingestion_to_draft"]["availability"], "illegal"
            )

            map_to_blueprint(
                ingestion_id=result["ingestion_id"],
                blueprint_id="runbook",
                database_path=database_path,
            )
            mapped = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            mapped_actions = {
                action["action_id"]: action for action in mapped["workflow_projection"]["actions"]
            }
            self.assertEqual(mapped["workflow_projection"]["rows"][0]["value"], "mapped")
            self.assertEqual(mapped_actions["review_ingestion_mapping"]["availability"], "allowed")
            self.assertEqual(
                mapped_actions["convert_ingestion_to_draft"]["availability"], "allowed"
            )

    def test_mapping_transition_requires_real_mapping_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n", encoding="utf-8"
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )

            with self.assertRaisesRegex(ValueError, "real mapping result exists"):
                update_ingestion_mapping(
                    ingestion_id=result["ingestion_id"],
                    mapping_result={},
                    blueprint_id="runbook",
                    database_path=database_path,
                )

            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(detail["mapping_result"], {})

    def test_conversion_transition_requires_real_mapping_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n", encoding="utf-8"
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )

            with self.assertRaisesRegex(
                ValueError, "real mapping result before it can be reviewed and converted"
            ):
                mark_ingestion_converted(
                    ingestion_id=result["ingestion_id"],
                    object_id="kb-vpn-recovery-imported",
                    revision_id="00000000-0000-0000-0000-000000000000",
                    database_path=database_path,
                )

            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertIsNone(detail["converted_revision_id"])

    def test_ordered_extraction_preserves_source_order_and_heading_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "ordered.md")
            source_path.write_text(
                "# Access Recovery\n\n"
                "## Procedure\n\n"
                "Confirm identity.\n\n"
                "- Reset access\n\n"
                "## Verification\n\n"
                "Confirm login succeeds.\n\n"
                "## Procedure\n\n"
                "Record the follow-up note.\n",
                encoding="utf-8",
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            sections = result["sections"]

            self.assertEqual(
                [(section["kind"], section["heading"], section["text"]) for section in sections],
                [
                    ("heading", "Access Recovery", "Access Recovery"),
                    ("heading", "Procedure", "Procedure"),
                    ("paragraph", "Procedure", "Confirm identity."),
                    ("list", "Procedure", "Reset access"),
                    ("heading", "Verification", "Verification"),
                    ("paragraph", "Verification", "Confirm login succeeds."),
                    ("heading", "Procedure", "Procedure"),
                    ("paragraph", "Procedure", "Record the follow-up note."),
                ],
            )
            self.assertEqual(
                [entry["text"] for entry in sections[2]["heading_path"]],
                ["Access Recovery", "Procedure"],
            )
            self.assertEqual(
                [entry["text"] for entry in sections[-1]["heading_path"]],
                ["Access Recovery", "Procedure"],
            )
            self.assertEqual(len({section["fragment_id"] for section in sections}), len(sections))

    def test_empty_markdown_is_flagged_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "empty.md")
            source_path.write_text("", encoding="utf-8")

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )

            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(
                detail["normalized_content"]["extraction_quality"]["state"], "degraded"
            )
            self.assertIn(
                "Markdown file is empty.", detail["normalized_content"]["parser_warnings"]
            )

    def test_weak_pdf_is_ingested_with_parser_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "weak.pdf")
            source_path.write_bytes(
                b"%PDF-1.4\n1 0 obj\n<< /Length 18 >>\nstream\nBT /F1 12 Tf ET\nendstream\nendobj\n%%EOF"
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )

            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(
                detail["normalized_content"]["extraction_quality"]["state"], "degraded"
            )
            self.assertTrue(detail["normalized_content"]["parser_warnings"])
            self.assertIn(
                "No extractable PDF text found.", detail["normalized_content"]["parser_warnings"][0]
            )

    def test_malformed_docx_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "broken.docx")
            source_path.write_bytes(b"not-a-docx")

            with self.assertRaisesRegex(ValueError, "malformed DOCX"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )

    def test_malformed_pdf_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "broken.pdf")
            source_path.write_bytes(b"not-a-pdf")

            with self.assertRaisesRegex(ValueError, "malformed PDF"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )

    def test_unsupported_file_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "notes.txt")
            source_path.write_text("unsupported", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unsupported ingestion file type"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )
