from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import ingest_file, ingestion_detail
from papyrus.application.mapping_flow import convert_to_draft, map_to_blueprint
from papyrus.application.queries import review_detail


class MappingFlowTests(unittest.TestCase):
    def test_mapping_flags_missing_sections_without_silent_assumptions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_path = Path(temp_dir) / "known-error.md"
            source_path.write_text(
                "# Login failure\n\n## Symptoms\n\nUsers cannot sign in.\n\n## Mitigations\n\n- Reset the cache\n",
                encoding="utf-8",
            )
            result = ingest_file(file_path=source_path, database_path=database_path)
            mapping = map_to_blueprint(ingestion_id=result["ingestion_id"], blueprint_id="known_error", database_path=database_path)
            detail = ingestion_detail(ingestion_id=result["ingestion_id"], database_path=database_path)

            self.assertEqual(mapping["blueprint_id"], "known_error")
            self.assertIn("diagnostic_checks", mapping["missing_sections"])
            self.assertTrue(mapping["sections"]["diagnosis"]["confidence"] >= 0.0)
            self.assertIsNotNone(mapping["sections"]["diagnosis"]["provenance"])
            self.assertEqual(detail["status"], "mapped")
            self.assertEqual(detail["mapping_result"]["blueprint_id"], "known_error")

    def test_mapping_records_conflicts_when_sections_compete_for_same_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_path = Path(temp_dir) / "conflicted-known-error.md"
            source_path.write_text(
                "# Login failure\n\n"
                "## Symptoms\n\n"
                "Users cannot sign in.\n\n"
                "## Diagnostic mitigation\n\n"
                "Diagnostic check mitigation workaround for cache corruption.\n",
                encoding="utf-8",
            )

            result = ingest_file(file_path=source_path, database_path=database_path)
            mapping = map_to_blueprint(ingestion_id=result["ingestion_id"], blueprint_id="known_error", database_path=database_path)

            used_fragments = [
                entry["provenance"]["source_fragment_id"]
                for entry in mapping["sections"].values()
                if entry.get("provenance") is not None
            ]
            self.assertEqual(len(used_fragments), len(set(used_fragments)))
            self.assertTrue(mapping["conflicts"])
            self.assertEqual(mapping["sections"]["diagnostic_checks"]["conflict_state"], "conflicted")
            self.assertEqual(mapping["sections"]["mitigations"]["conflict_state"], "conflicted")
            self.assertIsNotNone(mapping["sections"]["diagnostic_checks"]["provenance"])
            self.assertIsNone(mapping["sections"]["mitigations"]["match"])
            self.assertIn("diagnostic_checks", {item["section_id"] for item in mapping["conflicts"][0]["competing_sections"]})
            self.assertIn("mitigations", {item["section_id"] for item in mapping["conflicts"][0]["competing_sections"]})

    def test_mapping_keeps_unmapped_leftovers_with_fragment_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_path = Path(temp_dir) / "runbook-with-notes.md"
            source_path.write_text(
                "# Access recovery\n\n"
                "## Procedure\n\n"
                "- Confirm identity\n\n"
                "## Verification\n\n"
                "Confirm access works again.\n\n"
                "## Notes\n\n"
                "Keep this note for the reviewer.\n",
                encoding="utf-8",
            )

            result = ingest_file(file_path=source_path, database_path=database_path)
            mapping = map_to_blueprint(ingestion_id=result["ingestion_id"], blueprint_id="runbook", database_path=database_path)

            self.assertTrue(mapping["unmapped_content"])
            note_fragment = next(
                item for item in mapping["unmapped_content"] if item.get("text") == "Keep this note for the reviewer."
            )
            self.assertEqual(note_fragment["heading"], "Notes")
            self.assertTrue(note_fragment["fragment_id"].startswith("fragment-"))

    def test_convert_to_draft_leaves_unresolved_fields_blank_instead_of_spraying_section_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            source_path = Path(temp_dir) / "partial-known-error.md"
            source_path.write_text(
                "# Login failure\n\n"
                "## Symptoms\n\n"
                "- Users cannot sign in\n\n"
                "## Mitigations\n\n"
                "- Clear the stale token cache\n",
                encoding="utf-8",
            )

            ingested = ingest_file(file_path=source_path, database_path=database_path)
            map_to_blueprint(ingestion_id=ingested["ingestion_id"], blueprint_id="known_error", database_path=database_path)
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-login-failure-imported",
                title="Login failure",
                canonical_path="knowledge/imported/login-failure.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="after_change",
                status="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            detail = review_detail(
                "kb-login-failure-imported",
                converted["revision_id"],
                database_path=database_path,
            )
            diagnosis = detail["revision"]["section_content"]["diagnosis"]
            mitigations = detail["revision"]["section_content"]["mitigations"]

            self.assertEqual(diagnosis["symptoms"], ["Users cannot sign in"])
            self.assertEqual(diagnosis["scope"], "")
            self.assertEqual(diagnosis["cause"], "")
            self.assertEqual(diagnosis["_field_provenance"]["scope"]["status"], "manual_required")
            self.assertEqual(diagnosis["_field_provenance"]["cause"]["status"], "manual_required")
            self.assertEqual(mitigations["mitigations"], ["Clear the stale token cache"])
            self.assertEqual(mitigations["permanent_fix_status"], "")
            self.assertEqual(mitigations["_field_provenance"]["permanent_fix_status"]["status"], "manual_required")
            self.assertEqual(detail["object"]["summary"], "")
            self.assertEqual(detail["revision"]["metadata"]["summary"], "")
            self.assertLess(converted["completion"]["completion_percentage"], 100)

    def test_convert_to_draft_rejects_repeat_conversion_for_same_ingestion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            source_path = Path(temp_dir) / "runbook.md"
            source_path.write_text(
                "# Access recovery\n\n"
                "## Procedure\n\n"
                "- Confirm identity\n\n"
                "## Verification\n\n"
                "- Confirm access works again.\n",
                encoding="utf-8",
            )

            ingested = ingest_file(file_path=source_path, database_path=database_path)
            map_to_blueprint(ingestion_id=ingested["ingestion_id"], blueprint_id="runbook", database_path=database_path)
            first_conversion = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-access-recovery-imported",
                title="Access recovery",
                canonical_path="knowledge/imported/access-recovery.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="quarterly",
                status="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            with self.assertRaisesRegex(ValueError, "already been reviewed and converted"):
                convert_to_draft(
                    ingestion_id=ingested["ingestion_id"],
                    object_id="kb-access-recovery-imported-duplicate",
                    title="Access recovery duplicate",
                    canonical_path="knowledge/imported/access-recovery-duplicate.md",
                    owner="workflow_owner",
                    team="IT Operations",
                    review_cadence="quarterly",
                    status="draft",
                    audience="service_desk",
                    actor="local.operator",
                    database_path=database_path,
                    source_root=source_root,
                )

            detail = ingestion_detail(ingestion_id=ingested["ingestion_id"], database_path=database_path)
            self.assertEqual(detail["status"], "reviewed")
            self.assertEqual(detail["converted_object_id"], "kb-access-recovery-imported")
            self.assertEqual(detail["converted_revision_id"], first_conversion["revision_id"])
