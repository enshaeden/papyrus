from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.event_flow import ingest_event
from papyrus.application.queries import impact_view_for_object, impact_view_for_service
from papyrus.application.sync_flow import build_search_projection


class ImpactPropagationTests(unittest.TestCase):
    def test_object_impact_view_includes_causal_reasoning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            ingest_event(
                database_path=database_path,
                event_type="service_change",
                source="local",
                entity_type="service",
                entity_id="Remote Access",
                payload={"summary": "Remote Access policy changed."},
                actor="tests",
            )

            impact = impact_view_for_object("kb-troubleshooting-vpn-connectivity", database_path=database_path)

            self.assertEqual(impact["entity"]["object_id"], "kb-troubleshooting-vpn-connectivity")
            self.assertIn("what_changed", impact["current_impact"])
            self.assertIn("why_impacted", impact["current_impact"])
            if impact["impacted_objects"]:
                first = impact["impacted_objects"][0]
                self.assertIn("reason", first)
                self.assertIn("propagation_path", first)
                self.assertTrue(first["propagation_path"])

    def test_service_impact_view_shows_recent_event_and_revalidation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            ingest_event(
                database_path=database_path,
                event_type="service_change",
                source="local",
                entity_type="service",
                entity_id="Remote Access",
                payload={"summary": "Remote Access policy changed."},
                actor="tests",
            )

            impact = impact_view_for_service("Remote Access", database_path=database_path)

            self.assertEqual(impact["entity"]["service_name"], "Remote Access")
            self.assertTrue(impact["recent_events"])
            self.assertIn("what_changed", impact["current_impact"])
            self.assertTrue(impact["impacted_objects"])
            self.assertTrue(impact["impacted_objects"][0]["revalidate"])


if __name__ == "__main__":
    unittest.main()
