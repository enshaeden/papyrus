from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.infrastructure.transactional_mutation import (
    MutationConflictError,
    MutationRecoveryError,
    TransactionalMutation,
)


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

    def test_recover_prepared_mutation_marks_journal_without_touching_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "prepared.md"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("before\n", encoding="utf-8")
            authority = PolicyAuthority.from_repository_policy()

            with TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-prepared-test",
                mutation_type="source_sync_apply",
                object_id="kb-prepared-mutation",
                authority=authority,
            ) as mutation:
                mutation.stage_write(
                    target_path=target_path,
                    previous_text="before\n",
                    new_text="after\n",
                )

            recovered = TransactionalMutation.recover_pending_mutations(
                source_root=source_root,
                authority=authority,
            )
            self.assertEqual(recovered, ["mutation-prepared-test"])
            self.assertEqual(target_path.read_text(encoding="utf-8"), "before\n")
            journal_path = authority.mutation_root(source_root=source_root) / "mutation-prepared-test" / "journal.json"
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
            self.assertEqual(journal["status"], "rolled_back")
            self.assertEqual(journal["applied_change_count"], 0)

    def test_recovery_rolls_back_only_recorded_applied_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_a = source_root / "knowledge" / "runbooks" / "partial-a.md"
            target_b = source_root / "knowledge" / "runbooks" / "partial-b.md"
            target_a.parent.mkdir(parents=True, exist_ok=True)
            target_a.write_text("before-a\n", encoding="utf-8")
            authority = PolicyAuthority.from_repository_policy()

            mutation = TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-partial-test",
                mutation_type="source_sync_apply",
                object_id="kb-partial-mutation",
                authority=authority,
            ).start()
            mutation.stage_write(
                target_path=target_a,
                previous_text="before-a\n",
                new_text="after-a\n",
            )
            mutation.stage_write(
                target_path=target_b,
                previous_text=None,
                new_text="after-b\n",
            )
            first_change = mutation.journal.file_changes[0]
            mutation.journal.status = "applying"
            mutation._write_journal()
            target_a.write_text("after-a\n", encoding="utf-8")
            mutation._applied_changes.append(first_change)
            mutation.journal.applied_change_count = 1
            mutation._write_journal()
            mutation.close()

            recovered = TransactionalMutation.recover_pending_mutations(
                source_root=source_root,
                authority=authority,
            )
            self.assertEqual(recovered, ["mutation-partial-test"])
            self.assertEqual(target_a.read_text(encoding="utf-8"), "before-a\n")
            self.assertFalse(target_b.exists())

    def test_recovery_reclaims_stale_lock_and_pending_journal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "stale-lock.md"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("before\n", encoding="utf-8")
            authority = PolicyAuthority.from_repository_policy()

            mutation = TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-stale-lock",
                mutation_type="source_sync_apply",
                object_id="kb-stale-lock",
                authority=authority,
            ).start()
            mutation.stage_write(
                target_path=target_path,
                previous_text="before\n",
                new_text="after\n",
            )
            mutation.apply_files()

            recovered = TransactionalMutation.recover_pending_mutations(
                source_root=source_root,
                authority=authority,
                stale_lock_seconds=0,
            )
            self.assertEqual(recovered, ["mutation-stale-lock"])
            self.assertEqual(target_path.read_text(encoding="utf-8"), "before\n")
            self.assertFalse((authority.mutation_root(source_root=source_root) / "locks" / "kb-stale-lock.lock").exists())

    def test_recovery_fails_safely_when_live_lock_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "live-lock.md"
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("before\n", encoding="utf-8")
            authority = PolicyAuthority.from_repository_policy()

            mutation = TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-live-lock",
                mutation_type="source_sync_apply",
                object_id="kb-live-lock",
                authority=authority,
            ).start()
            mutation.stage_write(
                target_path=target_path,
                previous_text="before\n",
                new_text="after\n",
            )

            with self.assertRaisesRegex(MutationRecoveryError, "still holds a live lock"):
                TransactionalMutation.recover_pending_mutations(
                    source_root=source_root,
                    authority=authority,
                )
            mutation.close()

    def test_recovery_reclaims_stale_orphan_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            authority = PolicyAuthority.from_repository_policy()
            lock_root = authority.mutation_root(source_root=source_root) / "locks"
            lock_root.mkdir(parents=True, exist_ok=True)
            lock_path = lock_root / "kb-orphan.lock"
            lock_path.write_text(
                json.dumps(
                    {
                        "mutation_id": "mutation-orphan",
                        "object_id": "kb-orphan",
                        "created_at": (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat(),
                    },
                    sort_keys=True,
                    ensure_ascii=True,
                ),
                encoding="utf-8",
            )

            recovered = TransactionalMutation.recover_pending_mutations(
                source_root=source_root,
                authority=authority,
                stale_lock_seconds=60,
            )
            self.assertEqual(recovered, [])
            self.assertFalse(lock_path.exists())

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
