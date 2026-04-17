from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import ingest_file
from papyrus.application.mapping_flow import convert_to_draft, map_to_blueprint
from papyrus.application.queries import review_detail


def governed_ingest_path(temp_dir: str, filename: str) -> tuple[Path, Path]:
    source_root = Path(temp_dir) / "repo"
    source_path = source_root / "build" / "local-ingest" / filename
    source_path.parent.mkdir(parents=True, exist_ok=True)
    return source_root, source_path


class IngestionToAuthoringIntegrationTests(unittest.TestCase):
    def test_imported_html_runbook_converts_into_the_same_structured_draft_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "runbook.html")
            source_path.write_text(
                "<html><body>"
                "<h1>Access Recovery</h1>"
                "<h2>Procedure</h2>"
                "<ul><li>Confirm identity</li><li>Reset access</li></ul>"
                "<h2>Verification</h2>"
                "<ul><li>User can sign in</li></ul>"
                "</body></html>",
                encoding="utf-8",
            )

            ingested = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            map_to_blueprint(
                ingestion_id=ingested["ingestion_id"],
                blueprint_id="runbook",
                database_path=database_path,
            )
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-access-recovery-imported-html",
                title="Access Recovery",
                canonical_path="knowledge/imported/access-recovery-html.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="quarterly",
                object_lifecycle_state="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            detail = review_detail(
                "kb-access-recovery-imported-html",
                converted["revision_id"],
                database_path=database_path,
            )
            self.assertEqual(detail["object"]["object_type"], "runbook")
            self.assertEqual(
                detail["revision"]["section_content"]["procedure"]["steps"],
                ["Confirm identity", "Reset access"],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["verification"]["verification"],
                ["User can sign in"],
            )

    def test_imported_runbook_stays_honestly_partial_when_required_fields_are_unresolved(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "runbook.md")
            source_path.write_text(
                "# Access Recovery\n\n## Procedure\n\n- Confirm identity\n- Reset access\n\n## Verification\n\n- User can sign in\n",
                encoding="utf-8",
            )

            ingested = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            map_to_blueprint(
                ingestion_id=ingested["ingestion_id"],
                blueprint_id="runbook",
                database_path=database_path,
            )
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-access-recovery-imported",
                title="Access Recovery",
                canonical_path="knowledge/imported/access-recovery.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="quarterly",
                object_lifecycle_state="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            detail = review_detail(
                "kb-access-recovery-imported",
                converted["revision_id"],
                database_path=database_path,
            )
            self.assertEqual(detail["object"]["object_type"], "runbook")
            self.assertEqual(detail["object"]["summary"], "")
            self.assertEqual(detail["revision"]["revision_review_state"], "in_progress")
            self.assertEqual(detail["revision"]["metadata"]["summary"], "")
            self.assertIn("section_content", detail["revision"])
            self.assertEqual(
                detail["revision"]["section_content"]["procedure"]["steps"],
                ["Confirm identity", "Reset access"],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["verification"]["verification"],
                ["User can sign in"],
            )
            self.assertEqual(detail["revision"]["section_content"]["purpose"]["use_when"], "")
            self.assertEqual(detail["revision"]["section_content"]["evidence"]["citations"], [])
            self.assertEqual(
                detail["revision"]["section_content"]["procedure"]["_field_provenance"]["steps"][
                    "status"
                ],
                "mapped",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["purpose"]["_field_provenance"]["use_when"][
                    "status"
                ],
                "manual_required",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["stewardship"]["_field_provenance"][
                    "summary"
                ]["status"],
                "manual_required",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["evidence"]["_field_provenance"]["citations"][
                    "status"
                ],
                "manual_required",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["relationships"]["_field_provenance"][
                    "related_object_ids"
                ]["status"],
                "unresolved",
            )
            self.assertTrue(detail["revision"]["section_completion_map"]["procedure"]["completed"])
            self.assertFalse(detail["revision"]["section_completion_map"]["purpose"]["completed"])
            self.assertNotEqual(detail["revision"]["draft_progress_state"], "ready_for_review")
            self.assertLess(converted["completion"]["completion_percentage"], 100)
            self.assertLess(
                detail["revision"]["section_completion_map"]["purpose"]["completed_field_count"],
                detail["revision"]["section_completion_map"]["purpose"]["required_field_count"],
            )
            self.assertFalse(detail["revision"]["section_completion_map"]["evidence"]["completed"])

    def test_known_error_import_maps_distinct_fragments_to_distinct_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "known-error.md")
            source_path.write_text(
                "# Login failure\n\n"
                "## Symptoms\n\n"
                "- Users cannot sign in\n"
                "- Sessions expire immediately\n\n"
                "## Scope\n\n"
                "Only federated desktop clients are affected.\n\n"
                "## Cause\n\n"
                "A cached token schema mismatch breaks refresh validation.\n\n"
                "## Diagnostic Checks\n\n"
                "- Inspect the token refresh logs\n\n"
                "## Mitigations\n\n"
                "- Clear the stale token cache\n\n"
                "## Detection Notes\n\n"
                "Alert when refresh failures exceed five per minute.\n\n"
                "## Escalation Threshold\n\n"
                "Escalate to identity engineering after two repeated incidents.\n",
                encoding="utf-8",
            )

            ingested = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            map_to_blueprint(
                ingestion_id=ingested["ingestion_id"],
                blueprint_id="known_error",
                database_path=database_path,
            )
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-login-failure-imported",
                title="Login failure",
                canonical_path="knowledge/imported/login-failure.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="after_change",
                object_lifecycle_state="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            detail = review_detail(
                "kb-login-failure-imported",
                converted["revision_id"],
                database_path=database_path,
            )
            self.assertEqual(detail["object"]["summary"], "")
            self.assertEqual(detail["revision"]["metadata"]["summary"], "")
            diagnosis = detail["revision"]["section_content"]["diagnosis"]
            self.assertEqual(
                diagnosis["symptoms"], ["Users cannot sign in", "Sessions expire immediately"]
            )
            self.assertEqual(diagnosis["scope"], "Only federated desktop clients are affected.")
            self.assertEqual(
                diagnosis["cause"], "A cached token schema mismatch breaks refresh validation."
            )
            self.assertNotEqual(
                diagnosis["_field_provenance"]["symptoms"]["source_fragment_id"],
                diagnosis["_field_provenance"]["scope"]["source_fragment_id"],
            )
            self.assertNotEqual(
                diagnosis["_field_provenance"]["scope"]["source_fragment_id"],
                diagnosis["_field_provenance"]["cause"]["source_fragment_id"],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["mitigations"]["permanent_fix_status"], ""
            )
            self.assertEqual(
                detail["revision"]["section_content"]["mitigations"]["_field_provenance"][
                    "permanent_fix_status"
                ]["status"],
                "manual_required",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["escalation"]["detection_notes"],
                "Alert when refresh failures exceed five per minute.",
            )
            self.assertFalse(
                detail["revision"]["section_completion_map"]["mitigations"]["completed"]
            )

    def test_policy_import_uses_explicit_policy_fields_and_stays_partial_without_evidence(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "policy.md")
            source_path.write_text(
                "# Remote Access Change Policy\n\n"
                "## Policy Scope\n\n"
                "Applies to authentication, VPN, and remote access control changes.\n\n"
                "## Controls\n\n"
                "- Require CAB approval before production change\n"
                "- Record a rollback plan before execution\n\n"
                "## Exceptions\n\n"
                "Emergency changes require follow-up review within 24 hours.\n",
                encoding="utf-8",
            )

            ingested = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            map_to_blueprint(
                ingestion_id=ingested["ingestion_id"],
                blueprint_id="policy",
                database_path=database_path,
            )
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-remote-access-policy-imported",
                title="Remote Access Change Policy",
                canonical_path="knowledge/imported/remote-access-change-policy.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="annual",
                object_lifecycle_state="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            detail = review_detail(
                "kb-remote-access-policy-imported",
                converted["revision_id"],
                database_path=database_path,
            )
            self.assertEqual(detail["object"]["object_type"], "policy")
            self.assertEqual(
                detail["revision"]["section_content"]["policy_scope"]["policy_scope"],
                "Applies to authentication, VPN, and remote access control changes.",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["controls"]["controls"],
                [
                    "Require CAB approval before production change",
                    "Record a rollback plan before execution",
                ],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["exceptions"]["exceptions"],
                "Emergency changes require follow-up review within 24 hours.",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["evidence"]["_field_provenance"]["citations"][
                    "status"
                ],
                "manual_required",
            )
            self.assertEqual(detail["object"]["summary"], "")
            self.assertNotEqual(detail["revision"]["draft_progress_state"], "ready_for_review")
            self.assertLess(converted["completion"]["completion_percentage"], 100)

    def test_system_design_import_uses_explicit_system_design_fields_and_keeps_optional_support_blank(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "system-design.md")
            source_path.write_text(
                "# Identity Platform Design\n\n"
                "## Architecture\n\n"
                "Identity broker fronts directory, OAuth, and SAML providers.\n\n"
                "## Dependencies\n\n"
                "- Directory service\n"
                "- MFA provider\n\n"
                "## Interfaces\n\n"
                "- OIDC callback\n"
                "- SCIM provisioning API\n\n"
                "## Failure Modes\n\n"
                "- Signing key drift\n"
                "- Directory sync delay\n\n"
                "## Operational Notes\n\n"
                "Coordinate production changes through platform operations.\n",
                encoding="utf-8",
            )

            ingested = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            map_to_blueprint(
                ingestion_id=ingested["ingestion_id"],
                blueprint_id="system_design",
                database_path=database_path,
            )
            converted = convert_to_draft(
                ingestion_id=ingested["ingestion_id"],
                object_id="kb-identity-platform-design-imported",
                title="Identity Platform Design",
                canonical_path="knowledge/imported/identity-platform-design.md",
                owner="workflow_owner",
                team="IT Operations",
                review_cadence="after_change",
                object_lifecycle_state="draft",
                audience="service_desk",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )

            detail = review_detail(
                "kb-identity-platform-design-imported",
                converted["revision_id"],
                database_path=database_path,
            )
            self.assertEqual(detail["object"]["object_type"], "system_design")
            self.assertEqual(
                detail["revision"]["section_content"]["architecture"]["architecture"],
                "Identity broker fronts directory, OAuth, and SAML providers.",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["dependencies"]["dependencies"],
                ["Directory service", "MFA provider"],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["interfaces"]["interfaces"],
                ["OIDC callback", "SCIM provisioning API"],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["failure_modes"]["common_failure_modes"],
                ["Signing key drift", "Directory sync delay"],
            )
            self.assertEqual(
                detail["revision"]["section_content"]["operations"]["operational_notes"],
                "Coordinate production changes through platform operations.",
            )
            self.assertEqual(
                detail["revision"]["section_content"]["operations"]["support_entrypoints"], []
            )
            self.assertEqual(
                detail["revision"]["section_content"]["operations"]["_field_provenance"][
                    "support_entrypoints"
                ]["status"],
                "unresolved",
            )
            self.assertTrue(detail["revision"]["section_completion_map"]["operations"]["completed"])
            self.assertNotEqual(detail["revision"]["draft_progress_state"], "ready_for_review")
            self.assertLess(converted["completion"]["completion_percentage"], 100)
