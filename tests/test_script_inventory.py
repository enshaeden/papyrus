from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
INVENTORY_DOC = ROOT / "knowledge" / "getting-started.md"
WRAPPER_IMPORTS = {
    "build_route_map.py": "from papyrus.jobs.route_map_build import main",
    "demo_runtime.py": "from papyrus.jobs.demo_runtime_build import main",
    "ingest_event.py": "from papyrus.interfaces.ingest_event_cli import main",
    "new_object.py": "from papyrus.interfaces.new_object_cli import main",
    "run.py": "from papyrus.interfaces.local_runtime_cli import main",
    "source_sync.py": "from papyrus.interfaces.source_sync_cli import main",
}


class ScriptInventoryTests(unittest.TestCase):
    def test_every_top_level_script_is_recorded_in_inventory(self) -> None:
        inventory_text = INVENTORY_DOC.read_text(encoding="utf-8")
        script_names = sorted(path.name for path in SCRIPTS_DIR.iterdir() if path.is_file())
        self.assertTrue(script_names, msg="expected at least one top-level script")
        for script_name in script_names:
            self.assertIn(
                f"`{script_name}`",
                inventory_text,
                msg=f"{script_name} is missing from knowledge/getting-started.md",
            )

    def test_curated_entrypoints_remain_wrappers(self) -> None:
        for script_name, expected_import in WRAPPER_IMPORTS.items():
            script_text = (SCRIPTS_DIR / script_name).read_text(encoding="utf-8")
            self.assertIn(
                expected_import,
                script_text,
                msg=f"{script_name} should delegate to a packaged module",
            )
            self.assertIn(
                "ensure_src_path()",
                script_text,
                msg=f"{script_name} should bootstrap src/ before import",
            )

    def test_removed_migration_scripts_are_not_present(self) -> None:
        self.assertFalse((SCRIPTS_DIR / "import_knowledge_portal.py").exists())
        self.assertFalse((SCRIPTS_DIR / "validate_migration.py").exists())
