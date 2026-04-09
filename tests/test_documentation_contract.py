from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


DOC_PATHS = [
    ROOT / "README.md",
    ROOT / "docs" / "getting-started.md",
    ROOT / "docs" / "reference" / "system-model.md",
    ROOT / "docs" / "reference" / "operator-readiness.md",
    ROOT / "docs" / "playbooks" / "write.md",
    ROOT / "docs" / "playbooks" / "manage.md",
]


class DocumentationContractTests(unittest.TestCase):
    def test_docs_do_not_overclaim_old_writeback_guarantees(self) -> None:
        forbidden = (
            "one authoritative layer",
            "write back deterministically",
            "deterministic application-layer flow",
            "Business logic remains in the shared application layer",
        )
        for path in DOC_PATHS:
            text = path.read_text(encoding="utf-8")
            for phrase in forbidden:
                self.assertNotIn(phrase, text, msg=f"{path} still contains overclaim: {phrase}")

    def test_docs_describe_explicit_policy_and_state_model(self) -> None:
        system_model = (ROOT / "docs" / "reference" / "system-model.md").read_text(encoding="utf-8")
        getting_started = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8")
        self.assertIn("object_lifecycle_state", system_model)
        self.assertIn("revision_review_state", system_model)
        self.assertIn("source_sync_state", system_model)
        self.assertIn("allowlisted read roots", getting_started)
