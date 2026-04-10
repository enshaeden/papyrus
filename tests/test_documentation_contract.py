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
    ROOT / "docs" / "reference" / "operator-web-ui.md",
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

    def test_docs_keep_acknowledgement_and_conflict_language_explicit(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        manage = (ROOT / "docs" / "playbooks" / "manage.md").read_text(encoding="utf-8").lower()
        system_model = (ROOT / "docs" / "reference" / "system-model.md").read_text(encoding="utf-8").lower()
        self.assertIn("required acknowledgements", readme)
        self.assertIn("required acknowledgements", manage)
        self.assertIn("conflicted", system_model)
        self.assertIn("restored", system_model)

    def test_docs_describe_backend_ui_cut_line_and_guardrails(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        system_model = (ROOT / "docs" / "reference" / "system-model.md").read_text(encoding="utf-8").lower()
        operator_readiness = (ROOT / "docs" / "reference" / "operator-readiness.md").read_text(encoding="utf-8").lower()
        operator_web_ui = (ROOT / "docs" / "reference" / "operator-web-ui.md").read_text(encoding="utf-8").lower()
        self.assertIn("contract-driven surface boundary", readme)
        self.assertIn("backend/ui cut line", system_model)
        self.assertIn("do not reintroduce route-local policy checks", system_model)
        self.assertIn("surfaces render `ui_projection`", operator_readiness)
        self.assertIn("should not derive governed action availability", operator_web_ui)

    def test_docs_record_recovery_behavior_and_remaining_fallback_debt(self) -> None:
        getting_started = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8").lower()
        write_playbook = (ROOT / "docs" / "playbooks" / "write.md").read_text(encoding="utf-8").lower()
        operator_readiness = (ROOT / "docs" / "reference" / "operator-readiness.md").read_text(encoding="utf-8").lower()
        self.assertIn("pending mutation recovery", getting_started)
        self.assertIn("retained technical debt", write_playbook)
        self.assertIn("stale journals and stale locks", getting_started)
        self.assertIn("remaining technical debt", operator_readiness)
