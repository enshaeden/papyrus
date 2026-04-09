from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from papyrus.application.policy_authority import PolicyAuthority


class MutationConflictError(RuntimeError):
    """Raised when another mutation already owns the same object lock."""


@dataclass(frozen=True)
class StagedFileChange:
    action: str
    target_path: str
    previous_text: str | None
    new_text: str | None


@dataclass
class MutationJournal:
    mutation_id: str
    mutation_type: str
    object_id: str | None
    root_path: str
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)
    file_changes: list[StagedFileChange] = field(default_factory=list)


class TransactionalMutation:
    def __init__(
        self,
        *,
        source_root: Path,
        mutation_id: str,
        mutation_type: str,
        object_id: str | None,
        authority: PolicyAuthority | None = None,
    ) -> None:
        self.source_root = Path(source_root).resolve()
        self.mutation_id = mutation_id
        self.mutation_type = mutation_type
        self.object_id = object_id
        self.authority = authority or PolicyAuthority.from_repository_policy()
        self.mutation_root = self.authority.mutation_root(source_root=self.source_root)
        self.lock_root = self.mutation_root / "locks"
        self.journal_dir = self.mutation_root / mutation_id
        self.journal_path = self.journal_dir / "journal.json"
        self._applied_changes: list[StagedFileChange] = []
        self._lock_path: Path | None = None
        self._started = False
        self._closed = False
        self.journal = MutationJournal(
            mutation_id=mutation_id,
            mutation_type=mutation_type,
            object_id=object_id,
            root_path=self.source_root.as_posix(),
            status="prepared",
        )

    def start(self) -> "TransactionalMutation":
        if self._started:
            return self
        self._acquire_lock()
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self._write_journal()
        self._started = True
        self._closed = False
        return self

    def close(self) -> None:
        if self._closed:
            return
        self._release_lock()
        self._closed = True

    def __enter__(self) -> "TransactionalMutation":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None and self.journal.status not in {"rolled_back", "committed"}:
            self.rollback_files()
            self.mark_rolled_back()
        self.close()

    def stage_write(self, *, target_path: Path, previous_text: str | None, new_text: str) -> None:
        self.journal.file_changes.append(
            StagedFileChange(
                action="write",
                target_path=target_path.resolve(strict=False).as_posix(),
                previous_text=previous_text,
                new_text=new_text,
            )
        )
        self._write_journal()

    def stage_delete(self, *, target_path: Path, previous_text: str | None) -> None:
        self.journal.file_changes.append(
            StagedFileChange(
                action="delete",
                target_path=target_path.resolve(strict=False).as_posix(),
                previous_text=previous_text,
                new_text=None,
            )
        )
        self._write_journal()

    def set_metadata(self, **metadata: Any) -> None:
        self.journal.metadata.update(metadata)
        self._write_journal()

    def execute(
        self,
        *,
        connection: sqlite3.Connection,
        mutate: Callable[["TransactionalMutation"], Any],
        commit_connection: bool = True,
    ) -> Any:
        result = mutate(self)
        try:
            self.apply_files()
            if commit_connection:
                connection.commit()
                self.mark_committed()
            return result
        except Exception:
            if commit_connection:
                connection.rollback()
            self.rollback_files()
            self.mark_rolled_back()
            raise

    def apply_files(self) -> None:
        self.journal.status = "applying"
        self._write_journal()
        for change in self.journal.file_changes:
            target_path = Path(change.target_path)
            if change.action == "write":
                target_path.parent.mkdir(parents=True, exist_ok=True)
                self._atomic_write(target_path, str(change.new_text or ""))
            elif change.action == "delete":
                if target_path.exists():
                    target_path.unlink()
                    self._cleanup_empty_parents(target_path.parent)
            self._applied_changes.append(change)
        self.journal.status = "applied"
        self._write_journal()

    def rollback_files(self) -> None:
        for change in reversed(self._applied_changes):
            target_path = Path(change.target_path)
            if change.previous_text is None:
                if target_path.exists():
                    target_path.unlink()
                    self._cleanup_empty_parents(target_path.parent)
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            self._atomic_write(target_path, change.previous_text)
        self._applied_changes = []

    def mark_committed(self) -> None:
        self.journal.status = "committed"
        self._write_journal()

    def mark_rolled_back(self) -> None:
        self.journal.status = "rolled_back"
        self._write_journal()

    @classmethod
    def recover_pending_mutations(
        cls,
        *,
        source_root: Path,
        authority: PolicyAuthority | None = None,
    ) -> list[str]:
        current_authority = authority or PolicyAuthority.from_repository_policy()
        mutation_root = current_authority.mutation_root(source_root=Path(source_root).resolve())
        if not mutation_root.exists():
            return []
        recovered: list[str] = []
        for journal_path in sorted(mutation_root.glob("*/journal.json")):
            payload = json.loads(journal_path.read_text(encoding="utf-8"))
            if str(payload.get("status")) in {"committed", "rolled_back"}:
                continue
            mutation = cls(
                source_root=Path(payload["root_path"]),
                mutation_id=str(payload["mutation_id"]),
                mutation_type=str(payload["mutation_type"]),
                object_id=payload.get("object_id"),
                authority=current_authority,
            )
            mutation.journal = MutationJournal(
                mutation_id=str(payload["mutation_id"]),
                mutation_type=str(payload["mutation_type"]),
                object_id=payload.get("object_id"),
                root_path=str(payload["root_path"]),
                status=str(payload["status"]),
                metadata=dict(payload.get("metadata") or {}),
                file_changes=[
                    StagedFileChange(
                        action=str(item["action"]),
                        target_path=str(item["target_path"]),
                        previous_text=item.get("previous_text"),
                        new_text=item.get("new_text"),
                    )
                    for item in payload.get("file_changes", [])
                ],
            )
            mutation._applied_changes = list(mutation.journal.file_changes)
            mutation.rollback_files()
            mutation.mark_rolled_back()
            recovered.append(mutation.mutation_id)
        return recovered

    def _write_journal(self) -> None:
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "mutation_id": self.journal.mutation_id,
            "mutation_type": self.journal.mutation_type,
            "object_id": self.journal.object_id,
            "root_path": self.journal.root_path,
            "status": self.journal.status,
            "metadata": self.journal.metadata,
            "file_changes": [
                {
                    "action": item.action,
                    "target_path": item.target_path,
                    "previous_text": item.previous_text,
                    "new_text": item.new_text,
                }
                for item in self.journal.file_changes
            ],
        }
        self.journal_path.write_text(
            json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    def _acquire_lock(self) -> None:
        self.lock_root.mkdir(parents=True, exist_ok=True)
        lock_name = self.object_id or self.mutation_id
        self._lock_path = self.lock_root / f"{lock_name}.lock"
        try:
            fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise MutationConflictError(
                f"another governed mutation is already in progress for {lock_name}"
            ) from exc
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(self.mutation_id)

    def _release_lock(self) -> None:
        if self._lock_path is not None and self._lock_path.exists():
            self._lock_path.unlink()

    def _atomic_write(self, target_path: Path, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(
            prefix=".papyrus-mutation-",
            suffix=".tmp",
            dir=str(target_path.parent),
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            os.replace(temp_path, target_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _cleanup_empty_parents(self, directory: Path) -> None:
        stop_roots = {
            *(self.authority.canonical_write_roots(source_root=self.source_root)),
            self.authority.archive_root(source_root=self.source_root),
            self.source_root,
        }
        current = directory
        while current not in stop_roots and current.exists():
            try:
                current.rmdir()
            except OSError:
                return
            current = current.parent
