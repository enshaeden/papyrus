from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree, ignore_patterns

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def run_command(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def copy_repo_for_cli(destination: Path) -> Path:
    target = destination / "repo"
    copytree(
        ROOT,
        target,
        ignore=ignore_patterns(".git", ".venv", "__pycache__", "site", "site_docs"),
    )
    return target


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
            self.assertIn("/read", json_output.read_text(encoding="utf-8"))
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

    def test_new_object_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            result = run_command(
                "scripts/new_object.py",
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

    def test_list_object_types_cli_with_external_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_command(
                "scripts/new_object.py",
                "--root",
                temp_dir,
                "--list-object-types",
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("[object_types]", result.stdout)
            self.assertIn("service_record", result.stdout)

    def test_list_taxonomy_cli(self) -> None:
        result = run_command("scripts/new_object.py", "--list-taxonomy", "services")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[services]", result.stdout)
        self.assertIn("Remote Access", result.stdout)

    def test_list_object_types_cli(self) -> None:
        result = run_command("scripts/new_object.py", "--list-object-types")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[object_types]", result.stdout)
        self.assertIn("service_record", result.stdout)

    def test_validate_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            result = run_command("scripts/validate.py", cwd=repo_root)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("validated", result.stdout)

    def test_build_sh_validates_repo_contract_without_source_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            result = subprocess.run(
                ["bash", "scripts/build.sh"],
                cwd=repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("validated repo contract", result.stdout)

    def test_build_sh_builds_runtime_with_explicit_source_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            result = subprocess.run(
                [
                    "bash",
                    "scripts/build.sh",
                    "--source-root",
                    str(repo_root / "tests" / "fixtures" / "source_workspace"),
                ],
                cwd=repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("validated repo contract and", result.stdout)
            self.assertIn("knowledge.db", result.stdout)

    def test_build_index_cli_requires_explicit_source_root(self) -> None:
        result = run_command("scripts/build_index.py")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--source-root", result.stderr)

    def test_build_index_and_search_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            source_root = repo_root / "tests" / "fixtures" / "source_workspace"
            build_result = run_command(
                "scripts/build_index.py",
                "--source-root",
                str(source_root),
                cwd=repo_root,
            )
            self.assertEqual(build_result.returncode, 0, msg=build_result.stderr)
            self.assertIn("knowledge.db", build_result.stdout)
            connection = sqlite3.connect(repo_root / "build" / "knowledge.db")
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

            search_result = run_command("scripts/search.py", "vpn", cwd=repo_root)
            self.assertEqual(search_result.returncode, 0, msg=search_result.stderr)
            self.assertIn("VPN Troubleshooting", search_result.stdout)

    def test_stale_report_for_seed_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            result = run_command(
                "scripts/report_stale.py",
                "--as-of",
                "2026-04-07",
                "--source-root",
                str(repo_root / "tests" / "fixtures" / "source_workspace"),
                cwd=repo_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("no stale knowledge objects found", result.stdout)

    def test_content_health_report_cli(self) -> None:
        result = run_command("scripts/report_content_health.py", "--section", "duplicates")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[duplicates]", result.stdout)

    def test_content_health_report_citation_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            source_root = repo_root / "tests" / "fixtures" / "source_workspace"
            run_command(
                "scripts/build_index.py",
                "--source-root",
                str(source_root),
                cwd=repo_root,
            )
            result = run_command(
                "scripts/report_content_health.py",
                "--section",
                "citation-health",
                cwd=repo_root,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("[citation-health]", result.stdout)
            self.assertIn("kb-runbooks-laptop-provisioning", result.stdout)

    def test_content_health_report_docs_warning_section(self) -> None:
        result = run_command("scripts/report_content_health.py", "--section", "knowledge-like-docs")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[knowledge-like-docs]", result.stdout)

    def test_content_health_report_usefulness_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = copy_repo_for_cli(Path(temp_dir))
            source_root = repo_root / "tests" / "fixtures" / "source_workspace"
            build_result = run_command(
                "scripts/build_index.py",
                "--source-root",
                str(source_root),
                cwd=repo_root,
            )
            self.assertEqual(build_result.returncode, 0, msg=build_result.stderr)
            result = run_command(
                "scripts/report_content_health.py",
                "--source-root",
                str(source_root),
                "--section",
                "placeholder-heavy",
                "--section",
                "weak-evidence",
                "--section",
                "migration-gaps",
                cwd=repo_root,
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

    def test_retired_migration_scripts_are_removed(self) -> None:
        self.assertFalse((ROOT / "scripts" / "import_knowledge_portal.py").exists())
        self.assertFalse((ROOT / "scripts" / "validate_migration.py").exists())


if __name__ == "__main__":
    unittest.main()
