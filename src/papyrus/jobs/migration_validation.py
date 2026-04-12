from __future__ import annotations

import sys
from pathlib import Path

from papyrus.infrastructure.paths import ROOT

RATIONALE_PATH = ROOT / "docs" / "migration" / "seed-migration-rationale.md"
REMOVED_ARTIFACT_PATTERNS = (
    "migration/seed-plan.yml",
    "migration/import-manifest.yml",
)
EXPECTED_COLLECTION_INDEXES = (
    ROOT / "knowledge" / "access" / "index.md",
    ROOT / "knowledge" / "incidents" / "index.md",
    ROOT / "knowledge" / "postmortems" / "index.md",
    ROOT / "knowledge" / "runbooks" / "index.md",
)


def render_errors(errors: list[str]) -> int:
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"migration validation failed with {len(errors)} issue(s)", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    errors: list[str] = []
    if not RATIONALE_PATH.exists():
        errors.append(f"missing migration rationale: {RATIONALE_PATH.relative_to(ROOT).as_posix()}")
    else:
        rationale_text = RATIONALE_PATH.read_text(encoding="utf-8")
        for removed_artifact in REMOVED_ARTIFACT_PATTERNS:
            if removed_artifact in rationale_text:
                errors.append(f"migration rationale still references removed artifact: {removed_artifact}")

    for candidate in EXPECTED_COLLECTION_INDEXES:
        if not candidate.exists():
            errors.append(f"missing collection index: {candidate.relative_to(ROOT).as_posix()}")

    if render_errors(errors):
        return 1

    print(
        "migration validation passed | "
        f"record={RATIONALE_PATH.relative_to(ROOT).as_posix()} | "
        f"collection_indexes={len(EXPECTED_COLLECTION_INDEXES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
