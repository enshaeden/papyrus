from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.authoring_flow import (
    CONVERSION_GAPS_KEY,
    FIELD_PROVENANCE_KEY,
    build_draft_revision_artifacts,
    compute_completion_state,
    create_draft_from_blueprint,
    update_section,
    validate_draft_progress,
)
from papyrus.application.blueprint_registry import get_blueprint
from papyrus.application.commands import create_object_command, submit_for_review_command
from papyrus.application.queries import knowledge_object_detail
from papyrus.application.revision_runtime import RevisionRuntimeServices
from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies


class AuthoringFlowTests(unittest.TestCase):
    def test_revision_runtime_service_parses_revision_without_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            runtime = RevisionRuntimeServices(source_root=source_root, taxonomies=load_taxonomies())

            parsed = runtime.parse_revision(
                {
                    "id": "kb-policy-runtime",
                    "title": "Runtime Policy",
                    "canonical_path": "knowledge/policies/runtime-policy.md",
                    "summary": "Govern runtime changes.",
                    "knowledge_object_type": "policy",
                    "legacy_article_type": None,
                    "status": "draft",
                    "owner": "workflow_owner",
                    "source_type": "native",
                    "source_system": "repository",
                    "source_title": "Runtime Policy",
                    "team": "IT Operations",
                    "systems": ["<VPN_SERVICE>"],
                    "tags": ["vpn"],
                    "created": "2026-04-09",
                    "updated": "2026-04-09",
                    "last_reviewed": "2026-04-09",
                    "review_cadence": "annual",
                    "audience": "service_desk",
                    "citations": [
                        {
                            "source_title": "Write playbook",
                            "source_type": "document",
                            "source_ref": "docs/playbooks/write.md",
                            "note": "Governed reference.",
                        }
                    ],
                    "related_object_ids": [],
                    "policy_scope": "Applies to runtime changes.",
                    "controls": ["Require approval before production changes."],
                    "exceptions": "",
                    "superseded_by": None,
                    "replaced_by": None,
                    "retirement_reason": None,
                    "services": [],
                    "related_articles": [],
                    "references": [{"title": "Write playbook", "path": "docs/playbooks/write.md", "note": "Governed reference."}],
                    "change_log": [{"date": "2026-04-09", "summary": "Created runtime seam test.", "author": "tests"}],
                },
                "## Policy Scope\n\nApplies to runtime changes.\n",
            )

            self.assertEqual(parsed.object_type, "policy")
            self.assertEqual(parsed.metadata["canonical_path"], "knowledge/policies/runtime-policy.md")
            self.assertEqual(parsed.metadata["review_cadence"], "annual")

    def test_build_draft_revision_artifacts_is_unit_testable_without_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            runtime = RevisionRuntimeServices(source_root=source_root, taxonomies=load_taxonomies())
            blueprint = get_blueprint("policy")
            object_row = {
                "object_id": "kb-policy-artifacts",
                "title": "Artifact Policy",
                "summary": "Govern artifact updates.",
                "owner": "workflow_owner",
                "team": "IT Operations",
                "canonical_path": "knowledge/policies/artifact-policy.md",
                "status": "draft",
                "review_cadence": "annual",
                "source_type": "native",
                "source_system": "repository",
                "created_date": "2026-04-09",
            }
            section_content = {
                "identity": {
                    "object_id": "kb-policy-artifacts",
                    "title": "Artifact Policy",
                    "canonical_path": "knowledge/policies/artifact-policy.md",
                },
                "stewardship": {
                    "summary": "Govern artifact updates.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "status": "draft",
                    "review_cadence": "annual",
                    "audience": "service_desk",
                    "systems": ["<VPN_SERVICE>"],
                    "tags": ["vpn"],
                    "related_services": [],
                    "related_object_ids": [],
                    "change_summary": "",
                },
                "policy_scope": {"policy_scope": "Applies to artifact updates."},
                "controls": {"controls": ["Require CAB approval before production change."]},
                "exceptions": {"exceptions": ""},
                "evidence": {
                    "citations": [
                        {
                            "source_title": "Write playbook",
                            "source_type": "document",
                            "source_ref": "docs/playbooks/write.md",
                            "note": "Governed reference.",
                        }
                    ]
                },
                "relationships": {"related_object_ids": []},
            }

            artifacts = build_draft_revision_artifacts(
                blueprint=blueprint,
                object_row=object_row,
                section_content=section_content,
                actor="local.operator",
                existing_metadata=None,
                runtime=runtime,
            )

            self.assertEqual(artifacts.payload["controls"], ["Require CAB approval before production change."])
            self.assertIn("## Policy Scope", artifacts.body_markdown)
            self.assertEqual(artifacts.completion["draft_progress_state"], "ready_for_review")
            self.assertEqual(artifacts.completion["completion_percentage"], 100)
            self.assertEqual(artifacts.parsed.metadata["knowledge_object_type"], "policy")

    def test_blueprint_draft_progress_moves_to_ready_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            create_object_command(
                database_path=database_path,
                source_root=source_root,
                actor="local.operator",
                object_id="kb-blueprint-runbook",
                object_type="runbook",
                title="Blueprint Runbook",
                summary="Guided blueprint coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/blueprint-runbook.md",
                review_cadence="quarterly",
                status="draft",
            )
            created = create_draft_from_blueprint(
                object_id="kb-blueprint-runbook",
                blueprint_id="runbook",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )
            revision_id = str(created["revision_id"])
            self.assertIn(created["completion"]["draft_progress_state"], {"blocked", "in_progress"})

            updates = {
                "purpose": {"use_when": "Use this when the operator needs guided recovery."},
                "prerequisites": {"prerequisites": ["Open the incident ticket."]},
                "procedure": {"steps": ["Validate the precondition.", "Apply the fix."]},
                "verification": {"verification": ["Confirm the service recovers."]},
                "rollback": {"rollback": ["Undo the applied fix."]},
                "boundaries": {"boundaries_and_escalation": "Escalate after two failed attempts.", "related_knowledge_notes": ""},
                "evidence": {"citations": [{"source_title": "Controlled reference", "source_type": "document", "source_ref": "docs/playbooks/write.md", "note": "Governed internal evidence."}]},
            }
            for section_id, values in updates.items():
                update_section(
                    object_id="kb-blueprint-runbook",
                    revision_id=revision_id,
                    section_id=section_id,
                    values=values,
                    actor="local.operator",
                    database_path=database_path,
                    source_root=source_root,
                )

            progress = validate_draft_progress(
                object_id="kb-blueprint-runbook",
                revision_id=revision_id,
                database_path=database_path,
                source_root=source_root,
            )
            self.assertEqual(progress["completion"]["draft_progress_state"], "ready_for_review")
            self.assertEqual(progress["completion"]["completion_percentage"], 100)

    def test_draft_progress_exposes_field_level_import_provenance_and_conversion_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            create_object_command(
                database_path=database_path,
                source_root=source_root,
                actor="local.operator",
                object_id="kb-imported-runbook",
                object_type="runbook",
                title="Imported Runbook",
                summary="",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/imported/runbook.md",
                review_cadence="quarterly",
                status="draft",
            )
            created = create_draft_from_blueprint(
                object_id="kb-imported-runbook",
                blueprint_id="runbook",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )
            revision_id = str(created["revision_id"])

            update_section(
                object_id="kb-imported-runbook",
                revision_id=revision_id,
                section_id="purpose",
                values={"use_when": ""},
                section_metadata={
                    FIELD_PROVENANCE_KEY: {
                        "use_when": {
                            "status": "manual_required",
                            "note": "Import conversion could not determine a reliable purpose field.",
                        }
                    },
                    CONVERSION_GAPS_KEY: [
                        {
                            "field": "use_when",
                            "status": "manual_required",
                            "reason": "Import conversion could not determine a reliable purpose field.",
                        }
                    ],
                },
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            progress = validate_draft_progress(
                object_id="kb-imported-runbook",
                revision_id=revision_id,
                database_path=database_path,
                source_root=source_root,
            )
            purpose_completion = progress["completion"]["section_completion_map"]["purpose"]
            field_status = purpose_completion["fields"]["use_when"]

            self.assertFalse(field_status["completed"])
            self.assertFalse(field_status["value_present"])
            self.assertEqual(field_status["provenance"]["status"], "manual_required")
            self.assertEqual(purpose_completion["conversion_gaps"][0]["field"], "use_when")
            self.assertIn(
                "Purpose: Use when remains manual_required after import.",
                progress["completion"]["warnings"],
            )

    def test_policy_blueprint_progress_and_submit_use_explicit_policy_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            create_object_command(
                database_path=database_path,
                source_root=source_root,
                actor="local.operator",
                object_id="kb-policy-blueprint",
                object_type="policy",
                title="Remote Access Change Policy",
                summary="Govern remote access changes.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/policies/remote-access-change-policy.md",
                review_cadence="annual",
                status="draft",
            )
            created = create_draft_from_blueprint(
                object_id="kb-policy-blueprint",
                blueprint_id="policy",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )
            revision_id = str(created["revision_id"])

            updates = {
                "policy_scope": {"policy_scope": "Applies to authentication, VPN, and remote access control changes."},
                "controls": {"controls": ["Require CAB approval before production change.", "Document rollback before execution."]},
                "exceptions": {"exceptions": "Emergency changes require follow-up review within 24 hours."},
                "evidence": {"citations": [{"source_title": "Write playbook", "source_type": "document", "source_ref": "docs/playbooks/write.md", "note": "Authoring control reference."}]},
            }
            for section_id, values in updates.items():
                update_section(
                    object_id="kb-policy-blueprint",
                    revision_id=revision_id,
                    section_id=section_id,
                    values=values,
                    actor="local.operator",
                    database_path=database_path,
                    source_root=source_root,
                )

            progress = validate_draft_progress(
                object_id="kb-policy-blueprint",
                revision_id=revision_id,
                database_path=database_path,
                source_root=source_root,
            )
            self.assertEqual(progress["completion"]["draft_progress_state"], "ready_for_review")
            self.assertEqual(progress["completion"]["completion_percentage"], 100)
            self.assertTrue(progress["completion"]["section_completion_map"]["policy_scope"]["completed"])
            self.assertTrue(progress["completion"]["section_completion_map"]["controls"]["completed"])

            submit_for_review_command(
                database_path=database_path,
                source_root=source_root,
                object_id="kb-policy-blueprint",
                revision_id=revision_id,
                actor="local.operator",
                notes="Policy draft ready for governance review.",
            )
            detail = knowledge_object_detail("kb-policy-blueprint", database_path=database_path)
            self.assertEqual(detail["current_revision"]["revision_review_state"], "in_review")
            self.assertEqual(detail["current_revision"]["blueprint_id"], "policy")

    def test_system_design_blueprint_progress_and_submit_use_explicit_system_design_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            create_object_command(
                database_path=database_path,
                source_root=source_root,
                actor="local.operator",
                object_id="kb-system-design-blueprint",
                object_type="system_design",
                title="Identity Platform Design",
                summary="Document the identity platform architecture.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/system-designs/identity-platform.md",
                review_cadence="after_change",
                status="draft",
            )
            created = create_draft_from_blueprint(
                object_id="kb-system-design-blueprint",
                blueprint_id="system_design",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )
            revision_id = str(created["revision_id"])

            updates = {
                "architecture": {"architecture": "Identity broker fronts directory, OAuth, and SAML providers."},
                "dependencies": {"dependencies": ["Directory service", "MFA provider"]},
                "interfaces": {"interfaces": ["OIDC callback", "SCIM provisioning API"]},
                "failure_modes": {"common_failure_modes": ["Signing key drift", "Directory sync delay"]},
                "operations": {
                    "operational_notes": "Coordinate production changes through platform operations.",
                    "support_entrypoints": ["Service Desk -> Identity Engineering"],
                },
                "evidence": {"citations": [{"source_title": "Write playbook", "source_type": "document", "source_ref": "docs/playbooks/write.md", "note": "Authoring control reference."}]},
            }
            for section_id, values in updates.items():
                update_section(
                    object_id="kb-system-design-blueprint",
                    revision_id=revision_id,
                    section_id=section_id,
                    values=values,
                    actor="local.operator",
                    database_path=database_path,
                    source_root=source_root,
                )

            progress = validate_draft_progress(
                object_id="kb-system-design-blueprint",
                revision_id=revision_id,
                database_path=database_path,
                source_root=source_root,
            )
            self.assertEqual(progress["completion"]["draft_progress_state"], "ready_for_review")
            self.assertEqual(progress["completion"]["completion_percentage"], 100)
            self.assertTrue(progress["completion"]["section_completion_map"]["architecture"]["completed"])
            self.assertTrue(progress["completion"]["section_completion_map"]["operations"]["completed"])

            submit_for_review_command(
                database_path=database_path,
                source_root=source_root,
                object_id="kb-system-design-blueprint",
                revision_id=revision_id,
                actor="local.operator",
                notes="System design draft ready for governance review.",
            )
            detail = knowledge_object_detail("kb-system-design-blueprint", database_path=database_path)
            self.assertEqual(detail["current_revision"]["revision_review_state"], "in_review")
            self.assertEqual(detail["current_revision"]["blueprint_id"], "system_design")

    def test_validate_draft_progress_uses_supplied_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            create_object_command(
                database_path=database_path,
                source_root=source_root,
                actor="local.operator",
                object_id="kb-source-root-progress",
                object_type="runbook",
                title="Source Root Progress",
                summary="Verify progress uses the supplied root.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/source-root-progress.md",
                review_cadence="quarterly",
                status="draft",
            )
            created = create_draft_from_blueprint(
                object_id="kb-source-root-progress",
                blueprint_id="runbook",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            with patch("papyrus.application.authoring_flow.RevisionRuntimeServices") as runtime_class:
                runtime_instance = runtime_class.return_value
                runtime_instance.taxonomies.return_value = load_taxonomies()

                progress = validate_draft_progress(
                    object_id="kb-source-root-progress",
                    revision_id=str(created["revision_id"]),
                    database_path=database_path,
                    source_root=source_root,
                )

            runtime_class.assert_called_once_with(source_root=source_root)
            self.assertEqual(progress["blueprint"].blueprint_id, "runbook")
            self.assertEqual(progress["completion"]["draft_progress_state"], "blocked")

    def test_completion_state_distinguishes_internal_references_from_weak_external_evidence(self) -> None:
        blueprint = get_blueprint("runbook")
        completion = compute_completion_state(
            blueprint=blueprint,
            section_content={
                "identity": {
                    "object_id": "kb-evidence-posture",
                    "title": "Evidence Posture",
                    "canonical_path": "knowledge/runbooks/evidence-posture.md",
                },
                "stewardship": {
                    "summary": "Exercise evidence posture warnings.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "status": "draft",
                    "review_cadence": "quarterly",
                    "audience": "service_desk",
                    "systems": ["<VPN_SERVICE>"],
                    "tags": ["vpn"],
                    "related_services": ["Remote Access"],
                    "related_object_ids": ["kb-troubleshooting-vpn-connectivity"],
                    "change_summary": "Seed evidence posture coverage.",
                },
                "purpose": {"use_when": "Use when validating evidence posture signals."},
                "prerequisites": {"prerequisites": ["Open the ticket."]},
                "procedure": {"steps": ["Run the guided step."]},
                "verification": {"verification": ["Confirm the result."]},
                "rollback": {"rollback": ["Undo the change."]},
                "boundaries": {"boundaries_and_escalation": "Escalate after two failures.", "related_knowledge_notes": ""},
                "evidence": {
                    "citations": [
                        {
                            "source_title": "VPN Troubleshooting",
                            "source_type": "document",
                            "source_ref": "knowledge/troubleshooting/vpn-connectivity.md",
                            "note": "Internal cross-reference.",
                            "captured_at": None,
                            "integrity_hash": None,
                            "validity_status": "verified",
                        },
                        {
                            "source_title": "Import manifest",
                            "source_type": "document",
                            "source_ref": "migration/import-manifest.yml",
                            "note": "Migration provenance.",
                            "captured_at": None,
                            "integrity_hash": None,
                            "validity_status": "unverified",
                        },
                    ]
                },
            },
            taxonomies=load_taxonomies(),
        )

        evidence_posture = completion["evidence_posture"]
        self.assertEqual(evidence_posture["internal_reference_count"], 1)
        self.assertEqual(evidence_posture["weak_external_evidence_count"], 1)
        self.assertEqual(evidence_posture["posture"], "mixed_support")
        self.assertIn(
            "Evidence: 1 external/manual citation(s) remain weak because the write surface has not recorded capture time and integrity hash.",
            completion["warnings"],
        )
