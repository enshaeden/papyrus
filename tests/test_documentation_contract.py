from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


class DocumentationContractTests(unittest.TestCase):
    def test_reference_docs_describe_ui_boundary_and_semantic_hooks(self) -> None:
        operator_web_ui = (
            (ROOT / "docs" / "reference" / "operator-web-ui.md").read_text(encoding="utf-8").lower()
        )
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
        self.assertIn("pantone 7659 c", operator_web_ui)
        self.assertIn("identity and intent", operator_web_ui)
        self.assertIn("authority and depth", operator_web_ui)
        self.assertIn("context and grouping", operator_web_ui)
        self.assertIn("neutral surfaces must dominate", operator_web_ui)

    def test_operator_readiness_records_recovery_and_cleanup_boundary(self) -> None:
        operator_readiness = (
            (ROOT / "docs" / "reference" / "operator-readiness.md")
            .read_text(encoding="utf-8")
            .lower()
        )
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
        self.assertIn("not part of the role-scoped web experience contract", getting_started)
        self.assertIn("separate decision and migration", getting_started)

    def test_canonical_decision_docs_lock_experience_architecture(self) -> None:
        experience_architecture = (
            (ROOT / "decisions" / "role-scoped-experience-architecture.md")
            .read_text(encoding="utf-8")
            .lower()
        )
        layout_contracts = (
            (ROOT / "decisions" / "layout-contracts-by-role.md").read_text(encoding="utf-8").lower()
        )
        component_contracts = (
            (ROOT / "decisions" / "web-ui-component-contracts.md")
            .read_text(encoding="utf-8")
            .lower()
        )

        self.assertIn(
            "global search is shell-owned and remains centered in the top bar",
            experience_architecture,
        )
        self.assertIn("pantone 7659 c", experience_architecture)
        self.assertIn("one dominant purple-family tone per component", experience_architecture)
        self.assertIn("redirecting to `/operator`", experience_architecture)
        self.assertIn("`local.operator` maps to operator", experience_architecture)
        self.assertIn("top bar", layout_contracts)
        self.assertIn("contextual only", layout_contracts)
        self.assertIn("page files are assemblers only", component_contracts)
        self.assertIn("data-component", component_contracts)
        self.assertIn("remove duplicated navigation", component_contracts)

    def test_mkdocs_nav_lists_only_canonical_decision_records(self) -> None:
        mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8").lower()

        self.assertIn("role-scoped experience architecture", mkdocs)
        self.assertIn("layout contracts by role", mkdocs)
        self.assertIn("knowledge workflows and lifecycle", mkdocs)
        self.assertIn("web ui component contracts", mkdocs)
        self.assertNotIn("experience principles: decisions/experience-principles.md", mkdocs)
        self.assertNotIn(
            "role and visibility matrix: decisions/role-experience-visibility-matrix.md", mkdocs
        )
        self.assertNotIn(
            "route separation and experience boundaries: decisions/route-separation-and-experience-boundaries.md",
            mkdocs,
        )
        self.assertNotIn(
            "actor model to role model mapping: decisions/actor-model-to-role-model-mapping.md",
            mkdocs,
        )

    def test_docs_describe_operator_only_api_boundary(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        system_model = (
            (ROOT / "docs" / "reference" / "system-model.md").read_text(encoding="utf-8").lower()
        )
        read_playbook = (
            (ROOT / "docs" / "playbooks" / "read.md").read_text(encoding="utf-8").lower()
        )

        self.assertIn(
            "papyrus is a governed knowledge management database that provides end users with dependable content, while it operators maintain backend authorship and oversight.",
            readme,
        )
        self.assertIn("operator-oriented local api surface", readme)
        self.assertIn("separate decision and migration", readme)
        self.assertIn("governance and decisions", readme)
        self.assertIn("json api remains an operator-oriented local surface", system_model)
        self.assertIn("not part of the role-scoped web route contract", system_model)
        self.assertIn("json api remains operator-oriented", read_playbook)

    def test_lifecycle_decision_uses_explicit_state_machines(self) -> None:
        lifecycle = (
            (ROOT / "decisions" / "knowledge-workflows-and-lifecycle.md")
            .read_text(encoding="utf-8")
            .lower()
        )
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

    def test_docs_no_longer_reference_split_decision_tree(self) -> None:
        for path in [
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "docs" / "AGENTS.md",
            ROOT / "docs" / "index.md",
            ROOT / "docs" / "getting-started.md",
            ROOT / "src" / "papyrus" / "interfaces" / "web" / "AGENTS.md",
        ]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                "docs/decisions/", text, msg=f"{path} still references docs/decisions/"
            )

    def test_readme_is_current_state_entrypoint(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("## run it now", readme)
        self.assertIn("## source of truth", readme)
        self.assertIn("## read more", readme)
        self.assertIn("python3 scripts/run.py --operator", readme)
        self.assertIn("governance and decisions: [decisions/index.md]", readme)
        self.assertNotIn("docs/decisions/", readme)
