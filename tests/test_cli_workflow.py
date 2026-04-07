from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copytree


ROOT = Path(__file__).resolve().parent.parent


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
        generated_index = ROOT / "generated" / "site_docs" / "knowledge" / "index.md"
        self.assertTrue(generated_index.exists())

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
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            created_path = temp_root / result.stdout.strip()
            self.assertTrue(created_path.exists())
            self.assertIn("Temporary Example Procedure", created_path.read_text(encoding="utf-8"))
            self.assertIn("canonical_path:", created_path.read_text(encoding="utf-8"))

    def test_validate_cli(self) -> None:
        result = run_command("scripts/validate.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("validated", result.stdout)

    def test_build_index_and_search_cli(self) -> None:
        build_result = run_command("scripts/build_index.py")
        self.assertEqual(build_result.returncode, 0, msg=build_result.stderr)
        self.assertIn("knowledge.db", build_result.stdout)

        search_result = run_command("scripts/search.py", "vpn")
        self.assertEqual(search_result.returncode, 0, msg=search_result.stderr)
        self.assertIn("VPN Troubleshooting", search_result.stdout)

    def test_stale_report_for_seed_date(self) -> None:
        result = run_command("scripts/report_stale.py", "--as-of", "2026-04-07")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("no stale articles found", result.stdout)

    def test_content_health_report_cli(self) -> None:
        result = run_command("scripts/report_content_health.py", "--section", "duplicates")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[duplicates]", result.stdout)


if __name__ == "__main__":
    unittest.main()
