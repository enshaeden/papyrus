from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.event_flow import ingest_event
from papyrus.application.sync_flow import build_search_projection


class EventFlowTests(unittest.TestCase):
    def test_service_change_event_is_stored_and_propagates_to_linked_objects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)

            result = ingest_event(
                database_path=database_path,
                event_type="service_change",
                source="local",
                entity_type="service",
                entity_id="Remote Access",
                payload={"summary": "Remote Access authentication behavior changed."},
                actor="tests",
            )

            self.assertEqual(result.event.event_type, "service_change")
            self.assertGreater(len(result.impacted_objects), 0)
            self.assertIn(
                "kb-troubleshooting-vpn-connectivity",
                {item["object_id"] for item in result.impacted_objects},
            )

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                stored_event = connection.execute(
                    "SELECT event_type, entity_type, entity_id, actor FROM events WHERE event_id = ?",
                    (result.event.event_id,),
                ).fetchone()
                impacted_row = connection.execute(
                    """
                    SELECT trust_state
                    FROM knowledge_objects
                    WHERE object_id = 'kb-troubleshooting-vpn-connectivity'
                    """
                ).fetchone()
                propagated_audit = connection.execute(
                    """
                    SELECT event_type, details_json
                    FROM audit_events
                    WHERE event_type = 'impact_propagated'
                      AND object_id = 'kb-troubleshooting-vpn-connectivity'
                    ORDER BY occurred_at DESC
                    LIMIT 1
                    """
                ).fetchone()
            finally:
                connection.close()

            self.assertIsNotNone(stored_event)
            self.assertEqual(stored_event["event_type"], "service_change")
            self.assertEqual(stored_event["entity_type"], "service")
            self.assertEqual(stored_event["entity_id"], "Remote Access")
            self.assertEqual(stored_event["actor"], "tests")
            self.assertIsNotNone(impacted_row)
            self.assertEqual(impacted_row["trust_state"], "suspect")
            self.assertIsNotNone(propagated_audit)
            self.assertIn("Remote Access", str(propagated_audit["details_json"]))


if __name__ == "__main__":
    unittest.main()
