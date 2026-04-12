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
from papyrus.application.commands import archive_object_command
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.cli import operator_main
from papyrus.interfaces.web import app as web_app
from papyrus.interfaces.web.presenters.governed_presenter import action_href
from papyrus.infrastructure.transactional_mutation import TransactionalMutation
from papyrus.application.writeback_flow import restore_last_writeback
from tests.web_assertions import SemanticHookAssertions


def humanize_token(token: str) -> str:
    return token.replace("_", " ").strip()


def action_by_id(actions: list[dict[str, object]], action_id: str) -> dict[str, object]:
    for action in actions:
        if str(action.get("action_id") or "") == action_id:
            return action
    raise AssertionError(f"action not found: {action_id}")


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
        status_holder["object_lifecycle_state"] = status
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
    return str(status_holder["object_lifecycle_state"]), dict(status_holder["headers"]), body


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Surface conformance for {title.lower()}",
        "knowledge_object_type": "runbook",
        "legacy_article_type": None,
        "object_lifecycle_state": "active",
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
                "source_ref": "docs/migration/seed-migration-rationale.md",
                "note": "Surface conformance evidence.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "related_articles": [],
        "references": [{"title": "Seed import manifest", "path": "docs/migration/seed-migration-rationale.md"}],
        "change_log": [{"date": "2026-04-09", "summary": "Surface conformance draft.", "author": "tests"}],
    }


