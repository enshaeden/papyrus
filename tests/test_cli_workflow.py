from __future__ import annotations

import copy
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree, which


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.application.sync_flow import build_search_projection
from papyrus.infrastructure.markdown.parser import parse_knowledge_document


def mkdocs_available() -> bool:
    return (ROOT / ".venv" / "bin" / "mkdocs").exists() or which("mkdocs") is not None


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class CliWorkflowTests(unittest.TestCase):
    def test_build_site_docs_cli(self) -> None:
        build_index = run_command("scripts/build_index.py")
        self.assertEqual(build_index.returncode, 0, msg=build_index.stderr)
        result = run_command("scripts/build_site_docs.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        generated_home = ROOT / "generated" / "site_docs" / "index.md"
        generated_index = ROOT / "generated" / "site_docs" / "knowledge" / "index.md"
        generated_docs_index = ROOT / "generated" / "site_docs" / "system-design-docs" / "index.md"
        generated_explorer = ROOT / "generated" / "site_docs" / "knowledge" / "explorer.md"
        generated_ticket_guide = (
            ROOT
            / "generated"
            / "site_docs"
            / "knowledge"
            / "user-lifecycle"
            / "job-and-org-change"
            / "job-and-org-change-ticket-review-guide.md"
        )
        generated_license_guide = (
            ROOT
            / "generated"
            / "site_docs"
            / "knowledge"
            / "applications"
            / "access-and-license-management"
            / "add-productivity-platform-licenses.md"
        )
        self.assertTrue(generated_home.exists())
        self.assertTrue(generated_index.exists())
        self.assertTrue(generated_docs_index.exists())
        self.assertTrue(generated_explorer.exists())
        self.assertTrue(generated_ticket_guide.exists())
        self.assertTrue(generated_license_guide.exists())
        generated_home_text = generated_home.read_text(encoding="utf-8")
        generated_explorer_text = generated_explorer.read_text(encoding="utf-8")
        generated_ticket_guide_text = generated_ticket_guide.read_text(encoding="utf-8")
        generated_license_guide_text = generated_license_guide.read_text(encoding="utf-8")
        self.assertIn("approved-content export", generated_home_text)
        self.assertIn('href="knowledge/"', generated_home_text)
        self.assertNotIn('href="knowledge/index.md"', generated_home_text)
        self.assertIn("System & Design Docs", generated_docs_index.read_text(encoding="utf-8"))
        self.assertIn("Knowledge Explorer", generated_explorer_text)
        site_paths = re.findall(r'"site_path": "([^"]+)"', generated_explorer_text)
        self.assertTrue(site_paths)
        self.assertTrue(all(not path.endswith(".md") for path in site_paths))
        self.assertNotIn("](<INTERNAL_URL>)", generated_ticket_guide_text)
        self.assertIn("Job and Org Change", generated_ticket_guide_text)
        self.assertNotIn("](<INTERNAL_URL>)", generated_license_guide_text)
        self.assertNotIn("](<SUPPLIER_PORTAL_URL>)", generated_license_guide_text)

    def test_build_site_docs_cli_exports_only_runtime_approved_objects(self) -> None:
        generated_vpn_guide = (
            ROOT
            / "generated"
            / "site_docs"
            / "knowledge"
            / "troubleshooting"
            / "vpn-connectivity.md"
        )
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                database_path = Path(temp_dir) / "workflow.db"
                build_search_projection(database_path)
                workflow = GovernanceWorkflow(database_path)

                document = parse_knowledge_document(
                    ROOT / "knowledge" / "troubleshooting" / "vpn-connectivity.md"
                )
                payload = copy.deepcopy(document.metadata)
                payload["summary"] = "Draft export suppression test for VPN troubleshooting."
                payload["change_log"] = [
                    *payload["change_log"],
                    {"date": "2026-04-07", "summary": "Draft export suppression test.", "author": "tests"},
                ]
                workflow.create_revision(
                    object_id=payload["id"],
                    normalized_payload=payload,
                    body_markdown=f"{document.body}\n\nDraft export suppression test note.",
                    actor="tests",
                    legacy_metadata=document.metadata,
                    change_summary="Draft export suppression test.",
                )

                result = run_command("scripts/build_site_docs.py", "--db", str(database_path))
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                self.assertFalse(generated_vpn_guide.exists())
        finally:
            rebuild_index = run_command("scripts/build_index.py")
            self.assertEqual(rebuild_index.returncode, 0, msg=rebuild_index.stderr)
            restore = run_command("scripts/build_site_docs.py")
            self.assertEqual(restore.returncode, 0, msg=restore.stderr)

    def test_new_article_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            copytree(ROOT / "taxonomies", temp_root / "taxonomies")
            copytree(ROOT / "schemas", temp_root / "schemas")
            copytree(ROOT / "templates", temp_root / "templates")
            (temp_root / "knowledge" / "runbooks").mkdir(parents=True)
            result = run_command(
                "scripts/new_article.py",
                "--root",
                str(temp_root),
                "--type",
                "runbook",
                "--title",
                "Temporary Example Procedure",
                "--service",
                "Remote Access",
                "--system",
                "<VPN_SERVICE>",
                "--tag",
                "vpn",
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            created_path = temp_root / result.stdout.strip()
            self.assertTrue(created_path.exists())
            created_text = created_path.read_text(encoding="utf-8")
            self.assertIn("Temporary Example Procedure", created_text)
            self.assertIn("knowledge_object_type: runbook", created_text)
            self.assertIn("canonical_path:", created_text)
            self.assertIn("related_services:\n- Remote Access", created_text)
            self.assertIn("services:\n- Remote Access", created_text)
            self.assertIn("systems:\n- <VPN_SERVICE>", created_text)
            self.assertIn("tags:\n- vpn", created_text)

    def test_list_taxonomy_cli(self) -> None:
        result = run_command("scripts/new_article.py", "--list-taxonomy", "services")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[services]", result.stdout)
        self.assertIn("Remote Access", result.stdout)

    def test_validate_cli(self) -> None:
        result = run_command("scripts/validate.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("validated", result.stdout)

    def test_build_sh_builds_runtime_without_static_export(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/build.sh"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("validated", result.stdout)
        self.assertIn("knowledge.db", result.stdout)

    @unittest.skipUnless(mkdocs_available(), "mkdocs not installed")
    def test_build_static_export_sh_runs_rendered_site_validation(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/build_static_export.sh"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("validated", result.stdout)

    def test_build_index_and_search_cli(self) -> None:
        build_result = run_command("scripts/build_index.py")
        self.assertEqual(build_result.returncode, 0, msg=build_result.stderr)
        self.assertIn("knowledge.db", build_result.stdout)
        connection = sqlite3.connect(ROOT / "build" / "knowledge.db")
        connection.row_factory = sqlite3.Row
        try:
            table_names = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
                ).fetchall()
            }
            citation_statuses = {
                row["validity_status"]: row["item_count"]
                for row in connection.execute(
                    "SELECT validity_status, COUNT(*) AS item_count FROM citations GROUP BY validity_status"
                ).fetchall()
            }
            citation_validation_row = connection.execute(
                "SELECT run_type, status FROM validation_runs WHERE run_type = 'citation_scan' ORDER BY completed_at DESC LIMIT 1"
            ).fetchone()
            after_change_row = connection.execute(
                """
                SELECT freshness_rank
                FROM search_documents
                WHERE object_id = 'kb-applications-access-and-license-management-add-productivity-platform-licenses'
                """
            ).fetchone()
        finally:
            connection.close()
        self.assertIn("knowledge_objects", table_names)
        self.assertIn("knowledge_revisions", table_names)
        self.assertIn("citations", table_names)
        self.assertIn("services", table_names)
        self.assertIn("relationships", table_names)
        self.assertIn("review_assignments", table_names)
        self.assertIn("validation_runs", table_names)
        self.assertIn("audit_events", table_names)
        self.assertIn("search_documents", table_names)
        self.assertNotIn("articles", table_names)
        self.assertIn("unverified", citation_statuses)
        self.assertIn("verified", citation_statuses)
        self.assertIsNotNone(citation_validation_row)
        self.assertEqual(citation_validation_row["run_type"], "citation_scan")
        self.assertEqual(after_change_row["freshness_rank"], 0)

        search_result = run_command("scripts/search.py", "vpn")
        self.assertEqual(search_result.returncode, 0, msg=search_result.stderr)
        self.assertIn("VPN Troubleshooting", search_result.stdout)

    def test_stale_report_for_seed_date(self) -> None:
        result = run_command("scripts/report_stale.py", "--as-of", "2026-04-07")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("no stale knowledge objects found", result.stdout)

    def test_content_health_report_cli(self) -> None:
        result = run_command("scripts/report_content_health.py", "--section", "duplicates")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[duplicates]", result.stdout)

    def test_content_health_report_citation_section(self) -> None:
        run_command("scripts/build_index.py")
        result = run_command("scripts/report_content_health.py", "--section", "citation-health")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[citation-health]", result.stdout)
        self.assertIn("kb-applications-access-and-license-management-add-productivity-platform-licenses", result.stdout)

    def test_content_health_report_docs_warning_section(self) -> None:
        result = run_command("scripts/report_content_health.py", "--section", "knowledge-like-docs")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[knowledge-like-docs]", result.stdout)

    def test_validate_migration_cli(self) -> None:
        result = run_command("scripts/validate_migration.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("migration validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
