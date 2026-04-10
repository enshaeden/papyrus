from __future__ import annotations

import datetime as dt
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


class MutationRecoveryError(RuntimeError):
    """Raised when Papyrus cannot recover pending governed mutations safely."""


DEFAULT_STALE_LOCK_SECONDS = 900
TERMINAL_MUTATION_STATUSES = {"committed", "rolled_back"}
RECOVERABLE_MUTATION_STATUSES = {"prepared", "applying", "applied"}


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _isoformat_utc(value: dt.datetime | None = None) -> str:
    return (value or _now_utc()).isoformat()


def _parse_timestamp(value: object) -> dt.datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


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
    created_at: str = field(default_factory=_isoformat_utc)
    updated_at: str = field(default_factory=_isoformat_utc)
    applied_change_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    file_changes: list[StagedFileChange] = field(default_factory=list)


@dataclass(frozen=True)
class MutationRecoveryRecord:
    mutation_id: str | None
    object_id: str | None
    outcome: str
    detail: str


@dataclass(frozen=True)
class MutationRecoverySummary:
    records: tuple[MutationRecoveryRecord, ...]

    @property
    def recovered_mutation_ids(self) -> list[str]:
        return [
            str(record.mutation_id)
            for record in self.records
            if record.mutation_id and record.outcome == "rolled_back"
        ]

    @property
    def failures(self) -> tuple[MutationRecoveryRecord, ...]:
        return tuple(record for record in self.records if record.outcome == "failed")

    def raise_for_failures(self) -> None:
        if not self.failures:
            return
        reasons = "; ".join(record.detail for record in self.failures)
        raise MutationRecoveryError(f"automatic mutation recovery failed: {reasons}")


