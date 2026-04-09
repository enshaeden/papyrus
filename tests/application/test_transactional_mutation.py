from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.infrastructure.transactional_mutation import MutationConflictError, TransactionalMutation


class TransactionalMutationTests(unittest.TestCase):
    def test_recover_pending_mutation_rolls_back_applied_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "example.md"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("before\n", encoding="utf-8")
            authority = PolicyAuthority.from_repository_policy()

            with TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-recover-test",
                mutation_type="source_sync_apply",
                object_id="kb-mutation-recover",
                authority=authority,
            ) as mutation:
                mutation.stage_write(
                    target_path=target_path,
                    previous_text="before\n",
                    new_text="after\n",
                )
                mutation.apply_files()

            self.assertEqual(target_path.read_text(encoding="utf-8"), "after\n")
            recovered = TransactionalMutation.recover_pending_mutations(
                source_root=source_root,
                authority=authority,
            )
            self.assertEqual(recovered, ["mutation-recover-test"])
            self.assertEqual(target_path.read_text(encoding="utf-8"), "before\n")
            journal_path = authority.mutation_root(source_root=source_root) / "mutation-recover-test" / "journal.json"
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            self.assertEqual(journal["status"], "rolled_back")

    def test_object_lock_rejects_concurrent_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            authority = PolicyAuthority.from_repository_policy()
            with TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-lock-a",
                mutation_type="source_sync_apply",
                object_id="kb-locked-object",
                authority=authority,
            ):
                with self.assertRaises(MutationConflictError):
                    with TransactionalMutation(
                        source_root=source_root,
                        mutation_id="mutation-lock-b",
                        mutation_type="source_sync_apply",
                        object_id="kb-locked-object",
                        authority=authority,
                    ):
                        self.fail("concurrent mutation lock was not enforced")
