from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.read_models.content_health import (  # noqa: E402
    CONTENT_HEALTH_SECTIONS,
    collect_content_health_sections,
)
from papyrus.application.sync_flow import build_search_projection  # noqa: E402
from tests.source_workspace import fixture_source_root  # noqa: E402


class ContentHealthReadModelTests(unittest.TestCase):
    def test_usefulness_sections_are_part_of_stable_contract(self) -> None:
        for section in (
            "unclear-ownership",
            "weak-evidence",
            "placeholder-heavy",
            "legacy-blueprint-fallback",
            "migration-gaps",
        ):
            self.assertIn(section, CONTENT_HEALTH_SECTIONS)

    def test_source_backed_usefulness_sections_report_known_migration_findings(self) -> None:
        outputs = collect_content_health_sections(
            [
                "placeholder-heavy",
                "legacy-blueprint-fallback",
                "migration-gaps",
            ],
            source_workspace_root=fixture_source_root(),
        )

        placeholder_lines = outputs["placeholder-heavy"]
        fallback_lines = outputs["legacy-blueprint-fallback"]
        migration_lines = outputs["migration-gaps"]

        self.assertTrue(
            any(
                "kb-applications-access-and-license-management-add-productivity-platform-licenses"
                in line
                and "<PRODUCTIVITY_PLATFORM>" in line
                for line in placeholder_lines
            )
        )
        self.assertTrue(
            any(
                "kb-applications-access-and-license-management-add-productivity-platform-licenses"
                in line
                and "source_type=imported" in line
                for line in fallback_lines
            )
        )
        self.assertTrue(
            any(
                "kb-applications-access-and-license-management-add-productivity-platform-licenses"
                in line
                and "placeholder-heavy(" in line
                and "legacy-blueprint-fallback" in line
                for line in migration_lines
            )
        )

    def test_runtime_backed_usefulness_sections_report_evidence_risk(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())

            outputs = collect_content_health_sections(
                ["unclear-ownership", "weak-evidence"],
                database_path=database_path,
            )

        self.assertEqual(outputs["unclear-ownership"], [])
        self.assertTrue(
            any(
                "kb-troubleshooting-audio-video-boardrooms-standard-av-room-user-guide" in line
                and "trust=weak_evidence" in line
                and "citation_health_rank=" in line
                for line in outputs["weak-evidence"]
            )
        )


if __name__ == "__main__":
    unittest.main()
