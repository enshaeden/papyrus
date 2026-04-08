from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from papyrus.application.demo_flow import OPERATOR_SCENARIOS, run_operator_scenario


class OperatorScenarioTests(unittest.TestCase):
    def _run(self, scenario: str) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            return run_operator_scenario(
                scenario=scenario,
                database_path=Path(temp_dir) / "scenario.db",
                source_root=Path(temp_dir) / "source",
                actor="tests",
            )

    def test_all_supported_scenarios_execute(self) -> None:
        for scenario in OPERATOR_SCENARIOS:
            with self.subTest(scenario=scenario):
                result = self._run(scenario)
                self.assertEqual(result["scenario"], scenario)
                self.assertIn("queue_counts", result)
                self.assertIn("trust_counts", result)

    def test_service_degradation_surfaces_impacted_objects(self) -> None:
        result = self._run("service_degradation")
        impacted_object_ids = [item["object_id"] for item in result["impacted_objects"]]
        self.assertIn("kb-demo-remote-access-service-record", impacted_object_ids)
        self.assertGreaterEqual(result["queue_counts"]["weak_evidence_items"], 1)

    def test_stale_knowledge_scenario_keeps_stale_object_visible(self) -> None:
        result = self._run("stale_knowledge")
        stale_object_ids = [item["object_id"] for item in result["stale_items"]]
        self.assertIn("kb-demo-identity-fallback-runbook", stale_object_ids)

    def test_conflicting_evidence_scenario_degrades_trust(self) -> None:
        result = self._run("conflicting_evidence")
        self.assertEqual(result["object_id"], "kb-demo-remote-access-service-record")
        self.assertIn(result["trust_state"], {"weak_evidence", "suspect"})
        self.assertGreaterEqual(result["evidence_status"]["snapshot_count"], 1)

    def test_review_backlog_scenario_increases_review_pressure(self) -> None:
        result = self._run("review_backlog")
        self.assertGreaterEqual(result["queue_counts"]["review_required"], 2)
        revision_ids = [item["revision_id"] for item in result["review_required"]]
        self.assertIn(result["revision_id"], revision_ids)


if __name__ == "__main__":
    unittest.main()
