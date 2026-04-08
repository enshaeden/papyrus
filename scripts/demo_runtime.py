#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.application.demo_flow import build_operator_demo_runtime
from papyrus.infrastructure.paths import ROOT


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a demo runtime with realistic operator-readiness tension.")
    parser.add_argument(
        "--db",
        default=str(ROOT / "build" / "demo-knowledge.db"),
        help="Path to the demo SQLite runtime database.",
    )
    args = parser.parse_args()

    database_path = Path(args.db)
    for sibling in (database_path, database_path.with_name(database_path.name + "-shm"), database_path.with_name(database_path.name + "-wal")):
        if sibling.exists():
            sibling.unlink()

    result = build_operator_demo_runtime(database_path=database_path)
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
