from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from papyrus.infrastructure.markdown.serializer import slugify
from papyrus.infrastructure.paths import ROOT


OBJECT_TYPE_DEFAULT_DIRS = {
    "runbook": "runbooks",
    "known_error": "known-errors",
    "service_record": "services",
}

@dataclass(frozen=True)
class MarkdownWriteResult:
    file_path: Path
    previous_text: str | None
    new_text: str


class MarkdownWriter:
    def __init__(self, root_path: Path = ROOT):
        self.root_path = Path(root_path)

    @property
    def canonical_roots(self) -> tuple[Path, Path]:
        return (
            (self.root_path / "knowledge").resolve(),
            (self.root_path / "archive" / "knowledge").resolve(),
        )

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
            candidate = (self.root_path / normalized).resolve()
            self._ensure_canonical_root(candidate)
            return candidate

        folder = OBJECT_TYPE_DEFAULT_DIRS.get(object_type, "objects")
        filename = slugify(title or object_id) or object_id
        candidate = (self.root_path / "knowledge" / folder / f"{filename}.md").resolve()
        self._ensure_canonical_root(candidate)
        return candidate

    def write_text(
        self,
        *,
        object_type: str,
        canonical_path: str | None,
        object_id: str,
        title: str,
        text: str,
    ) -> MarkdownWriteResult:
        file_path = self.resolve_path(
            object_type=object_type,
            canonical_path=canonical_path,
            object_id=object_id,
            title=title,
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        previous_text = file_path.read_text(encoding="utf-8") if file_path.exists() else None
        self._atomic_write(file_path, text)
        return MarkdownWriteResult(
            file_path=file_path,
            previous_text=previous_text,
            new_text=text,
        )

    def restore(self, *, file_path: Path, previous_text: str | None) -> None:
        self._ensure_canonical_root(file_path.resolve())
        if previous_text is None:
            if file_path.exists():
                file_path.unlink()
            self._cleanup_empty_parents(file_path.parent)
            return
        self._atomic_write(file_path, previous_text)

    def _atomic_write(self, file_path: Path, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(prefix=".papyrus-writeback-", suffix=".tmp", dir=str(file_path.parent))
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
        raise ValueError(f"canonical Markdown path must stay under knowledge/ or archive/knowledge/: {file_path}")

    def _cleanup_empty_parents(self, directory: Path) -> None:
        stop_roots = set(self.canonical_roots)
        current = directory
        while current not in stop_roots and current.exists():
            try:
                current.rmdir()
            except OSError:
                return
            current = current.parent
