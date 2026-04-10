from __future__ import annotations

import argparse

from papyrus.application.commands import (
    preview_writeback_command,
    restore_writeback_command,
    writeback_all_command,
    writeback_object_command,
)
from papyrus.application.queries import knowledge_object_detail
from papyrus.infrastructure.paths import DB_PATH


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect, apply, or restore governed source writeback for canonical Markdown."
    )
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the runtime SQLite database.")
    parser.add_argument("--actor", default="papyrus-source-sync", help="Actor to record in the audit trail.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview_parser = subparsers.add_parser(
        "preview",
        help="Preview the canonical Markdown that a revision would write.",
    )
    preview_parser.add_argument("--object", dest="object_id", required=True, help="Knowledge object ID.")
    preview_parser.add_argument(
        "--revision",
        dest="revision_id",
        default=None,
        help="Revision ID to preview. Defaults to the object's current revision.",
    )

    writeback_parser = subparsers.add_parser("writeback", help="Write the current approved revision for one object.")
    writeback_parser.add_argument("--object", dest="object_id", required=True, help="Knowledge object ID.")

    subparsers.add_parser("writeback-all", help="Write all current approved revisions.")

    restore_parser = subparsers.add_parser(
        "restore-last",
        help="Restore the previous canonical source state from the most recent writeback backup.",
    )
    restore_parser.add_argument("--object", dest="object_id", required=True, help="Knowledge object ID.")
    restore_parser.add_argument(
        "--revision",
        dest="revision_id",
        default=None,
        help="Limit restore lookup to a specific revision ID.",
    )

    args = parser.parse_args()

    if args.command == "preview":
        revision_id = args.revision_id
        if not revision_id:
            detail = knowledge_object_detail(args.object_id, database_path=args.db)
            current_revision = detail.get("current_revision")
            revision_id = str(current_revision["revision_id"]) if current_revision else ""
        if not revision_id:
            raise SystemExit(f"{args.object_id} has no current revision to preview")
        result = preview_writeback_command(
            database_path=args.db,
            object_id=args.object_id,
            revision_id=revision_id,
        )
        print(f"{result.object_id} | {result.revision_id} | {result.file_path}")
        print(f"conflict_detected={str(result.conflict_detected).lower()}")
        print("changed_fields=" + (", ".join(result.changed_fields) if result.changed_fields else "none"))
        print("changed_sections=" + (", ".join(result.changed_sections) if result.changed_sections else "none"))
        return 0

    if args.command == "writeback":
        result = writeback_object_command(database_path=args.db, object_id=args.object_id, actor=args.actor)
        print(f"{result.object_id} | {result.revision_id} | {result.file_path}")
        return 0

    if args.command == "restore-last":
        result = restore_writeback_command(
            database_path=args.db,
            object_id=args.object_id,
            revision_id=args.revision_id,
            actor=args.actor,
        )
        print(f"{result.object_id} | {result.revision_id or 'unknown-revision'} | {result.file_path}")
        print(f"restored_event_id={result.restored_event_id}")
        print(f"restored_to_missing={str(result.restored_to_missing).lower()}")
        if result.backup_path is not None:
            print(f"backup_path={result.backup_path}")
        return 0

    results = writeback_all_command(database_path=args.db, actor=args.actor)
    print(f"writeback_count={len(results)}")
    for result in results:
        print(f"{result.object_id} | {result.revision_id} | {result.file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
