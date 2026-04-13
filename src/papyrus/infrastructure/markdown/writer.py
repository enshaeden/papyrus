from __future__ import annotations

import datetime as dt
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.infrastructure.markdown.serializer import slugify
from papyrus.infrastructure.paths import ROOT

OBJECT_TYPE_DEFAULT_DIRS = {
    "runbook": "runbooks",
    "known_error": "known-errors",
    "service_record": "services",
}


class SourceWriteConflictError(ValueError):
    """Raised when the canonical source does not match the expected pre-write state."""


@dataclass(frozen=True)
class MarkdownWriteResult:
    file_path: Path
    previous_text: str | None
    new_text: str
    backup_path: Path | None
    changed: bool


class MarkdownWriter:
    def __init__(self, root_path: Path = ROOT, authority: PolicyAuthority | None = None):
        self.root_path = Path(root_path).resolve()
        self.authority = authority or PolicyAuthority.from_repository_policy()

    @property
    def canonical_roots(self) -> tuple[Path, Path]:
        roots = self.authority.canonical_write_roots(source_root=self.root_path)
        return roots[0], roots[1]

    @property
    def backup_root(self) -> Path:
        return self.authority.backup_root(source_root=self.root_path)

    def resolve_path(
        self,
        *,
        object_type: str,
        canonical_path: str | None,
        object_id: str,
        title: str,
    ) -> Path:
        normalized = str(canonical_path or "").strip()
        if normalized:
            return self.authority.resolve_canonical_target_path(
                source_root=self.root_path,
                canonical_path=normalized,
            )

        folder = OBJECT_TYPE_DEFAULT_DIRS.get(object_type, "objects")
        filename = slugify(title or object_id) or object_id
        return self.authority.resolve_canonical_target_path(
            source_root=self.root_path,
            canonical_path=f"knowledge/{folder}/{filename}.md",
        )

    def read_current_text(
        self,
        *,
        object_type: str,
        canonical_path: str | None,
        object_id: str,
        title: str,
    ) -> tuple[Path, str | None]:
        file_path = self.resolve_path(
            object_type=object_type,
            canonical_path=canonical_path,
            object_id=object_id,
            title=title,
        )
        current_text = file_path.read_text(encoding="utf-8") if file_path.exists() else None
        return file_path, current_text

    def would_conflict(
        self,
        *,
        current_text: str | None,
        expected_previous_text: str | None,
        new_text: str,
    ) -> bool:
        if current_text == new_text:
            return False
        return current_text != expected_previous_text

    def write_text(
        self,
        *,
        object_type: str,
        canonical_path: str | None,
        object_id: str,
        title: str,
        text: str,
        expected_previous_text: str | None = None,
    ) -> MarkdownWriteResult:
        file_path, current_text = self.read_current_text(
            object_type=object_type,
            canonical_path=canonical_path,
            object_id=object_id,
            title=title,
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if self.would_conflict(
            current_text=current_text,
            expected_previous_text=expected_previous_text,
            new_text=text,
        ):
            raise SourceWriteConflictError(
                f"canonical source changed unexpectedly for {object_id}: {file_path}"
            )
        if current_text == text:
            return MarkdownWriteResult(
                file_path=file_path,
                previous_text=current_text,
                new_text=text,
                backup_path=None,
                changed=False,
            )

        backup_path = self._write_backup(
            object_id=object_id, file_path=file_path, previous_text=current_text
        )
        self._atomic_write(file_path, text)
        return MarkdownWriteResult(
            file_path=file_path,
            previous_text=current_text,
            new_text=text,
            backup_path=backup_path,
            changed=True,
        )

    def restore(self, *, file_path: Path, previous_text: str | None) -> None:
        self._ensure_canonical_root(file_path.resolve())
        if previous_text is None:
            if file_path.exists():
                file_path.unlink()
            self._cleanup_empty_parents(file_path.parent)
            return
        self._atomic_write(file_path, previous_text)

    def _write_backup(
        self, *, object_id: str, file_path: Path, previous_text: str | None
    ) -> Path | None:
        if previous_text is None:
            return None
        backup_dir = self.backup_root / slugify(object_id)
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
        backup_path = backup_dir / f"{timestamp}-{file_path.name}"
        self._atomic_write(backup_path, previous_text)
        return backup_path

    def _atomic_write(self, file_path: Path, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(
            prefix=".papyrus-writeback-", suffix=".tmp", dir=str(file_path.parent)
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
            os.replace(temp_path, file_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def _ensure_canonical_root(self, file_path: Path) -> None:
        for root in self.canonical_roots:
            try:
                file_path.relative_to(root)
                return
            except ValueError:
                continue
        raise ValueError(
            f"canonical Markdown path must stay under knowledge/ or archive/knowledge/: {file_path}"
        )

    def _cleanup_empty_parents(self, directory: Path) -> None:
        stop_roots = set(self.canonical_roots)
        current = directory
        while current not in stop_roots and current.exists():
            try:
                current.rmdir()
            except OSError:
                return
            current = current.parent
