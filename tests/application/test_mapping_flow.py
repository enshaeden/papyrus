from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import ingest_file
from papyrus.application.mapping_flow import map_to_blueprint


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

            self.assertEqual(mapping["blueprint_id"], "known_error")
            self.assertIn("diagnostic_checks", mapping["missing_sections"])
            self.assertTrue(mapping["sections"]["diagnosis"]["confidence"] >= 0.0)
