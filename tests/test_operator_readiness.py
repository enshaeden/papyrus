from __future__ import annotations

import io
import json
import sqlite3
import subprocess
import sys
import tempfile
import urllib.parse
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.demo_flow import build_operator_demo_runtime
from papyrus.application.queries import search_knowledge_objects
from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.application.sync_flow import build_search_projection
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.web import app as web_app


def call_wsgi(
    application,
    path: str,
    *,
    method: str = "GET",
    json_payload: dict[str, object] | None = None,
) -> tuple[str, dict[str, str], str]:
    status_holder: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = {name: value for name, value in headers}

    body = json.dumps(json_payload or {}).encode("utf-8") if json_payload is not None else b""
    if "?" in path:
        path_info, query_string = path.split("?", 1)
    else:
        path_info, query_string = path, ""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path_info,
        "QUERY_STRING": query_string,
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(body)),
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(body),
        "wsgi.errors": io.StringIO(),
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    response_body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), response_body


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class OperatorReadinessTests(unittest.TestCase):
    def test_operator_cli_queue_matches_api_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            api_payload = json.loads(call_wsgi(api_app(database_path), "/queue")[2])
            cli_result = run_script("scripts/operator_view.py", "queue", "--db", str(database_path), "--format", "json")
            self.assertEqual(cli_result.returncode, 0, msg=cli_result.stderr)
            cli_payload = json.loads(cli_result.stdout)
            self.assertEqual(api_payload["queue"][0]["object_id"], cli_payload["queue"][0]["object_id"])
            self.assertEqual(api_payload["queue"][0]["posture"]["trust_summary"], cli_payload["queue"][0]["posture"]["trust_summary"])

    def test_demo_runtime_builds_meaningful_operational_tension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "demo.db"
            source_root = Path(temp_dir) / "repo"
            result = build_operator_demo_runtime(database_path=database_path, source_root=source_root)
            self.assertEqual(len(result["demo_objects"]), 7)
            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                approval_counts = {
                    row["approval_state"]: row["item_count"]
                    for row in connection.execute(
                        "SELECT approval_state, COUNT(*) AS item_count FROM search_documents GROUP BY approval_state"
                    ).fetchall()
                }
                trust_counts = {
                    row["trust_state"]: row["item_count"]
                    for row in connection.execute(
                        "SELECT trust_state, COUNT(*) AS item_count FROM search_documents GROUP BY trust_state"
                    ).fetchall()
                }
                suspect_event = connection.execute(
                    """
                    SELECT details_json
                    FROM audit_events
                    WHERE event_type = 'object_marked_suspect_due_to_change'
                      AND object_id = 'kb-demo-identity-token-known-error'
                    """
                ).fetchone()
                validation_run = connection.execute(
                    """
                    SELECT run_type, status
                    FROM validation_runs
                    WHERE run_id = 'demo-operator-check-20260407'
                    """
                ).fetchone()
            finally:
                connection.close()
            self.assertGreaterEqual(approval_counts.get("approved", 0), 1)
            self.assertGreaterEqual(approval_counts.get("in_review", 0), 1)
            self.assertGreaterEqual(trust_counts.get("trusted", 0), 1)
            self.assertGreaterEqual(trust_counts.get("weak_evidence", 0), 1)
            self.assertGreaterEqual(trust_counts.get("stale", 0), 1)
            self.assertGreaterEqual(trust_counts.get("suspect", 0), 1)
            self.assertIsNotNone(suspect_event)
            self.assertIsNotNone(validation_run)
            self.assertEqual(validation_run["run_type"], "manual_operator_check")

    def test_search_prefers_strongest_identity_answer_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "demo.db"
            source_root = Path(temp_dir) / "repo"
            build_operator_demo_runtime(database_path=database_path, source_root=source_root)

            results = search_knowledge_objects("identity", limit=200, database_path=database_path)
            demo_identity_results = [item for item in results if item["object_id"].startswith("kb-demo-identity")]

            self.assertGreaterEqual(len(demo_identity_results), 3)
            self.assertEqual(demo_identity_results[0]["object_id"], "kb-demo-identity-service-record")
            self.assertEqual(demo_identity_results[0]["approval_state"], "approved")
            self.assertEqual(demo_identity_results[0]["trust_state"], "weak_evidence")
            self.assertIn("kb-demo-identity-token-known-error", [item["object_id"] for item in demo_identity_results[1:]])
            self.assertIn("kb-demo-identity-fallback-runbook", [item["object_id"] for item in demo_identity_results[1:]])

    def test_governance_api_endpoints_require_actor_and_record_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            workflow = GovernanceWorkflow(database_path)
            created = workflow.create_object(
                object_id="kb-api-governance-object",
                object_type="runbook",
                title="API Governance Object",
                summary="Used to exercise operator governance endpoints.",
                owner="api_owner",
                team="IT Operations",
                canonical_path="knowledge/demo/api-governance-object.md",
                actor="tests",
            )
            application = api_app(database_path)

            status, _, body = call_wsgi(
                application,
                "/objects",
                method="POST",
                json_payload={
                    "object_id": "kb-api-missing-actor",
                    "object_type": "runbook",
                    "title": "API Missing Actor",
                    "summary": "Should fail without an actor.",
                    "owner": "api_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/demo/api-missing-actor.md",
                },
            )
            self.assertEqual(status, "400 Bad Request")
            self.assertIn("actor is required", body)

            status, _, body = call_wsgi(
                application,
                f"/objects/{urllib.parse.quote(created.object_id)}/mark-suspect",
                method="POST",
                json_payload={
                    "reason": "Dependency changed.",
                    "changed_entity_type": "service",
                    "changed_entity_id": "Remote Access",
                },
            )
            self.assertEqual(status, "400 Bad Request")
            self.assertIn("actor is required", body)

            status, _, body = call_wsgi(
                application,
                f"/objects/{urllib.parse.quote(created.object_id)}/mark-suspect",
                method="POST",
                json_payload={
                    "actor": "tests",
                    "reason": "Dependency changed.",
                    "changed_entity_type": "service",
                    "changed_entity_id": "Remote Access",
                },
            )
            self.assertEqual(status, "200 OK")
            payload = json.loads(body)
            self.assertEqual(payload["object_id"], created.object_id)
            self.assertEqual(payload["actor"], "tests")

            status, _, body = call_wsgi(
                application,
                "/validation-runs",
                method="POST",
                json_payload={
                    "actor": "tests",
                    "run_id": "api-validation-run",
                    "run_type": "manual_check",
                    "status": "passed",
                    "finding_count": 0,
                    "details": {"summary": "Smoke check"},
                },
            )
            self.assertEqual(status, "201 Created")
            payload = json.loads(body)
            self.assertEqual(payload["run_id"], "api-validation-run")

    def test_degraded_surfaces_return_actionable_runtime_unavailable_responses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_database_path = Path(temp_dir) / "missing-runtime.db"

            api_status, _, api_body = call_wsgi(api_app(missing_database_path), "/queue")
            self.assertEqual(api_status, "503 Service Unavailable")
            api_payload = json.loads(api_body)
            self.assertEqual(api_payload["category"], "runtime_rebuild_needed")
            self.assertIn("build_index.py", api_payload["action"])

            web_status, _, web_body = call_wsgi(web_app(missing_database_path), "/queue")
            self.assertEqual(web_status, "503 Service Unavailable")
            self.assertIn("Runtime unavailable", web_body)
            self.assertIn("build_index.py", web_body)


if __name__ == "__main__":
    unittest.main()
