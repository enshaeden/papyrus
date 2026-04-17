from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.read_models.reader_object_nav import reader_object_nav_tree
from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.infrastructure.repositories.knowledge_repo import upsert_search_document


def ready_runbook_body(summary: str) -> str:
    return (
        "## Use When\n\n"
        + summary.strip()
        + "\n\n## Boundaries And Escalation\n\n"
        + "Escalate when the documented workflow does not restore the expected operator outcome."
    )


def runbook_payload(
    object_id: str,
    canonical_path: str,
    title: str,
    *,
    object_lifecycle_state: str = "active",
) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Reader tree payload for {title.lower()}",
        "knowledge_object_type": "runbook",
        "object_lifecycle_state": object_lifecycle_state,
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": ["Directory"],
        "tags": ["reader"],
        "created": "2026-04-10",
        "updated": "2026-04-10",
        "last_reviewed": "2026-04-10",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": [],
        "prerequisites": ["Open the request."],
        "steps": ["Complete the task."],
        "verification": ["Confirm the outcome."],
        "rollback": ["Undo the change."],
        "citations": [
            {
                "source_title": "System model",
                "source_type": "document",
                "source_ref": "knowledge/system-model.md",
                "note": "Reader navigation fixture evidence.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": [],
        "references": [{"title": "System model", "path": "knowledge/system-model.md"}],
        "change_log": [{"date": "2026-04-10", "summary": "Initial.", "author": "tests"}],
    }


def collect_object_ids(nodes: list[dict[str, object]]) -> list[str]:
    object_ids: list[str] = []
    for node in nodes:
        if str(node.get("kind") or "") == "group":
            group_object = node.get("object")
            if isinstance(group_object, dict):
                object_ids.append(str(group_object["object_id"]))
            object_ids.extend(collect_object_ids(list(node.get("children") or [])))
        else:
            object_ids.append(str(node["object_id"]))
    return object_ids


def find_group(nodes: list[dict[str, object]], label: str) -> dict[str, object]:
    for node in nodes:
        if str(node.get("kind") or "") == "group" and str(node.get("label") or "") == label:
            return node
    raise AssertionError(f"group not found: {label}")


class ReaderObjectNavReadModelTests(unittest.TestCase):
    def _create_revision(
        self,
        workflow: GovernanceWorkflow,
        *,
        object_id: str,
        title: str,
        canonical_path: str,
        approved: bool = True,
    ):
        created = workflow.create_object(
            object_id=object_id,
            object_type="runbook",
            title=title,
            summary=f"Reader tree coverage for {title.lower()}",
            owner="workflow_owner",
            team="IT Operations",
            canonical_path=canonical_path,
            actor="tests",
        )
        revision = workflow.create_revision(
            object_id=created.object_id,
            normalized_payload=runbook_payload(
                created.object_id, created.canonical_path, created.title
            ),
            body_markdown=ready_runbook_body("Exercise reader tree coverage."),
            actor="tests",
            change_summary="Initial reader tree revision.",
        )
        if approved:
            workflow.submit_for_review(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                actor="tests",
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approve reader tree coverage.",
            )
        return created, revision

    def _upsert_search_row(
        self,
        database_path: Path,
        *,
        object_id: str,
        revision_id: str,
        title: str,
        summary: str,
        path: str,
        revision_review_state: str = "approved",
        object_lifecycle_state: str = "active",
    ) -> None:
        connection = sqlite3.connect(database_path)
        try:
            upsert_search_document(
                connection,
                object_id=object_id,
                revision_id=revision_id,
                title=title,
                summary=summary,
                object_type="runbook",
                legacy_type=None,
                object_lifecycle_state=object_lifecycle_state,
                owner="workflow_owner",
                team="IT Operations",
                trust_state="trusted",
                revision_review_state=revision_review_state,
                draft_progress_state="ready_for_review",
                source_sync_state="applied",
                freshness_rank=0,
                citation_health_rank=0,
                ownership_rank=0,
                path=path,
                search_text=title,
            )
            connection.commit()
        finally:
            connection.close()

    def test_reader_tree_uses_visible_object_paths_and_expands_current_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            accounts, accounts_revision = self._create_revision(
                workflow,
                object_id="kb-accounts",
                title="Accounts Hub",
                canonical_path="knowledge/accounts.md",
            )
            licensing, licensing_revision = self._create_revision(
                workflow,
                object_id="kb-licensing",
                title="Licensing",
                canonical_path="knowledge/licensing.md",
            )
            passwords, passwords_revision = self._create_revision(
                workflow,
                object_id="kb-passwords",
                title="Passwords",
                canonical_path="knowledge/passwords.md",
            )
            hardware, hardware_revision = self._create_revision(
                workflow,
                object_id="kb-hardware",
                title="Hardware",
                canonical_path="knowledge/hardware.md",
            )
            mdm, mdm_revision = self._create_revision(
                workflow,
                object_id="kb-mdm",
                title="MDM Guide",
                canonical_path="knowledge/mdm.md",
            )
            secret, secret_revision = self._create_revision(
                workflow,
                object_id="kb-secret",
                title="Secret Draft",
                canonical_path="knowledge/secret.md",
                approved=False,
            )

            self._upsert_search_row(
                database_path,
                object_id=accounts.object_id,
                revision_id=accounts_revision.revision_id,
                title=accounts.title,
                summary="Accounts summary.",
                path="accounts",
            )
            self._upsert_search_row(
                database_path,
                object_id=licensing.object_id,
                revision_id=licensing_revision.revision_id,
                title=licensing.title,
                summary="Licensing summary.",
                path="accounts/licensing",
            )
            self._upsert_search_row(
                database_path,
                object_id=passwords.object_id,
                revision_id=passwords_revision.revision_id,
                title=passwords.title,
                summary="Passwords summary.",
                path="accounts/licensing/passwords",
            )
            self._upsert_search_row(
                database_path,
                object_id=hardware.object_id,
                revision_id=hardware_revision.revision_id,
                title=hardware.title,
                summary="Hardware summary.",
                path="hardware",
            )
            self._upsert_search_row(
                database_path,
                object_id=mdm.object_id,
                revision_id=mdm_revision.revision_id,
                title=mdm.title,
                summary="MDM summary.",
                path="hardware/mdm",
            )
            self._upsert_search_row(
                database_path,
                object_id=secret.object_id,
                revision_id=secret_revision.revision_id,
                title=secret.title,
                summary="Secret draft summary.",
                path="accounts/secret",
                revision_review_state="in_progress",
            )

            tree = reader_object_nav_tree(
                current_object_id=passwords.object_id,
                current_path="accounts/licensing/passwords",
                current_canonical_path=passwords.canonical_path,
                database_path=database_path,
            )

            self.assertEqual(tree["label"], "Browse objects")
            self.assertNotIn(secret.object_id, collect_object_ids(list(tree["nodes"])))

            accounts_group = find_group(list(tree["nodes"]), "Accounts")
            self.assertTrue(accounts_group["expanded"])
            self.assertEqual(accounts_group["object"]["object_id"], accounts.object_id)
            self.assertEqual(accounts_group["object"]["label"], "Accounts Hub")

            licensing_group = find_group(list(accounts_group["children"]), "Licensing")
            self.assertTrue(licensing_group["expanded"])
            self.assertEqual(licensing_group["object"]["object_id"], licensing.object_id)

            passwords_leaf = list(licensing_group["children"])[0]
            self.assertEqual(passwords_leaf["kind"], "object")
            self.assertEqual(passwords_leaf["object_id"], passwords.object_id)
            self.assertTrue(passwords_leaf["current"])

            hardware_group = find_group(list(tree["nodes"]), "Hardware")
            self.assertFalse(hardware_group["expanded"])
            self.assertEqual(hardware_group["object"]["object_id"], hardware.object_id)
            self.assertEqual(list(hardware_group["children"])[0]["object_id"], mdm.object_id)

    def test_reader_tree_falls_back_to_canonical_path_and_other_group(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            ordering, ordering_revision = self._create_revision(
                workflow,
                object_id="kb-ordering",
                title="Ordering",
                canonical_path="knowledge/hardware/ordering.md",
            )
            pathless, pathless_revision = self._create_revision(
                workflow,
                object_id="kb-other",
                title="Other Notes",
                canonical_path="knowledge/other-notes.md",
            )

            self._upsert_search_row(
                database_path,
                object_id=ordering.object_id,
                revision_id=ordering_revision.revision_id,
                title=ordering.title,
                summary="Ordering summary.",
                path="   ",
            )
            self._upsert_search_row(
                database_path,
                object_id=pathless.object_id,
                revision_id=pathless_revision.revision_id,
                title=pathless.title,
                summary="Other notes summary.",
                path=" ",
            )

            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    "UPDATE knowledge_objects SET canonical_path = '' WHERE object_id = ?",
                    (pathless.object_id,),
                )
                connection.commit()
            finally:
                connection.close()

            tree = reader_object_nav_tree(
                current_object_id=ordering.object_id,
                current_path="   ",
                current_canonical_path=ordering.canonical_path,
                database_path=database_path,
            )

            hardware_group = find_group(list(tree["nodes"]), "Hardware")
            self.assertTrue(hardware_group["expanded"])
            ordering_leaf = list(hardware_group["children"])[0]
            self.assertEqual(ordering_leaf["object_id"], ordering.object_id)
            self.assertTrue(ordering_leaf["current"])

            other_group = find_group(list(tree["nodes"]), "Other")
            self.assertFalse(other_group["expanded"])
            other_leaf = list(other_group["children"])[0]
            self.assertEqual(other_leaf["object_id"], pathless.object_id)
            self.assertEqual(other_leaf["label"], "Other Notes")


if __name__ == "__main__":
    unittest.main()