@dataclass(frozen=True)
class MutationLockState:
    lock_path: Path
    lock_name: str
    mutation_id: str | None
    object_id: str | None
    created_at: str | None
    age_seconds: float

    @property
    def stale(self) -> bool:
        return self.age_seconds >= DEFAULT_STALE_LOCK_SECONDS


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
        self.journal.applied_change_count = 0
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
            self.journal.applied_change_count = len(self._applied_changes)
            self._write_journal()
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
        stale_lock_seconds: int = DEFAULT_STALE_LOCK_SECONDS,
    ) -> list[str]:
        summary = cls.recover_pending_mutation_state(
            source_root=source_root,
            authority=authority,
            stale_lock_seconds=stale_lock_seconds,
        )
        summary.raise_for_failures()
        return summary.recovered_mutation_ids

    @classmethod
    def recover_pending_mutation_state(
        cls,
        *,
        source_root: Path,
        authority: PolicyAuthority | None = None,
        stale_lock_seconds: int = DEFAULT_STALE_LOCK_SECONDS,
    ) -> MutationRecoverySummary:
        current_authority = authority or PolicyAuthority.from_repository_policy()
        mutation_root = current_authority.mutation_root(source_root=Path(source_root).resolve())
        if not mutation_root.exists():
            return MutationRecoverySummary(records=())

        records: list[MutationRecoveryRecord] = []
        journals_by_id: dict[str, MutationJournal] = {}
        for journal_path in sorted(mutation_root.glob("*/journal.json")):
            try:
                payload = json.loads(journal_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                records.append(
                    MutationRecoveryRecord(
                        mutation_id=journal_path.parent.name,
                        object_id=None,
                        outcome="failed",
                        detail=f"journal {journal_path} is unreadable: {exc}",
                    )
                )
                continue
            journal = cls._journal_from_payload(payload)
            journals_by_id[journal.mutation_id] = journal

        locks_by_name: dict[str, MutationLockState] = {}
        locks_by_mutation_id: dict[str, MutationLockState] = {}
        for lock_path in sorted((mutation_root / "locks").glob("*.lock")):
            lock_state = cls._read_lock_state(lock_path)
            lock_state = MutationLockState(
                lock_path=lock_state.lock_path,
                lock_name=lock_state.lock_name,
                mutation_id=lock_state.mutation_id,
                object_id=lock_state.object_id,
                created_at=lock_state.created_at,
                age_seconds=cls._lock_age_seconds(lock_state),
            )
            locks_by_name[lock_state.lock_name] = lock_state
            if lock_state.mutation_id:
                locks_by_mutation_id[lock_state.mutation_id] = lock_state

        handled_lock_paths: set[Path] = set()
        for mutation_id, journal in sorted(journals_by_id.items()):
            if journal.status in TERMINAL_MUTATION_STATUSES:
                continue
            lock_state = None
            if mutation_id in locks_by_mutation_id:
                lock_state = locks_by_mutation_id[mutation_id]
            elif journal.object_id:
                lock_state = locks_by_name.get(str(journal.object_id))
            if lock_state is not None:
                handled_lock_paths.add(lock_state.lock_path)
                if not cls._is_stale_lock(lock_state, stale_lock_seconds=stale_lock_seconds):
                    records.append(
                        MutationRecoveryRecord(
                            mutation_id=mutation_id,
                            object_id=journal.object_id,
                            outcome="failed",
                            detail=(
                                f"mutation {mutation_id} still holds a live lock for "
                                f"{journal.object_id or lock_state.lock_name}"
                            ),
                        )
                    )
                    continue
            try:
                mutation = cls(
                    source_root=Path(journal.root_path),
                    mutation_id=journal.mutation_id,
                    mutation_type=journal.mutation_type,
                    object_id=journal.object_id,
                    authority=current_authority,
                )
                mutation.journal = journal
                mutation._applied_changes = list(
                    mutation.journal.file_changes[: mutation.journal.applied_change_count]
                )
                if mutation._applied_changes:
                    mutation.rollback_files()
                mutation.mark_rolled_back()
                if lock_state is not None and lock_state.lock_path.exists():
                    lock_state.lock_path.unlink()
                records.append(
                    MutationRecoveryRecord(
                        mutation_id=mutation_id,
                        object_id=journal.object_id,
                        outcome="rolled_back",
                        detail=(
                            f"rolled back pending mutation {mutation_id}"
                            + (
                                f" and reclaimed stale lock {lock_state.lock_path.name}"
                                if lock_state is not None
                                else ""
                            )
                        ),
                    )
                )
            except Exception as exc:
                records.append(
                    MutationRecoveryRecord(
                        mutation_id=mutation_id,
                        object_id=journal.object_id,
                        outcome="failed",
                        detail=f"mutation {mutation_id} could not be recovered safely: {exc}",
                    )
                )

        for lock_path in sorted((mutation_root / "locks").glob("*.lock")):
            if lock_path in handled_lock_paths:
                continue
            lock_state = cls._read_lock_state(lock_path)
            lock_state = MutationLockState(
                lock_path=lock_state.lock_path,
                lock_name=lock_state.lock_name,
                mutation_id=lock_state.mutation_id,
                object_id=lock_state.object_id,
                created_at=lock_state.created_at,
                age_seconds=cls._lock_age_seconds(lock_state),
            )
            journal = journals_by_id.get(str(lock_state.mutation_id or ""))
            if journal is not None and journal.status in TERMINAL_MUTATION_STATUSES:
                if lock_path.exists():
                    lock_path.unlink()
                records.append(
                    MutationRecoveryRecord(
                        mutation_id=lock_state.mutation_id,
                        object_id=lock_state.object_id,
                        outcome="lock_reclaimed",
                        detail=f"reclaimed terminal lock {lock_path.name}",
                    )
                )
                continue
            if cls._is_stale_lock(lock_state, stale_lock_seconds=stale_lock_seconds):
                if lock_path.exists():
                    lock_path.unlink()
                records.append(
                    MutationRecoveryRecord(
                        mutation_id=lock_state.mutation_id,
                        object_id=lock_state.object_id,
                        outcome="lock_reclaimed",
                        detail=f"reclaimed stale lock {lock_path.name}",
                    )
                )
                continue
            records.append(
                MutationRecoveryRecord(
                    mutation_id=lock_state.mutation_id,
                    object_id=lock_state.object_id,
                    outcome="failed",
                    detail=f"live mutation lock blocks startup or command execution: {lock_path.name}",
                )
            )

        return MutationRecoverySummary(records=tuple(records))

    def _write_journal(self) -> None:
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.journal.updated_at = _isoformat_utc()
        payload = {
            "mutation_id": self.journal.mutation_id,
            "mutation_type": self.journal.mutation_type,
            "object_id": self.journal.object_id,
            "root_path": self.journal.root_path,
            "status": self.journal.status,
            "created_at": self.journal.created_at,
            "updated_at": self.journal.updated_at,
            "applied_change_count": self.journal.applied_change_count,
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
            existing = self._read_lock_state(self._lock_path)
            raise MutationConflictError(
                "another governed mutation is already in progress for "
                f"{lock_name}"
                + (
                    f" (mutation_id={existing.mutation_id})"
                    if existing.mutation_id
                    else ""
                )
            ) from exc
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "mutation_id": self.mutation_id,
                        "object_id": self.object_id,
                        "created_at": _isoformat_utc(),
                    },
                    sort_keys=True,
                    ensure_ascii=True,
                )
            )

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

    @staticmethod
    def _journal_from_payload(payload: dict[str, Any]) -> MutationJournal:
        status = str(payload.get("status") or "prepared")
        file_changes = [
            StagedFileChange(
                action=str(item["action"]),
                target_path=str(item["target_path"]),
                previous_text=item.get("previous_text"),
                new_text=item.get("new_text"),
            )
            for item in payload.get("file_changes", [])
        ]
        applied_change_count = int(payload.get("applied_change_count") or 0)
        if "applied_change_count" not in payload and status in {"applying", "applied"}:
            applied_change_count = len(file_changes)
        applied_change_count = max(0, min(applied_change_count, len(file_changes)))
        created_at = str(payload.get("created_at") or payload.get("updated_at") or _isoformat_utc())
        updated_at = str(payload.get("updated_at") or created_at)
        return MutationJournal(
            mutation_id=str(payload["mutation_id"]),
            mutation_type=str(payload["mutation_type"]),
            object_id=payload.get("object_id"),
            root_path=str(payload["root_path"]),
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            applied_change_count=applied_change_count,
            metadata=dict(payload.get("metadata") or {}),
            file_changes=file_changes,
        )

    @staticmethod
    def _read_lock_state(lock_path: Path) -> MutationLockState:
        raw = lock_path.read_text(encoding="utf-8").strip() if lock_path.exists() else ""
        mutation_id: str | None = None
        object_id: str | None = None
        created_at: str | None = None
        if raw:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                mutation_id = raw
            else:
                if isinstance(payload, dict):
                    mutation_id = str(payload.get("mutation_id") or "").strip() or None
                    object_id = str(payload.get("object_id") or "").strip() or None
                    created_at = str(payload.get("created_at") or "").strip() or None
        return MutationLockState(
            lock_path=lock_path,
            lock_name=lock_path.stem,
            mutation_id=mutation_id,
            object_id=object_id,
            created_at=created_at,
            age_seconds=0.0,
        )

    @staticmethod
    def _lock_age_seconds(lock_state: MutationLockState) -> float:
        timestamp = _parse_timestamp(lock_state.created_at)
        if timestamp is None:
            timestamp = dt.datetime.fromtimestamp(lock_state.lock_path.stat().st_mtime, tz=dt.timezone.utc)
        return max(0.0, (_now_utc() - timestamp).total_seconds())

    @staticmethod
    def _is_stale_lock(
        lock_state: MutationLockState,
        *,
        stale_lock_seconds: int,
    ) -> bool:
        return lock_state.age_seconds >= stale_lock_seconds
