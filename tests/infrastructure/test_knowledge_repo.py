from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.sync_flow import build_search_projection  # noqa: E402
from papyrus.infrastructure.repositories.knowledge_repo import (  # noqa: E402
    collect_source_paths,
    load_current_runtime_documents,
    load_policy,
)
from tests.source_workspace import fixture_source_root  # noqa: E402


class KnowledgeRepoTests(unittest.TestCase):
    def test_collect_source_paths_excludes_agents_documents_in_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_root = Path(temp_dir) / "workspace"
            policy = load_policy()
            for root in policy["source_workspace"]["article_roots"]:
                (workspace_root / root).mkdir(parents=True, exist_ok=True)
            (workspace_root / "knowledge" / "AGENTS.md").write_text("ignored", encoding="utf-8")
            document_path = workspace_root / "knowledge" / "runbooks" / "test.md"
            document_path.parent.mkdir(parents=True, exist_ok=True)
            document_path.write_text(
                "---\n"
                "id: kb-test\n"
                "title: Test\n"
                "canonical_path: knowledge/runbooks/test.md\n"
                "summary: Test summary.\n"
                "knowledge_object_type: runbook\n"
                "object_lifecycle_state: active\n"
                "owner: workflow_owner\n"
                "team: IT Operations\n"
                "source_type: native\n"
                "source_system: repository\n"
                "source_title: Test\n"
                "created: 2026-04-08\n"
                "updated: 2026-04-08\n"
                "last_reviewed: 2026-04-08\n"
                "review_cadence: quarterly\n"
                "---\n\n"
                "## Purpose\n\nWorkspace test.\n",
                encoding="utf-8",
            )

            paths = collect_source_paths(workspace_root, policy)

            self.assertEqual(paths, [document_path.resolve()])
            self.assertNotIn(workspace_root / "knowledge" / "AGENTS.md", paths)

    def test_runtime_documents_load_from_database_without_workspace_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                documents = load_current_runtime_documents(connection)
            finally:
                connection.close()

            self.assertTrue(documents, msg="expected runtime documents")
            self.assertTrue(all(document.relative_path for document in documents))
            self.assertTrue(all(not document.source_path.is_absolute() for document in documents))


if __name__ == "__main__":
    unittest.main()
