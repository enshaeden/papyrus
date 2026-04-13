from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


class DocumentationContractTests(unittest.TestCase):
    def test_reference_docs_describe_ui_boundary_and_semantic_hooks(self) -> None:
        operator_web_ui = (ROOT / "docs" / "reference" / "operator-web-ui.md").read_text(encoding="utf-8").lower()
        self.assertIn("routes should not emit html fragments", operator_web_ui)
        self.assertIn("data-surface", operator_web_ui)
        self.assertIn("data-component", operator_web_ui)
        self.assertIn("data-action-id", operator_web_ui)
        self.assertIn("shared component canon", operator_web_ui)
        self.assertIn("content-section", operator_web_ui)
        self.assertIn("context-panel", operator_web_ui)
        self.assertIn("guided drafting uses the `normal` shell", operator_web_ui)
        self.assertIn("production ui must not expose an actor switcher", operator_web_ui)
        self.assertIn("/reader/*", operator_web_ui)
        self.assertIn("/operator/*", operator_web_ui)
        self.assertIn("/admin/*", operator_web_ui)
        self.assertIn("400 bad request", operator_web_ui)
        self.assertIn("post /operator/write/object/{object_id}/start", operator_web_ui)
        self.assertIn("no separate page-header actor banner contract", operator_web_ui)
        self.assertIn("url-driven selection state", operator_web_ui)
        self.assertIn("papyrus.interfaces.web.view_models.article_projection", operator_web_ui)

    def test_operator_readiness_records_recovery_and_cleanup_boundary(self) -> None:
        operator_readiness = (ROOT / "docs" / "reference" / "operator-readiness.md").read_text(encoding="utf-8").lower()
        self.assertIn("pending mutation recovery", operator_readiness)
        self.assertIn("stale journals and stale locks", operator_readiness)
        self.assertIn("fails closed", operator_readiness)
        self.assertIn("placeholder-heavy content", operator_readiness)
        self.assertIn("remaining technical debt", operator_readiness)

    def test_getting_started_inventory_marks_retired_import_shim(self) -> None:
        getting_started = (ROOT / "docs" / "getting-started.md").read_text(encoding="utf-8").lower()
        self.assertIn("retired legacy migration shim", getting_started)
        self.assertIn("import_knowledge_portal.py", getting_started)
        self.assertIn("decisions/index.md", getting_started)
        self.assertIn("/operator", getting_started)
        self.assertIn("/reader/*", getting_started)
        self.assertIn("/admin/*", getting_started)

    def test_lifecycle_decision_uses_explicit_state_machines(self) -> None:
        lifecycle = (ROOT / "docs" / "decisions" / "knowledge-workflows-and-lifecycle.md").read_text(encoding="utf-8").lower()
        self.assertIn("object_lifecycle_state", lifecycle)
        self.assertIn("revision_review_state", lifecycle)
        self.assertIn("draft_progress_state", lifecycle)
        self.assertIn("`published` is not a separate revision-review state", lifecycle)
        self.assertIn("do not encode it as `object_lifecycle_state = flagged`", lifecycle)

    def test_docs_do_not_overclaim_removed_writeback_guarantees(self) -> None:
        forbidden = (
            "one authoritative layer",
            "write back deterministically",
            "deterministic application-layer flow",
            "business logic remains in the shared application layer",
        )
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "getting-started.md",
            ROOT / "docs" / "reference" / "system-model.md",
            ROOT / "docs" / "reference" / "operator-readiness.md",
            ROOT / "docs" / "reference" / "operator-web-ui.md",
        ]:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in forbidden:
                self.assertNotIn(phrase, text, msg=f"{path} still contains overclaim: {phrase}")
