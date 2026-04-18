from __future__ import annotations

import datetime as dt
import difflib
import json
import re
from typing import Any

from papyrus.infrastructure.paths import DATE_PATTERN


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def normalize_for_similarity(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return normalize_whitespace(normalized)


def similarity_ratio(left: str, right: str) -> float:
    return difflib.SequenceMatcher(
        None, normalize_for_similarity(left), normalize_for_similarity(right)
    ).ratio()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def ensure_iso_date(value: Any) -> bool:
    if isinstance(value, dt.datetime):
        return False
    if isinstance(value, dt.date):
        return True
    if not isinstance(value, str):
        return False
    if not DATE_PATTERN.match(value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def ensure_iso_date_or_datetime(value: Any) -> bool:
    if value is None:
        return True
    if ensure_iso_date(value):
        return True
    if isinstance(value, dt.datetime):
        return True
    if not isinstance(value, str) or not value.strip():
        return False
    candidate = value.strip().replace("Z", "+00:00")
    try:
        dt.datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return True


def parse_iso_date(value: Any) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(value)


def parse_iso_date_or_datetime(value: Any) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    candidate = str(value).strip().replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(candidate).date()
    except ValueError:
        return dt.date.fromisoformat(candidate)


def date_to_iso(value: Any) -> str:
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def json_dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, default=date_to_iso)


def render_list(items: list[str]) -> str:
    if not items:
        return "- None documented.\n"
    return "".join(f"- {item}\n" for item in items)


def render_reference(reference: dict[str, Any]) -> str:
    parts = [reference["title"]]
    if reference.get("object_id"):
        parts.append(f"object_id: {reference['object_id']}")
    if reference.get("path"):
        parts.append(f"path: `{reference['path']}`")
    if reference.get("url"):
        parts.append(f"url: {reference['url']}")
    if reference.get("note"):
        parts.append(f"note: {reference['note']}")
    return " | ".join(parts)


def render_change_log(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "- None documented.\n"
    return "".join(
        f"- {date_to_iso(entry['date'])} | {entry['author']} | {entry['summary']}\n"
        for entry in entries
    )
