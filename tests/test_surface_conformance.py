from __future__ import annotations

import io
import json
import sqlite3
import sys
import tempfile
import unittest
import urllib.parse
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.application.sync_flow import build_search_projection
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.cli import operator_main
from papyrus.interfaces.web import app as web_app
from papyrus.infrastructure.transactional_mutation import TransactionalMutation


def call_wsgi(
    application,
    path: str,
    *,
    method: str = "GET",
    form: dict[str, object] | None = None,
    json_payload: dict[str, object] | None = None,
) -> tuple[str, dict[str, str], str]:
    status_holder: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = {name: value for name, value in headers}

    if json_payload is not None:
        body = json.dumps(json_payload).encode("utf-8")
        content_type = "application/json"
    else:
        body = urllib.parse.urlencode(form or {}, doseq=True).encode("utf-8")
        content_type = "application/x-www-form-urlencoded"

    if "?" in path:
        path_info, query_string = path.split("?", 1)
    else:
        path_info, query_string = path, ""

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path_info,
        "QUERY_STRING": query_string,
        "CONTENT_TYPE": content_type,
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
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), body


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Surface conformance for {title.lower()}",
        "knowledge_object_type": "runbook",
        "legacy_article_type": None,
        "status": "active",
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": ["<VPN_SERVICE>"],
        "tags": ["vpn"],
        "created": "2026-04-09",
        "updated": "2026-04-09",
        "last_reviewed": "2026-04-09",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": ["Remote Access"],
        "prerequisites": ["Open the incident ticket."],
        "steps": ["Perform the primary remediation step."],
        "verification": ["Confirm the workflow completed successfully."],
        "rollback": ["Undo the last remediation step."],
        "citations": [
            {
                "source_title": "Seed import manifest",
                "source_type": "document",
                "source_ref": "migration/import-manifest.yml",
                "note": "Surface conformance evidence.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "related_articles": [],
        "references": [{"title": "Seed import manifest", "path": "migration/import-manifest.yml"}],
        "change_log": [{"date": "2026-04-09", "summary": "Surface conformance draft.", "author": "tests"}],
    }


def read_truth(database_path: Path, *, object_id: str, revision_id: str, reviewer: str, source_root: Path) -> dict[str, object]:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        revision_row = connection.execute(
            """
            SELECT revision_review_state, revision_state
            FROM knowledge_revisions
            WHERE revision_id = ?
            """,
            (revision_id,),
        ).fetchone()
        assignment_row = connection.execute(
            """
            SELECT state
            FROM review_assignments
            WHERE revision_id = ? AND reviewer = ?
            ORDER BY assigned_at DESC
            LIMIT 1
            """,
            (revision_id, reviewer),
        ).fetchone()
        object_row = connection.execute(
            """
            SELECT object_lifecycle_state, source_sync_state, current_revision_id
            FROM knowledge_objects
            WHERE object_id = ?
            """,
            (object_id,),
        ).fetchone()
        search_row = connection.execute(
            """
            SELECT revision_review_state, source_sync_state
            FROM search_documents
            WHERE object_id = ?
            """,
            (object_id,),
        ).fetchone()
        audit_types = [
            str(row["event_type"])
            for row in connection.execute(
                """
                SELECT event_type
                FROM audit_events
                WHERE object_id = ?
                ORDER BY occurred_at ASC, rowid ASC
                """,
                (object_id,),
            ).fetchall()
        ]
    finally:
        connection.close()
    return {
        "revision_review_state": str(revision_row["revision_review_state"] or revision_row["revision_state"]),
        "assignment_state": str(assignment_row["state"]),
        "object_lifecycle_state": str(object_row["object_lifecycle_state"]),
        "object_source_sync_state": str(object_row["source_sync_state"]),
        "current_revision_id": str(object_row["current_revision_id"]),
        "search_revision_review_state": str(search_row["revision_review_state"]),
        "search_source_sync_state": str(search_row["source_sync_state"]),
        "audit_types": audit_types,
        "canonical_exists": (source_root / "knowledge" / "runbooks" / "surface-conformance.md").exists(),
    }


def read_archive_truth(database_path: Path, *, object_id: str, source_root: Path) -> dict[str, object]:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        object_row = connection.execute(
            """
            SELECT canonical_path, object_lifecycle_state, source_sync_state, current_revision_id
            FROM knowledge_objects
            WHERE object_id = ?
            """,
            (object_id,),
        ).fetchone()
        revision_row = connection.execute(
            """
            SELECT normalized_payload_json
            FROM knowledge_revisions
            WHERE revision_id = ?
            """,
            (str(object_row["current_revision_id"]),),
        ).fetchone()
        latest_event = connection.execute(
            """
            SELECT event_type, details_json
            FROM audit_events
            WHERE object_id = ?
            ORDER BY occurred_at DESC, rowid DESC
            LIMIT 1
            """,
            (object_id,),
        ).fetchone()
    finally:
        connection.close()
    archived_path = str(object_row["canonical_path"])
    old_path = "knowledge/runbooks/archive-conformance.md"
    metadata = json.loads(str(revision_row["normalized_payload_json"]))
    return {
        "canonical_path": archived_path,
        "object_lifecycle_state": str(object_row["object_lifecycle_state"]),
        "source_sync_state": str(object_row["source_sync_state"]),
        "old_path_exists": (source_root / old_path).exists(),
        "archived_path_exists": (source_root / archived_path).exists(),
        "revision_status": str(metadata["status"]),
        "revision_canonical_path": str(metadata["canonical_path"]),
        "latest_event_type": str(latest_event["event_type"]),
        "latest_event_details": json.loads(str(latest_event["details_json"]) or "{}"),
    }


class SurfaceConformanceTests(unittest.TestCase):
    def _seed_pending_mutation(self, temp_dir: str) -> tuple[Path, Path, Path]:
        database_path = Path(temp_dir) / "runtime.db"
        source_root = Path(temp_dir) / "repo"
        build_search_projection(database_path)
        target_path = source_root / "knowledge" / "runbooks" / "startup-recovery.md"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text("before\n", encoding="utf-8")
        authority = PolicyAuthority.from_repository_policy()
        with TransactionalMutation(
            source_root=source_root,
            mutation_id="mutation-surface-startup-recovery",
            mutation_type="source_sync_apply",
            object_id="kb-surface-startup-recovery",
            authority=authority,
        ) as mutation:
            mutation.stage_write(
                target_path=target_path,
                previous_text="before\n",
                new_text="after\n",
            )
            mutation.apply_files()
        self.assertEqual(target_path.read_text(encoding="utf-8"), "after\n")
        return database_path, source_root, target_path

    def _seed_candidate(self, temp_dir: str, *, submitted: bool) -> tuple[Path, Path, str, str]:
        database_path = Path(temp_dir) / "runtime.db"
        source_root = Path(temp_dir) / "repo"
        workflow = GovernanceWorkflow(database_path, source_root=source_root)
        created = workflow.create_object(
            object_id="kb-surface-conformance",
            object_type="runbook",
            title="Surface Conformance",
            summary="Cross-surface review flow test.",
            owner="workflow_owner",
            team="IT Operations",
            canonical_path="knowledge/runbooks/surface-conformance.md",
            actor="surface.setup",
        )
        revision = workflow.create_revision(
            object_id=created.object_id,
            normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
            body_markdown="## Use When\n\nExercise the same review truth across surfaces.\n",
            actor="surface.author",
            change_summary="Surface conformance revision.",
        )
        if submitted:
            workflow.submit_for_review(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                actor="surface.submit",
            )
        return database_path, source_root, created.object_id, revision.revision_id

    def _run_cli(self, argv: list[str]) -> str:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(sys, "argv", argv), redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = operator_main()
        self.assertEqual(exit_code, 0, msg=stderr.getvalue())
        return stdout.getvalue().strip()

    def _exercise_cli(self) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id, revision_id = self._seed_candidate(temp_dir, submitted=True)
            reviewer = "reviewer_cli"
            common = [
                "--db",
                str(database_path),
                "--source-root",
                str(source_root),
                "--allow-noncanonical-source-root",
                "--format",
                "json",
            ]
            self._run_cli(
                [
                    "papyrus-operator",
                    "assign-reviewer",
                    *common,
                    "--object",
                    object_id,
                    "--revision",
                    revision_id,
                    "--reviewer",
                    reviewer,
                    "--actor",
                    "cli.assign",
                ]
            )
            self._run_cli(
                [
                    "papyrus-operator",
                    "approve-review",
                    *common,
                    "--object",
                    object_id,
                    "--revision",
                    revision_id,
                    "--reviewer",
                    reviewer,
                    "--actor",
                    "cli.approve",
                ]
            )
            return read_truth(database_path, object_id=object_id, revision_id=revision_id, reviewer=reviewer, source_root=source_root)

    def _exercise_api(self) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id, revision_id = self._seed_candidate(temp_dir, submitted=True)
            reviewer = "reviewer_api"
            application = api_app(database_path, source_root, allow_noncanonical_source_root=True)
            status, _, _ = call_wsgi(
                application,
                "/reviews/assign",
                method="POST",
                json_payload={
                    "actor": "api.assign",
                    "object_id": object_id,
                    "revision_id": revision_id,
                    "reviewer": reviewer,
                },
            )
            self.assertEqual(status, "200 OK")
            status, _, _ = call_wsgi(
                application,
                "/reviews/approve",
                method="POST",
                json_payload={
                    "actor": "api.approve",
                    "object_id": object_id,
                    "revision_id": revision_id,
                    "reviewer": reviewer,
                },
            )
            self.assertEqual(status, "200 OK")
            return read_truth(database_path, object_id=object_id, revision_id=revision_id, reviewer=reviewer, source_root=source_root)

    def _exercise_web(self) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id, revision_id = self._seed_candidate(temp_dir, submitted=True)
            reviewer = "reviewer_web"
            application = web_app(database_path, source_root, allow_noncanonical_source_root=True)
            status, _, _ = call_wsgi(
                application,
                f"/manage/reviews/{object_id}/{revision_id}/assign",
                method="POST",
                form={"reviewer": reviewer, "notes": "", "due_at": ""},
            )
            self.assertIn(status, {"302 Found", "303 See Other"})
            status, _, _ = call_wsgi(
                application,
                f"/manage/reviews/{object_id}/{revision_id}",
                method="POST",
                form={"reviewer": reviewer, "notes": "", "decision": "approve"},
            )
            self.assertIn(status, {"302 Found", "303 See Other"})
            return read_truth(database_path, object_id=object_id, revision_id=revision_id, reviewer=reviewer, source_root=source_root)

    def _seed_archivable_candidate(self, temp_dir: str) -> tuple[Path, Path, str]:
        database_path = Path(temp_dir) / "runtime.db"
        source_root = Path(temp_dir) / "repo"
        workflow = GovernanceWorkflow(database_path, source_root=source_root)
        archived = workflow.create_object(
            object_id="kb-archive-conformance",
            object_type="runbook",
            title="Archive Conformance",
            summary="Cross-surface archive test.",
            owner="workflow_owner",
            team="IT Operations",
            canonical_path="knowledge/runbooks/archive-conformance.md",
            actor="surface.setup",
        )
        replacement = workflow.create_object(
            object_id="kb-archive-replacement",
            object_type="runbook",
            title="Archive Replacement",
            summary="Replacement object for archive test.",
            owner="workflow_owner",
            team="IT Operations",
            canonical_path="knowledge/runbooks/archive-replacement.md",
            actor="surface.setup",
        )
        revision = workflow.create_revision(
            object_id=archived.object_id,
            normalized_payload=runbook_payload(archived.object_id, archived.canonical_path, archived.title),
            body_markdown="## Use When\n\nArchive the same object across every surface.\n",
            actor="surface.author",
            change_summary="Archive conformance revision.",
        )
        workflow.submit_for_review(object_id=archived.object_id, revision_id=revision.revision_id, actor="surface.submit")
        workflow.assign_reviewer(
            object_id=archived.object_id,
            revision_id=revision.revision_id,
            reviewer="reviewer_archive",
            actor="surface.assign",
        )
        workflow.approve_revision(
            object_id=archived.object_id,
            revision_id=revision.revision_id,
            reviewer="reviewer_archive",
            actor="surface.approve",
            notes="Approve before archive.",
        )
        workflow.supersede_object(
            object_id=archived.object_id,
            replacement_object_id=replacement.object_id,
            actor="surface.supersede",
            notes="Deprecate before archive.",
        )
        return database_path, source_root, archived.object_id

    def _exercise_cli_archive(self) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id = self._seed_archivable_candidate(temp_dir)
            self._run_cli(
                [
                    "papyrus-operator",
                    "archive-object",
                    "--db",
                    str(database_path),
                    "--source-root",
                    str(source_root),
                    "--allow-noncanonical-source-root",
                    "--format",
                    "json",
                    "--object",
                    object_id,
                    "--retirement-reason",
                    "Retired through CLI archive conformance test.",
                    "--ack",
                    "canonical_path_will_move_to_archive",
                    "--actor",
                    "cli.archive",
                ]
            )
            return read_archive_truth(database_path, object_id=object_id, source_root=source_root)

    def _exercise_api_archive(self) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id = self._seed_archivable_candidate(temp_dir)
            application = api_app(database_path, source_root, allow_noncanonical_source_root=True)
            status, _, _ = call_wsgi(
                application,
                f"/objects/{object_id}/archive",
                method="POST",
                json_payload={
                    "actor": "api.archive",
                    "retirement_reason": "Retired through API archive conformance test.",
                    "acknowledgements": ["canonical_path_will_move_to_archive"],
                },
            )
            self.assertEqual(status, "200 OK")
            return read_archive_truth(database_path, object_id=object_id, source_root=source_root)

    def _exercise_web_archive(self) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id = self._seed_archivable_candidate(temp_dir)
            application = web_app(database_path, source_root, allow_noncanonical_source_root=True)
            status, _, _ = call_wsgi(
                application,
                f"/manage/objects/{object_id}/archive",
                method="POST",
                form={
                    "retirement_reason": "Retired through web archive conformance test.",
                    "notes": "",
                    "acknowledgements": ["canonical_path_will_move_to_archive"],
                },
            )
            self.assertIn(status, {"302 Found", "303 See Other"})
            return read_archive_truth(database_path, object_id=object_id, source_root=source_root)

    def test_review_matrix_matches_expected_truth_across_cli_api_and_web(self) -> None:
        expected_audit_types = [
            "object_created",
            "revision_created",
            "revision_submitted_for_review",
            "reviewer_assigned",
            "source_writeback",
            "revision_approved",
        ]
        expected = {
            "revision_review_state": "approved",
            "assignment_state": "approved",
            "object_lifecycle_state": "active",
            "object_source_sync_state": "applied",
            "current_revision_id": "kb-surface-conformance-rev-",  # prefix checked below
            "search_revision_review_state": "approved",
            "search_source_sync_state": "applied",
            "canonical_exists": True,
        }
        for result in (self._exercise_cli(), self._exercise_api(), self._exercise_web()):
            self.assertEqual(result["revision_review_state"], expected["revision_review_state"])
            self.assertEqual(result["assignment_state"], expected["assignment_state"])
            self.assertEqual(result["object_lifecycle_state"], expected["object_lifecycle_state"])
            self.assertEqual(result["object_source_sync_state"], expected["object_source_sync_state"])
            self.assertTrue(str(result["current_revision_id"]).startswith(expected["current_revision_id"]))
            self.assertEqual(result["search_revision_review_state"], expected["search_revision_review_state"])
            self.assertEqual(result["search_source_sync_state"], expected["search_source_sync_state"])
            self.assertEqual(result["audit_types"], expected_audit_types)
            self.assertTrue(result["canonical_exists"])

    def test_archive_matrix_matches_expected_truth_across_cli_api_and_web(self) -> None:
        expected_path = "archive/knowledge/runbooks/archive-conformance.md"
        for result in (self._exercise_cli_archive(), self._exercise_api_archive(), self._exercise_web_archive()):
            self.assertEqual(result["canonical_path"], expected_path)
            self.assertEqual(result["object_lifecycle_state"], "archived")
            self.assertEqual(result["source_sync_state"], "applied")
            self.assertFalse(result["old_path_exists"])
            self.assertTrue(result["archived_path_exists"])
            self.assertEqual(result["revision_status"], "archived")
            self.assertEqual(result["revision_canonical_path"], expected_path)
            self.assertEqual(result["latest_event_type"], "object_archived")
            self.assertEqual(
                result["latest_event_details"]["required_acknowledgements"],
                ["canonical_path_will_move_to_archive"],
            )
            self.assertEqual(
                result["latest_event_details"]["acknowledgements"],
                ["canonical_path_will_move_to_archive"],
            )
            self.assertEqual(result["latest_event_details"]["transition"]["to_state"], "archived")
            self.assertIn("policy_decision", result["latest_event_details"])

    def test_startup_recovery_runs_before_cli_api_and_web_surface_access(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, target_path = self._seed_pending_mutation(temp_dir)
            self._run_cli(
                [
                    "papyrus-operator",
                    "queue",
                    "--db",
                    str(database_path),
                    "--source-root",
                    str(source_root),
                    "--allow-noncanonical-source-root",
                    "--format",
                    "json",
                ]
            )
            self.assertEqual(target_path.read_text(encoding="utf-8"), "before\n")

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, target_path = self._seed_pending_mutation(temp_dir)
            api_app(database_path, source_root, allow_noncanonical_source_root=True)
            self.assertEqual(target_path.read_text(encoding="utf-8"), "before\n")

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, target_path = self._seed_pending_mutation(temp_dir)
            web_app(database_path, source_root, allow_noncanonical_source_root=True)
            self.assertEqual(target_path.read_text(encoding="utf-8"), "before\n")
