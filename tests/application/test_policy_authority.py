from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.domain.lifecycle import (
    DraftProgressState,
    IngestionLifecycleState,
    ObjectLifecycleState,
    RevisionReviewState,
    SourceSyncState,
    TransitionSemantics,
)


class PolicyAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authority = PolicyAuthority.from_repository_policy()

    def test_legal_transitions_are_allowed_for_all_lifecycle_machines(self) -> None:
        self.assertTrue(
            self.authority.require_object_lifecycle_transition(
                ObjectLifecycleState.DRAFT.value,
                ObjectLifecycleState.ACTIVE.value,
            ).allowed
        )
        self.assertTrue(
            self.authority.require_revision_review_transition(
                RevisionReviewState.DRAFT.value,
                RevisionReviewState.IN_REVIEW.value,
            ).allowed
        )
        self.assertTrue(
            self.authority.require_draft_progress_transition(
                DraftProgressState.BLOCKED.value,
                DraftProgressState.IN_PROGRESS.value,
            ).allowed
        )
        self.assertTrue(
            self.authority.require_ingestion_transition(
                IngestionLifecycleState.CLASSIFIED.value,
                IngestionLifecycleState.MAPPED.value,
            ).allowed
        )
        self.assertTrue(
            self.authority.require_source_sync_transition(
                SourceSyncState.APPLIED.value,
                SourceSyncState.CONFLICTED.value,
            ).allowed
        )

    def test_illegal_transitions_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "illegal object_lifecycle_state transition"):
            self.authority.require_object_lifecycle_transition(
                ObjectLifecycleState.ACTIVE.value,
                ObjectLifecycleState.DRAFT.value,
            )
        with self.assertRaisesRegex(ValueError, "illegal revision_review_state transition"):
            self.authority.require_revision_review_transition(
                RevisionReviewState.REJECTED.value,
                RevisionReviewState.APPROVED.value,
            )
        with self.assertRaisesRegex(ValueError, "illegal ingestion_state transition"):
            self.authority.require_ingestion_transition(
                IngestionLifecycleState.UPLOADED.value,
                IngestionLifecycleState.CONVERTED.value,
            )

    def test_transition_semantics_distinguish_noop_allowed_and_illegal(self) -> None:
        no_op = self.authority.evaluate_object_lifecycle_transition(
            ObjectLifecycleState.ACTIVE.value,
            ObjectLifecycleState.ACTIVE.value,
        )
        self.assertTrue(no_op.allowed)
        self.assertEqual(no_op.transition.semantics, TransitionSemantics.NO_OP)
        self.assertFalse(no_op.transition.changes_state)

        allowed = self.authority.evaluate_object_lifecycle_transition(
            ObjectLifecycleState.DRAFT.value,
            ObjectLifecycleState.ACTIVE.value,
        )
        self.assertTrue(allowed.allowed)
        self.assertEqual(allowed.transition.semantics, TransitionSemantics.ALLOWED)
        self.assertTrue(allowed.transition.changes_state)

        illegal = self.authority.evaluate_object_lifecycle_transition(
            ObjectLifecycleState.ACTIVE.value,
            ObjectLifecycleState.DRAFT.value,
        )
        self.assertFalse(illegal.allowed)
        self.assertEqual(illegal.transition.semantics, TransitionSemantics.ILLEGAL)
        self.assertIn("illegal object_lifecycle_state transition", illegal.operator_message)

    def test_source_sync_policy_decisions_expose_acknowledgement_and_restore_contracts(
        self,
    ) -> None:
        apply_decision = self.authority.evaluate_source_sync_transition(
            SourceSyncState.PENDING.value,
            SourceSyncState.APPLIED.value,
        )
        self.assertTrue(apply_decision.allowed)
        self.assertEqual(apply_decision.transition.semantics, TransitionSemantics.ALLOWED)
        self.assertEqual(
            apply_decision.required_acknowledgements,
            ("canonical_source_will_change",),
        )
        self.assertEqual(apply_decision.source_of_truth, "canonical_markdown")
        self.assertIn(
            "Canonical Markdown will win after this action", apply_decision.operator_message
        )

        restore_decision = self.authority.evaluate_source_sync_transition(
            SourceSyncState.APPLIED.value,
            SourceSyncState.RESTORED.value,
        )
        self.assertTrue(restore_decision.allowed)
        self.assertEqual(
            restore_decision.required_acknowledgements,
            ("restore_can_remove_current_canonical_text",),
        )
        self.assertIn(
            "Canonical Markdown will win after this action",
            restore_decision.operator_message,
        )

        no_op = self.authority.evaluate_source_sync_transition(
            SourceSyncState.RESTORED.value,
            SourceSyncState.RESTORED.value,
        )
        self.assertTrue(no_op.allowed)
        self.assertEqual(no_op.transition.semantics, TransitionSemantics.NO_OP)
        self.assertIn("action is a no-op", no_op.operator_message)

        illegal = self.authority.evaluate_source_sync_transition(
            SourceSyncState.CONFLICTED.value,
            SourceSyncState.RESTORED.value,
        )
        self.assertFalse(illegal.allowed)
        self.assertEqual(illegal.transition.semantics, TransitionSemantics.ILLEGAL)
        self.assertIn("illegal source_sync_state transition", illegal.operator_message)

    def test_local_ingest_policy_rejects_root_escape_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            allowed_file = source_root / "build" / "local-ingest" / "allowed.md"
            allowed_file.parent.mkdir(parents=True, exist_ok=True)
            allowed_file.write_text("# Allowed\n", encoding="utf-8")
            self.assertEqual(
                self.authority.validate_local_ingest_source_path(
                    source_root=source_root,
                    candidate_path=allowed_file,
                ),
                allowed_file.resolve(strict=True),
            )

            outside_file = Path(temp_dir) / "outside.md"
            outside_file.write_text("# Outside\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside the approved policy roots"):
                self.authority.validate_local_ingest_source_path(
                    source_root=source_root,
                    candidate_path=outside_file,
                )

            symlink_path = source_root / "build" / "local-ingest" / "escape.md"
            try:
                symlink_path.symlink_to(outside_file)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not supported in this environment")
            with self.assertRaisesRegex(ValueError, "outside the approved policy roots"):
                self.authority.validate_local_ingest_source_path(
                    source_root=source_root,
                    candidate_path=symlink_path,
                )

    def test_canonical_path_policy_rejects_traversal_and_symlinked_parents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            with self.assertRaisesRegex(ValueError, "Canonical path must not contain"):
                self.authority.validate_canonical_repo_relative_path("knowledge/../escape.md")

            real_root = Path(temp_dir) / "canonical-real"
            real_root.mkdir(parents=True, exist_ok=True)
            source_root.mkdir(parents=True, exist_ok=True)
            knowledge_link = source_root / "knowledge"
            try:
                knowledge_link.symlink_to(real_root, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are not supported in this environment")
            with self.assertRaisesRegex(ValueError, "Symlink traversal is not allowed"):
                self.authority.resolve_canonical_target_path(
                    source_root=source_root,
                    canonical_path="knowledge/runbooks/test.md",
                )
