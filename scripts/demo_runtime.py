#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.application.demo_flow import DEMO_SOURCE_ROOT, build_operator_demo_runtime
from papyrus.infrastructure.paths import ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a demo runtime with realistic operator-readiness tension.")
    parser.add_argument(
        "--db",
        default=str(ROOT / "build" / "demo-knowledge.db"),
        help="Path to the demo SQLite runtime database.",
    )
    parser.add_argument(
        "--source-root",
        default=str(DEMO_SOURCE_ROOT),
        help="Writable source root used for demo writeback and evidence snapshots.",
    )
    args = parser.parse_args()

    database_path = Path(args.db)
    source_root = Path(args.source_root)
    for sibling in (database_path, database_path.with_name(database_path.name + "-shm"), database_path.with_name(database_path.name + "-wal")):
        if sibling.exists():
            sibling.unlink()
    if source_root.exists():
        shutil.rmtree(source_root)

    result = build_operator_demo_runtime(database_path=database_path, source_root=source_root)
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
