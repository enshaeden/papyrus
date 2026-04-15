from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class CliWorkflowTests(unittest.TestCase):
    def test_build_route_map_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            json_output = Path(temp_dir) / "route-map.json"
            markdown_output = Path(temp_dir) / "route-map.md"
            result = run_command(
                "scripts/build_route_map.py",
                "--json-output",
                str(json_output),
                "--markdown-output",
                str(markdown_output),
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(json_output.exists())
            self.assertTrue(markdown_output.exists())
            self.assertIn("/operator/read", json_output.read_text(encoding="utf-8"))
            self.assertIn("Route Map", markdown_output.read_text(encoding="utf-8"))

            check_result = run_command(
                "scripts/build_route_map.py",
                "--check",
                "--json-output",
                str(json_output),
                "--markdown-output",
                str(markdown_output),
            )
            self.assertEqual(
                check_result.returncode, 0, msg=check_result.stdout + check_result.stderr
            )

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

    def test_list_object_types_cli(self) -> None:
        result = run_command("scripts/new_article.py", "--list-object-types")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[object_types]", result.stdout)
        self.assertIn("service_record", result.stdout)

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
        self.assertIn("kb-runbooks-laptop-provisioning", result.stdout)

    def test_content_health_report_docs_warning_section(self) -> None:
        result = run_command("scripts/report_content_health.py", "--section", "knowledge-like-docs")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[knowledge-like-docs]", result.stdout)

    def test_content_health_report_usefulness_sections(self) -> None:
        build_result = run_command("scripts/build_index.py")
        self.assertEqual(build_result.returncode, 0, msg=build_result.stderr)
        result = run_command(
            "scripts/report_content_health.py",
            "--section",
            "placeholder-heavy",
            "--section",
            "weak-evidence",
            "--section",
            "migration-gaps",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[placeholder-heavy]", result.stdout)
        self.assertIn("[weak-evidence]", result.stdout)
        self.assertIn("[migration-gaps]", result.stdout)
        self.assertIn(
            "kb-applications-access-and-license-management-add-productivity-platform-licenses",
            result.stdout,
        )
        self.assertIn(
            "kb-troubleshooting-audio-video-boardrooms-standard-av-room-user-guide",
            result.stdout,
        )

    def test_retired_import_shim_returns_deterministic_message(self) -> None:
        result = run_command("scripts/import_knowledge_portal.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("retired and unsupported", result.stderr)
        self.assertIn("decisions/index.md", result.stderr)
        self.assertIn("docs/migration/seed-migration-rationale.md", result.stderr)
        self.assertIn("scripts/validate_migration.py", result.stderr)

    def test_validate_migration_cli(self) -> None:
        result = run_command("scripts/validate_migration.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("migration validation passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
