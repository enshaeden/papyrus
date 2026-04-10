from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
INVENTORY_DOC = ROOT / "docs" / "getting-started.md"


class ScriptInventoryTests(unittest.TestCase):
    def test_every_top_level_script_is_recorded_in_inventory(self) -> None:
        inventory_text = INVENTORY_DOC.read_text(encoding="utf-8")
        script_names = sorted(
            path.name
            for path in SCRIPTS_DIR.iterdir()
            if path.is_file()
        )
        self.assertTrue(script_names, msg="expected at least one top-level script")
        for script_name in script_names:
            self.assertIn(f"`{script_name}`", inventory_text, msg=f"{script_name} is missing from docs/getting-started.md")
