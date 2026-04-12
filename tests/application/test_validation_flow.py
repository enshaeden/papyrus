from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.validation_flow import validate_knowledge_documents
from papyrus.domain.entities import KnowledgeDocument
from papyrus.infrastructure.repositories.knowledge_repo import load_object_schemas, load_policy, load_schema, load_taxonomies


def _citation() -> list[dict[str, object]]:
    return [
        {
            "article_id": None,
            "source_title": "Write playbook",
            "source_type": "document",
            "source_ref": "docs/playbooks/write.md",
            "note": "Local governed reference.",
            "excerpt": None,
            "captured_at": None,
            "validity_status": "verified",
            "integrity_hash": None,
        }
    ]


class BlueprintValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.object_schemas = load_object_schemas()
        self.legacy_schema = load_schema()
        self.taxonomies = load_taxonomies()
        self.policy = load_policy()

    def test_legacy_runbook_uses_blueprint_fallback_without_failing_required_sections(self) -> None:
        document = KnowledgeDocument(
            source_path=ROOT / "knowledge" / "tests" / "legacy-runbook.md",
            relative_path="knowledge/tests/legacy-runbook.md",
            metadata={
                "id": "kb-tests-legacy-runbook",
                "title": "Legacy Runbook",
                "canonical_path": "knowledge/tests/legacy-runbook.md",
                "summary": "Guide operators through a legacy but still governed procedure.",
                "knowledge_object_type": "runbook",
                "legacy_article_type": "runbook",
                "object_lifecycle_state": "active",
                "owner": "workflow_owner",
                "source_type": "imported",
                "source_system": "knowledge_portal_export",
                "source_title": "Legacy Runbook",
                "team": "IT Operations",
                "systems": ["<VPN_SERVICE>"],
                "tags": ["vpn"],
                "created": "2026-04-08",
                "updated": "2026-04-08",
                "last_reviewed": "2026-04-08",
                "review_cadence": "quarterly",
                "audience": "service_desk",
                "related_services": ["Remote Access"],
                "prerequisites": ["Open the ticket before continuing."],
                "steps": ["Perform the documented recovery step."],
                "verification": ["Confirm the service is restored."],
                "rollback": ["Undo the change if verification fails."],
                "citations": _citation(),
                "related_object_ids": [],
                "superseded_by": None,
                "replaced_by": None,
                "retirement_reason": None,
                "services": ["Remote Access"],
                "related_articles": [],
                "references": [{"title": "Write playbook", "path": "docs/playbooks/write.md", "note": "Local governed reference."}],
                "change_log": [{"date": "2026-04-08", "summary": "Imported legacy runbook.", "author": "tests"}],
            },
            body=(
                "## Overview\n\n"
                "Use this runbook when the legacy procedure still applies to the current request.\n\n"
                "## Effective-Date Actions\n\n"
                "1. Perform the recovery step.\n"
                "2. Stop and escalate if approvals or scope do not match the request."
            ),
        )

        issues = validate_knowledge_documents(
            [document],
            self.object_schemas,
            self.legacy_schema,
            self.taxonomies,
            self.policy,
        )

        blueprint_issues = [issue for issue in issues if "required blueprint section is incomplete" in issue.message]
        self.assertEqual(blueprint_issues, [])

    def test_native_runbook_without_required_blueprint_sections_still_fails(self) -> None:
        document = KnowledgeDocument(
            source_path=ROOT / "knowledge" / "tests" / "native-runbook.md",
            relative_path="knowledge/tests/native-runbook.md",
            metadata={
                "id": "kb-tests-native-runbook",
                "title": "Native Runbook",
                "canonical_path": "knowledge/tests/native-runbook.md",
                "summary": "Guide operators through a native runbook.",
                "knowledge_object_type": "runbook",
                "legacy_article_type": None,
                "object_lifecycle_state": "active",
                "owner": "workflow_owner",
                "source_type": "native",
                "source_system": "repository",
                "source_title": "Native Runbook",
                "team": "IT Operations",
                "systems": ["<VPN_SERVICE>"],
                "tags": ["vpn"],
                "created": "2026-04-08",
                "updated": "2026-04-08",
                "last_reviewed": "2026-04-08",
                "review_cadence": "quarterly",
                "audience": "service_desk",
                "related_services": ["Remote Access"],
                "prerequisites": ["Open the ticket before continuing."],
                "steps": ["Perform the documented recovery step."],
                "verification": ["Confirm the service is restored."],
                "rollback": ["Undo the change if verification fails."],
                "citations": _citation(),
                "related_object_ids": [],
                "superseded_by": None,
                "replaced_by": None,
                "retirement_reason": None,
                "services": ["Remote Access"],
                "related_articles": [],
                "references": [{"title": "Write playbook", "path": "docs/playbooks/write.md", "note": "Local governed reference."}],
                "change_log": [{"date": "2026-04-08", "summary": "Created native runbook.", "author": "tests"}],
            },
            body="## Procedure\n\nPerform the procedure exactly as written.",
        )

        issues = validate_knowledge_documents(
            [document],
            self.object_schemas,
            self.legacy_schema,
            self.taxonomies,
            self.policy,
        )

        self.assertIn(
            "required blueprint section is incomplete: Purpose",
            [issue.message for issue in issues],
        )

    def test_native_policy_without_required_blueprint_sections_still_fails(self) -> None:
        document = KnowledgeDocument(
            source_path=ROOT / "knowledge" / "tests" / "native-policy.md",
            relative_path="knowledge/tests/native-policy.md",
            metadata={
                "id": "kb-tests-native-policy",
                "title": "Native Policy",
                "canonical_path": "knowledge/tests/native-policy.md",
                "summary": "Govern remote access changes.",
                "knowledge_object_type": "policy",
                "legacy_article_type": None,
                "object_lifecycle_state": "active",
                "owner": "workflow_owner",
                "source_type": "native",
                "source_system": "repository",
                "source_title": "Native Policy",
                "team": "IT Operations",
                "systems": ["<VPN_SERVICE>"],
                "tags": ["vpn"],
                "created": "2026-04-08",
                "updated": "2026-04-08",
                "last_reviewed": "2026-04-08",
                "review_cadence": "annual",
                "audience": "service_desk",
                "citations": _citation(),
                "related_object_ids": [],
                "policy_scope": "",
                "controls": [],
                "exceptions": "",
                "superseded_by": None,
                "replaced_by": None,
                "retirement_reason": None,
                "services": [],
                "related_articles": [],
                "references": [{"title": "Write playbook", "path": "docs/playbooks/write.md", "note": "Local governed reference."}],
                "change_log": [{"date": "2026-04-08", "summary": "Created native policy.", "author": "tests"}],
            },
            body="## Policy Scope\n\n",
        )

        issues = validate_knowledge_documents(
            [document],
            self.object_schemas,
            self.legacy_schema,
            self.taxonomies,
            self.policy,
        )

        messages = [issue.message for issue in issues]
        self.assertIn("required blueprint section is incomplete: Scope", messages)
        self.assertIn("required blueprint section is incomplete: Controls", messages)

    def test_native_system_design_without_required_blueprint_sections_still_fails(self) -> None:
        document = KnowledgeDocument(
            source_path=ROOT / "knowledge" / "tests" / "native-system-design.md",
            relative_path="knowledge/tests/native-system-design.md",
            metadata={
                "id": "kb-tests-native-system-design",
                "title": "Native System Design",
                "canonical_path": "knowledge/tests/native-system-design.md",
                "summary": "Describe the identity platform architecture.",
                "knowledge_object_type": "system_design",
                "legacy_article_type": None,
                "object_lifecycle_state": "active",
                "owner": "workflow_owner",
                "source_type": "native",
                "source_system": "repository",
                "source_title": "Native System Design",
                "team": "IT Operations",
                "systems": ["<IDENTITY_PROVIDER>"],
                "tags": ["identity"],
                "created": "2026-04-08",
                "updated": "2026-04-08",
                "last_reviewed": "2026-04-08",
                "review_cadence": "after_change",
                "audience": "service_desk",
                "citations": _citation(),
                "related_object_ids": [],
                "dependencies": [],
                "interfaces": [],
                "common_failure_modes": [],
                "support_entrypoints": [],
                "architecture": "",
                "superseded_by": None,
                "replaced_by": None,
                "retirement_reason": None,
                "services": [],
                "related_articles": [],
                "references": [{"title": "Write playbook", "path": "docs/playbooks/write.md", "note": "Local governed reference."}],
                "change_log": [{"date": "2026-04-08", "summary": "Created native system design.", "author": "tests"}],
            },
            body="## Architecture\n\n",
        )

        issues = validate_knowledge_documents(
            [document],
            self.object_schemas,
            self.legacy_schema,
            self.taxonomies,
            self.policy,
        )

        messages = [issue.message for issue in issues]
        self.assertIn("required blueprint section is incomplete: Architecture", messages)
        self.assertIn("required blueprint section is incomplete: Dependencies", messages)
        self.assertIn("required blueprint section is incomplete: Interfaces", messages)
        self.assertIn("required blueprint section is incomplete: Failure Modes", messages)
        self.assertIn("required blueprint section is incomplete: Operations", messages)


if __name__ == "__main__":
    unittest.main()
