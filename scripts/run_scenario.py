#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.application.demo_flow import DEMO_SOURCE_ROOT, OPERATOR_SCENARIOS, run_operator_scenario
from papyrus.infrastructure.paths import ROOT


def _reset_runtime_artifacts(database_path: Path, source_root: Path) -> None:
    for sibling in (
        database_path,
        database_path.with_name(database_path.name + "-shm"),
        database_path.with_name(database_path.name + "-wal"),
    ):
        if sibling.exists():
            sibling.unlink()
    if source_root.exists():
        shutil.rmtree(source_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Papyrus operator pressure scenario against a fresh local demo runtime.")
    parser.add_argument("scenario", choices=[name.replace("_", "-") for name in OPERATOR_SCENARIOS], help="Scenario to execute.")
    parser.add_argument("--db", default=str(ROOT / "build" / "scenario-knowledge.db"), help="Path to the scenario SQLite runtime database.")
    parser.add_argument("--source-root", default=str(ROOT / "build" / "scenario-source"), help="Writable source root used for scenario writeback and evidence snapshots.")
    parser.add_argument("--actor", default="local.operator", help="Actor recorded in scenario-generated audit events.")
    args = parser.parse_args()

    database_path = Path(args.db)
    source_root = Path(args.source_root)
    _reset_runtime_artifacts(database_path, source_root)
    result = run_operator_scenario(
        scenario=args.scenario,
        database_path=database_path,
        source_root=source_root,
        actor=args.actor,
    )
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
