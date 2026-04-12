from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.infrastructure.repositories.knowledge_repo import collect_source_paths  # noqa: E402


class KnowledgeRepoTests(unittest.TestCase):
    def test_collect_source_paths_excludes_agents_documents(self) -> None:
        paths = collect_source_paths()

        self.assertTrue(paths, msg="expected canonical knowledge sources")
        self.assertNotIn(ROOT / "knowledge" / "AGENTS.md", paths)
        self.assertTrue(all(path.name != "AGENTS.md" for path in paths))


if __name__ == "__main__":
    unittest.main()
