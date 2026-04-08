from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from papyrus.infrastructure.paths import GENERATED_DIR, ROOT


@dataclass(frozen=True)
class EvidenceSnapshot:
    relative_path: str
    absolute_path: Path
    integrity_hash: str


class EvidenceStore:
    def __init__(self, root_path: Path = ROOT):
        self.root_path = Path(root_path).resolve()

    @property
    def storage_root(self) -> Path:
        return (self.root_path / GENERATED_DIR.relative_to(ROOT) / "evidence").resolve()

    def store_snapshot(self, *, citation_id: str, source_path: str | Path) -> EvidenceSnapshot:
        source = Path(source_path).expanduser().resolve()
        if not source.exists() or not source.is_file():
            raise ValueError(f"evidence snapshot source does not exist: {source}")

        target_dir = self.storage_root / citation_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / source.name
        shutil.copy2(source, target_path)
        digest = hashlib.sha256(target_path.read_bytes()).hexdigest()[:16]
        return EvidenceSnapshot(
            relative_path=target_path.relative_to(self.root_path).as_posix(),
            absolute_path=target_path,
            integrity_hash=digest,
        )

    def resolve_snapshot_path(self, snapshot_path: str) -> Path:
        candidate = Path(snapshot_path)
        if candidate.is_absolute():
            return candidate
        return (self.root_path / snapshot_path).resolve()

    def snapshot_exists(self, snapshot_path: str) -> bool:
        return self.resolve_snapshot_path(snapshot_path).exists()
