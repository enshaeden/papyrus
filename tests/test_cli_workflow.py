from __future__ import annotations

import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree, which


ROOT = Path(__file__).resolve().parent.parent


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
        result = run_command("scripts/build_site_docs.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        generated_home = ROOT / "generated" / "site_docs" / "index.md"
        generated_index = ROOT / "generated" / "site_docs" / "knowledge" / "index.md"
        generated_docs_index = ROOT / "generated" / "site_docs" / "system-design-docs" / "index.md"
        generated_explorer = ROOT / "generated" / "site_docs" / "knowledge" / "explorer.md"
        generated_health = ROOT / "generated" / "site_docs" / "knowledge" / "content-health.md"
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
        self.assertTrue(generated_health.exists())
        self.assertTrue(generated_ticket_guide.exists())
        self.assertTrue(generated_license_guide.exists())
        generated_home_text = generated_home.read_text(encoding="utf-8")
        generated_explorer_text = generated_explorer.read_text(encoding="utf-8")
        generated_ticket_guide_text = generated_ticket_guide.read_text(encoding="utf-8")
        generated_license_guide_text = generated_license_guide.read_text(encoding="utf-8")
        self.assertIn("Knowledge Base", generated_home_text)
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

    @unittest.skipUnless(mkdocs_available(), "mkdocs not installed")
    def test_build_sh_runs_rendered_site_validation(self) -> None:
        result = subprocess.run(
            ["bash", "scripts/build.sh"],
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
        with sqlite3.connect(ROOT / "build" / "knowledge.db") as connection:
            table_names = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
                ).fetchall()
            }
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