def read_truth(database_path: Path, *, object_id: str, revision_id: str, reviewer: str, source_root: Path) -> dict[str, object]:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        revision_row = connection.execute(
            """
            SELECT revision_review_state
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
        "revision_review_state": str(revision_row["revision_review_state"]),
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
        "revision_status": str(metadata["object_lifecycle_state"]),
        "revision_canonical_path": str(metadata["canonical_path"]),
        "latest_event_type": str(latest_event["event_type"]),
        "latest_event_details": json.loads(str(latest_event["details_json"]) or "{}"),
    }


class SurfaceConformanceTests(SemanticHookAssertions, unittest.TestCase):
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

    def _run_cli_json(self, argv: list[str]) -> dict[str, object]:
        return json.loads(self._run_cli(argv))

    def _seed_approved_object(
        self,
        temp_dir: str,
        *,
        object_id: str,
        title: str,
        canonical_path: str,
    ) -> tuple[Path, Path, str, str]:
        database_path = Path(temp_dir) / "runtime.db"
        source_root = Path(temp_dir) / "repo"
        workflow = GovernanceWorkflow(database_path, source_root=source_root)
        created = workflow.create_object(
            object_id=object_id,
            object_type="runbook",
            title=title,
            summary=f"{title} cross-surface state coverage.",
            owner="workflow_owner",
            team="IT Operations",
            canonical_path=canonical_path,
            actor="surface.setup",
        )
        revision = workflow.create_revision(
            object_id=created.object_id,
            normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
            body_markdown=f"## Use When\n\nExercise {title.lower()} state rendering across surfaces.\n",
            actor="surface.author",
            change_summary=f"{title} seed revision.",
        )
        workflow.submit_for_review(
            object_id=created.object_id,
            revision_id=revision.revision_id,
            actor="surface.submit",
        )
        workflow.assign_reviewer(
            object_id=created.object_id,
            revision_id=revision.revision_id,
            reviewer="reviewer_state",
            actor="surface.assign",
        )
        workflow.approve_revision(
            object_id=created.object_id,
            revision_id=revision.revision_id,
            reviewer="reviewer_state",
            actor="local.reviewer",
            notes=f"Approve {title.lower()} seed revision.",
        )
        return database_path, source_root, created.object_id, revision.revision_id

    def _seed_writeback_preview_candidate(
        self,
        temp_dir: str,
        *,
        conflict: bool,
    ) -> tuple[Path, Path, str, str]:
        database_path, source_root, object_id, _ = self._seed_approved_object(
            temp_dir,
            object_id="kb-surface-preview",
            title="Surface Preview",
            canonical_path="knowledge/runbooks/surface-preview.md",
        )
        workflow = GovernanceWorkflow(database_path, source_root=source_root)
        updated_payload = runbook_payload(
            object_id,
            "knowledge/runbooks/surface-preview.md",
            "Surface Preview",
        )
        updated_payload["summary"] = "Surface preview conflict coverage."
        revision = workflow.create_revision(
            object_id=object_id,
            normalized_payload=updated_payload,
            body_markdown="## Use When\n\nExercise conflicting writeback preview rendering.\n",
            actor="surface.author",
            change_summary="Surface preview revision.",
        )
        workflow.submit_for_review(
            object_id=object_id,
            revision_id=revision.revision_id,
            actor="surface.submit",
        )
        workflow.assign_reviewer(
            object_id=object_id,
            revision_id=revision.revision_id,
            reviewer="reviewer_preview",
            actor="surface.assign",
        )
        if conflict:
            target_path = source_root / "knowledge" / "runbooks" / "surface-preview.md"
            target_path.write_text("manual conflict\n", encoding="utf-8")
        return database_path, source_root, object_id, revision.revision_id

    def _seed_restored_object(self, temp_dir: str) -> tuple[Path, Path, str]:
        database_path, source_root, object_id, _ = self._seed_approved_object(
            temp_dir,
            object_id="kb-surface-restored",
            title="Surface Restored",
            canonical_path="knowledge/runbooks/surface-restored.md",
        )
        workflow = GovernanceWorkflow(database_path, source_root=source_root)
        second_payload = runbook_payload(
            object_id,
            "knowledge/runbooks/surface-restored.md",
            "Surface Restored",
        )
        second_payload["summary"] = "Surface restored coverage."
        second_revision = workflow.create_revision(
            object_id=object_id,
            normalized_payload=second_payload,
            body_markdown="## Use When\n\nExercise restored state rendering.\n",
            actor="surface.author",
            change_summary="Surface restored revision.",
        )
        workflow.submit_for_review(
            object_id=object_id,
            revision_id=second_revision.revision_id,
            actor="surface.submit",
        )
        workflow.assign_reviewer(
            object_id=object_id,
            revision_id=second_revision.revision_id,
            reviewer="reviewer_state",
            actor="surface.assign",
        )
        workflow.approve_revision(
            object_id=object_id,
            revision_id=second_revision.revision_id,
            reviewer="reviewer_state",
            actor="local.reviewer",
            notes="Approve restored state revision.",
        )
        restore_last_writeback(
            database_path=database_path,
            object_id=object_id,
            actor="local.manager",
            root_path=source_root,
            acknowledgements=["restore_can_remove_current_canonical_text"],
        )
        return database_path, source_root, object_id

    def _seed_archived_object(self, temp_dir: str) -> tuple[Path, Path, str]:
        database_path, source_root, object_id = self._seed_archivable_candidate(temp_dir)
        archive_object_command(
            database_path=database_path,
            source_root=source_root,
            object_id=object_id,
            actor="surface.archive",
            retirement_reason="Archive surface rendering conformance test.",
            acknowledgements=["canonical_path_will_move_to_archive"],
        )
        return database_path, source_root, object_id

    def _cli_common(self, *, database_path: Path, source_root: Path) -> list[str]:
        return [
            "--db",
            str(database_path),
            "--source-root",
            str(source_root),
            "--allow-noncanonical-source-root",
            "--format",
            "json",
        ]

    def _fetch_object_surfaces(
        self,
        *,
        database_path: Path,
        source_root: Path,
        object_id: str,
    ) -> tuple[dict[str, object], dict[str, object], str]:
        cli_payload = self._run_cli_json(
            [
                "papyrus-operator",
                "object",
                *self._cli_common(database_path=database_path, source_root=source_root),
                object_id,
            ]
        )
        status, _, api_body = call_wsgi(
            api_app(database_path, source_root, allow_noncanonical_source_root=True),
            f"/objects/{object_id}",
        )
        self.assertEqual(status, "200 OK")
        status, _, web_body = call_wsgi(
            web_app(database_path, source_root, allow_noncanonical_source_root=True),
            f"/objects/{object_id}",
        )
        self.assertEqual(status, "200 OK")
        return cli_payload, json.loads(api_body), web_body

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
        results = [self._exercise_cli_archive(), self._exercise_api_archive(), self._exercise_web_archive()]
        for result in results:
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
            self.assertIn("operator_message", result["latest_event_details"])
        self.assertEqual(
            {
                json.dumps(result["latest_event_details"]["transition"], sort_keys=True)
                for result in results
            },
            {
                json.dumps(results[0]["latest_event_details"]["transition"], sort_keys=True)
            },
        )
        self.assertEqual(
            {str(result["latest_event_details"]["operator_message"]) for result in results},
            {str(results[0]["latest_event_details"]["operator_message"])},
        )

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

    def test_object_action_contracts_match_across_cli_api_and_web(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id, revision_id = self._seed_candidate(temp_dir, submitted=True)
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            workflow.assign_reviewer(
                object_id=object_id,
                revision_id=revision_id,
                reviewer="reviewer_surface",
                actor="surface.assign",
            )
            cli_payload, api_payload, web_body = self._fetch_object_surfaces(
                database_path=database_path,
                source_root=source_root,
                object_id=object_id,
            )
            self.assertEqual(cli_payload["ui_projection"], api_payload["ui_projection"])
            self.assert_page_contract(web_body, primary_surface="object-detail", components=("action-cluster",))
            self.assert_surface(web_body, "posture")
            for action in cli_payload["ui_projection"]["actions"]:
                if str(action.get("availability") or "") != "allowed":
                    continue
                action_id = str(action.get("action_id") or "")
                if action_href(action_id=action_id, object_id=object_id, revision_id=revision_id) is None:
                    continue
                self.assert_action_id(web_body, action_id)
            self.assertIn(cli_payload["ui_projection"]["use_guidance"]["summary"], web_body)
            self.assertIn(cli_payload["ui_projection"]["use_guidance"]["detail"], web_body)
            self.assert_component_count(web_body, "action-cluster", 1)

    def test_archive_contract_and_acknowledgement_copy_match_across_cli_api_and_web(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id = self._seed_archivable_candidate(temp_dir)
            cli_payload, api_payload, _ = self._fetch_object_surfaces(
                database_path=database_path,
                source_root=source_root,
                object_id=object_id,
            )
            cli_archive_action = action_by_id(cli_payload["ui_projection"]["actions"], "archive_object")
            api_archive_action = action_by_id(api_payload["ui_projection"]["actions"], "archive_object")
            self.assertEqual(cli_archive_action, api_archive_action)

            status, _, web_body = call_wsgi(
                web_app(database_path, source_root, allow_noncanonical_source_root=True),
                f"/manage/objects/{object_id}/archive",
            )
            self.assertEqual(status, "200 OK")
            self.assertIn(str(cli_archive_action["summary"]), web_body)
            self.assertIn(str(cli_archive_action["detail"]), web_body)
            for token in (cli_archive_action.get("policy") or {}).get("required_acknowledgements") or []:
                self.assertIn(humanize_token(str(token)), web_body)
            self.assertEqual(web_body.count('name="acknowledgements"'), 1)

    def test_writeback_preview_conflict_contract_matches_across_cli_api_and_web(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id, revision_id = self._seed_writeback_preview_candidate(
                temp_dir,
                conflict=True,
            )
            cli_preview = self._run_cli_json(
                [
                    "papyrus-operator",
                    "preview-source-sync",
                    *self._cli_common(database_path=database_path, source_root=source_root),
                    "--object",
                    object_id,
                    "--revision",
                    revision_id,
                ]
            )
            status, _, api_body = call_wsgi(
                api_app(database_path, source_root, allow_noncanonical_source_root=True),
                f"/objects/{object_id}/source-sync/preview",
                method="POST",
                json_payload={"revision_id": revision_id},
            )
            self.assertEqual(status, "200 OK")
            api_preview = json.loads(api_body)
            self.assertEqual(cli_preview, api_preview)
            self.assertTrue(cli_preview["conflict_detected"])
            self.assertEqual(cli_preview["transition"]["to_state"], "conflicted")

            status, _, web_body = call_wsgi(
                web_app(database_path, source_root, allow_noncanonical_source_root=True),
                f"/manage/reviews/{object_id}/{revision_id}",
            )
            self.assertEqual(status, "200 OK")
            self.assertIn(cli_preview["operator_message"], web_body)
            for token in cli_preview["required_acknowledgements"]:
                self.assertIn(humanize_token(str(token)), web_body)
            self.assertEqual(web_body.count("Writeback contract"), 1)
            self.assertEqual(web_body.count("Writeback acknowledgement requirements"), 1)
            self.assertNotIn("ready to become canonical guidance", web_body)

    def test_conflicted_and_restored_object_projection_matches_across_cli_api_and_web(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id, _ = self._seed_approved_object(
                temp_dir,
                object_id="kb-surface-conflicted",
                title="Surface Conflicted",
                canonical_path="knowledge/runbooks/surface-conflicted.md",
            )
            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    "UPDATE knowledge_objects SET source_sync_state = 'conflicted' WHERE object_id = ?",
                    (object_id,),
                )
                connection.commit()
            finally:
                connection.close()
            cli_payload, api_payload, web_body = self._fetch_object_surfaces(
                database_path=database_path,
                source_root=source_root,
                object_id=object_id,
            )
            self.assertEqual(
                cli_payload["ui_projection"]["use_guidance"],
                api_payload["ui_projection"]["use_guidance"],
            )
            self.assertEqual(
                cli_payload["ui_projection"]["use_guidance"]["code"],
                "source_sync_conflicted",
            )
            self.assertIn(cli_payload["ui_projection"]["use_guidance"]["summary"], web_body)
            self.assertIn(cli_payload["ui_projection"]["use_guidance"]["detail"], web_body)
            self.assertNotIn("Safe to use now", web_body)

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id = self._seed_restored_object(temp_dir)
            cli_payload, api_payload, web_body = self._fetch_object_surfaces(
                database_path=database_path,
                source_root=source_root,
                object_id=object_id,
            )
            self.assertEqual(
                cli_payload["ui_projection"]["use_guidance"],
                api_payload["ui_projection"]["use_guidance"],
            )
            self.assertEqual(
                cli_payload["ui_projection"]["use_guidance"]["code"],
                "source_sync_restored",
            )
            self.assertIn(cli_payload["ui_projection"]["use_guidance"]["summary"], web_body)
            self.assertIn(cli_payload["ui_projection"]["use_guidance"]["detail"], web_body)

    def test_archived_object_projection_matches_across_cli_api_and_web(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path, source_root, object_id = self._seed_archived_object(temp_dir)
            cli_payload, api_payload, web_body = self._fetch_object_surfaces(
                database_path=database_path,
                source_root=source_root,
                object_id=object_id,
            )
            self.assertEqual(cli_payload["ui_projection"]["state"], api_payload["ui_projection"]["state"])
            self.assertEqual(
                cli_payload["ui_projection"]["state"]["object_lifecycle_state"],
                "archived",
            )
            self.assert_primary_surface(web_body, "object-detail")
            self.assertIn("archived", web_body)
