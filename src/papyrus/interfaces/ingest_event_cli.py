from __future__ import annotations

import argparse
import json
from pathlib import Path

from papyrus.application.commands import ingest_event_command
from papyrus.infrastructure.paths import DB_PATH


def infer_entity_type(event_type: str, entity_id: str) -> str:
    if event_type == "service_change":
        return "service"
    if event_type.startswith("validation_"):
        return "knowledge_object" if entity_id.startswith("kb-") else "service"
    if event_type.startswith("evidence_"):
        return "evidence"
    return "knowledge_object" if entity_id.startswith("kb-") else "service"


def load_payload(path: str | None) -> dict[str, object]:
    if not path:
        return {}
    payload_path = Path(path)
    with payload_path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError("payload file must contain a JSON object")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest a structured change, validation, or evidence event into Papyrus."
    )
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the runtime SQLite database.")
    parser.add_argument(
        "--type",
        dest="event_type",
        required=True,
        help="Event type, for example service_change or validation_failure.",
    )
    parser.add_argument(
        "--entity", required=True, help="Changed service, object, or evidence identifier."
    )
    parser.add_argument(
        "--entity-type",
        help="Optional entity type override. Defaults are inferred from the event type and entity value.",
    )
    parser.add_argument("--payload", help="Path to a JSON object payload file.")
    parser.add_argument(
        "--source",
        default="local",
        choices=("local", "external", "connector"),
        help="Event source.",
    )
    parser.add_argument(
        "--actor", default="local.operator", help="Actor to record in the event and audit trail."
    )
    parser.add_argument(
        "--occurred-at", help="Optional ISO-8601 timestamp. Defaults to now in UTC."
    )
    args = parser.parse_args()

    payload = load_payload(args.payload)
    entity_type = args.entity_type or infer_entity_type(args.event_type, args.entity)
    result = ingest_event_command(
        database_path=args.db,
        event_type=args.event_type,
        source=args.source,
        entity_type=entity_type,
        entity_id=args.entity,
        payload=payload,
        actor=args.actor,
        occurred_at=args.occurred_at,
    )
    print(
        f"{result.event_id} | {result.event_type} | {result.entity_type}={result.entity_id} | impacted={result.impacted_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
