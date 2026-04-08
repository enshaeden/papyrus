#!/usr/bin/env python3
from __future__ import annotations

import argparse

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.application.commands import writeback_all_command, writeback_object_command
from papyrus.infrastructure.paths import DB_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Write approved runtime revisions back to canonical Markdown source.")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the runtime SQLite database.")
    parser.add_argument("--actor", default="papyrus-source-sync", help="Actor to record in the audit trail.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    writeback_parser = subparsers.add_parser("writeback", help="Write the current approved revision for one object.")
    writeback_parser.add_argument("--object", dest="object_id", required=True, help="Knowledge object ID.")

    subparsers.add_parser("writeback-all", help="Write all current approved revisions.")

    args = parser.parse_args()

    if args.command == "writeback":
        result = writeback_object_command(database_path=args.db, object_id=args.object_id, actor=args.actor)
        print(f"{result.object_id} | {result.revision_id} | {result.file_path}")
        return 0

    results = writeback_all_command(database_path=args.db, actor=args.actor)
    print(f"writeback_count={len(results)}")
    for result in results:
        print(f"{result.object_id} | {result.revision_id} | {result.file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
