from __future__ import annotations

import argparse
import sys

from papyrus.application.workspace import (
    WorkspaceSourceRequiredError,
    require_workspace_source_root,
)
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate workspace-only migration rationale and collection indexes."
    )
    parser.add_argument(
        "--workspace-root",
        default=None,
        help="Workspace source root that contains canonical knowledge trees.",
    )
    args = parser.parse_args(argv)
    try:
        workspace_root = require_workspace_source_root(
            args.workspace_root,
            operation="migration validation",
        )
    except WorkspaceSourceRequiredError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors: list[str] = []
    rationale_path = workspace_root / RATIONALE_PATH.relative_to(ROOT)
    if not rationale_path.exists():
        errors.append(
            f"missing migration rationale: {rationale_path.relative_to(workspace_root).as_posix()}"
        )
    else:
        rationale_text = rationale_path.read_text(encoding="utf-8")
        for removed_artifact in REMOVED_ARTIFACT_PATTERNS:
            if removed_artifact in rationale_text:
                errors.append(
                    f"migration rationale still references removed artifact: {removed_artifact}"
                )

    for candidate in EXPECTED_COLLECTION_INDEXES:
        workspace_candidate = workspace_root / candidate.relative_to(ROOT)
        if not workspace_candidate.exists():
            errors.append(
                f"missing collection index: {workspace_candidate.relative_to(workspace_root).as_posix()}"
            )

    if render_errors(errors):
        return 1

    print(
        "migration validation passed | "
        f"record={rationale_path.relative_to(workspace_root).as_posix()} | "
        f"collection_indexes={len(EXPECTED_COLLECTION_INDEXES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
