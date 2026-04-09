from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import ingest_file
from papyrus.application.mapping_flow import convert_to_draft, map_to_blueprint
from papyrus.application.queries import review_detail


class IngestionToAuthoringIntegrationTests(unittest.TestCase):
    def test_imported_content_converts_into_normal_draft_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            source_path = Path(temp_dir) / "runbook.md"
            source_path.write_text(
                "# Access Recovery\n\n## Procedure\n\n- Confirm identity\n- Reset access\n\n## Verification\n\n- User can sign in\n",
                encoding="utf-8",
            )

            ingested = ingest_file(file_path=source_path, database_path=database_path)
            map_to_blueprint(ingestion_id=ingested["ingestion_id"], blueprint_id="runbook", database_path=database_path)
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-access-recovery-imported",
                title="Access Recovery",
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

            detail = review_detail(
                "kb-access-recovery-imported",
                converted["revision_id"],
                database_path=database_path,
            )
            self.assertEqual(detail["object"]["object_type"], "runbook")
            self.assertEqual(detail["revision"]["revision_state"], "draft")
            self.assertIn("section_content", detail["revision"])
