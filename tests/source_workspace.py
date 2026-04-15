from __future__ import annotations

from pathlib import Path
from shutil import copytree


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SOURCE_ROOT = ROOT / "tests" / "fixtures" / "source_workspace"


def fixture_source_root() -> Path:
    return FIXTURE_SOURCE_ROOT


def copy_fixture_source_workspace(destination: Path) -> Path:
    target = Path(destination).resolve()
    copytree(FIXTURE_SOURCE_ROOT, target, dirs_exist_ok=True)
    return target
