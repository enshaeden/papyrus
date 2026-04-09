from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import ingest_file, ingestion_detail


class IngestionFlowTests(unittest.TestCase):
    def test_markdown_ingestion_is_normalized_and_stored(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_path = Path(temp_dir) / "sample.md"
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n- Reconnect client\n\n## Verification\n\n- Confirm tunnel\n",
                encoding="utf-8",
            )

            result = ingest_file(file_path=source_path, database_path=database_path)
            detail = ingestion_detail(ingestion_id=result["ingestion_id"], database_path=database_path)

            self.assertEqual(detail["filename"], "sample.md")
            self.assertEqual(detail["status"], "mapped")
            self.assertEqual(detail["normalized_content"]["title"], "VPN Recovery")
            self.assertGreaterEqual(len(detail["artifacts"]), 1)
