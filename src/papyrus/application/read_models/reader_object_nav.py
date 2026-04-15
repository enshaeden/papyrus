from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from papyrus.application.role_visibility import READER_ROLE, object_visible_to_role
from papyrus.infrastructure.paths import DB_PATH

from .support import require_runtime_connection

_OTHER_GROUP_KEY = "__other__"
_ACRONYM_SEGMENTS = {
    "api",
    "av",
    "dns",
    "hr",
    "iam",
    "idp",
    "it",
    "jamf",
    "ldap",
    "mdm",
    "mfa",
    "okta",
    "sso",
    "vpn",
}
_LOWERCASE_WORDS = {"and", "as", "at", "by", "for", "in", "of", "on", "or", "to"}
_MARKDOWN_EXTENSION_PATTERN = re.compile(r"\.(md|mdx)$", re.IGNORECASE)


def _humanize_segment(segment: str) -> str:
    if segment == _OTHER_GROUP_KEY:
        return "Other"
    parts = [part for part in re.split(r"[-_]+", segment.strip()) if part]
    if not parts:
        return "Other"
    words: list[str] = []
    for index, part in enumerate(parts):
        token = part.lower()
        if token in _ACRONYM_SEGMENTS:
            words.append(token.upper())
        elif index > 0 and token in _LOWERCASE_WORDS:
            words.append(token)
        else:
            words.append(token.capitalize())
    return " ".join(words)


def _normalized_segments(
    path: str | None,
    *,
    fallback_path: str | None = None,
    object_id: str,
) -> list[str]:
    for candidate in (path, fallback_path):
        normalized = str(candidate or "").strip().replace("\\", "/").strip("/")
        if not normalized:
            continue
        segments = [segment for segment in normalized.split("/") if segment]
        if (
            len(segments) >= 2
            and segments[0].lower() == "archive"
            and segments[1].lower() == "knowledge"
        ):
            segments = segments[2:]
        elif segments and segments[0].lower() == "knowledge":
            segments = segments[1:]
        if segments:
            segments[-1] = _MARKDOWN_EXTENSION_PATTERN.sub("", segments[-1]) or segments[-1]
        cleaned = [segment for segment in segments if segment]
        if cleaned:
            return cleaned
    return [_OTHER_GROUP_KEY, object_id]


def _new_group_node(segment: str) -> dict[str, Any]:
    return {
        "segment": segment,
        "label": _humanize_segment(segment),
        "object": None,
        "children": {},
    }


def _payload_sort_key(node: dict[str, Any]) -> tuple[int, str, str]:
    return (
        0 if str(node.get("kind") or "") == "group" else 1,
        str(node.get("label") or "").casefold(),
        str(node.get("object_id") or node.get("key") or ""),
    )


def _finalize_node(node: dict[str, Any], *, path_segments: tuple[str, ...]) -> dict[str, Any]:
    object_payload = None
    if isinstance(node.get("object"), dict):
        object_payload = dict(node["object"])
    child_payloads = [
        _finalize_node(child, path_segments=path_segments + (segment,))
        for segment, child in sorted(
            dict(node.get("children") or {}).items(),
            key=lambda item: (str(item[1].get("label") or "").casefold(), str(item[0])),
        )
    ]
    if not child_payloads and object_payload is not None:
        return object_payload
    contains_current = bool(object_payload and object_payload.get("current")) or any(
        bool(child.get("contains_current") or child.get("current")) for child in child_payloads
    )
    return {
        "kind": "group",
        "key": "/".join(path_segments),
        "label": str(node["label"]),
        "expanded": contains_current,
        "contains_current": contains_current,
        "object": object_payload,
        "children": sorted(child_payloads, key=_payload_sort_key),
    }


def reader_object_nav_tree(
    *,
    current_object_id: str,
    current_path: str | None,
    current_canonical_path: str | None = None,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                o.object_id,
                o.title,
                o.canonical_path,
                COALESCE(d.path, o.canonical_path) AS path,
                COALESCE(d.object_lifecycle_state, o.object_lifecycle_state) AS object_lifecycle_state,
                COALESCE(
                    d.revision_review_state,
                    r.revision_review_state,
                    CASE WHEN o.current_revision_id IS NULL THEN 'draft' ELSE 'unknown' END
                ) AS revision_review_state
            FROM knowledge_objects AS o
            LEFT JOIN search_documents AS d ON d.object_id = o.object_id
            LEFT JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
            ORDER BY LOWER(COALESCE(d.path, o.canonical_path)), LOWER(o.title), o.object_id
            """
        ).fetchall()
    finally:
        connection.close()

    current_segments = _normalized_segments(
        current_path,
        fallback_path=current_canonical_path,
        object_id=current_object_id,
    )
    root: dict[str, Any] = {"children": {}}
    for row in rows:
        if not object_visible_to_role(
            READER_ROLE,
            object_lifecycle_state=str(row["object_lifecycle_state"] or ""),
            revision_review_state=str(row["revision_review_state"] or ""),
        ):
            continue
        object_id = str(row["object_id"])
        segments = (
            list(current_segments)
            if object_id == current_object_id
            else _normalized_segments(
                str(row["path"]) if row["path"] is not None else None,
                fallback_path=str(row["canonical_path"])
                if row["canonical_path"] is not None
                else None,
                object_id=object_id,
            )
        )
        node = root
        for segment in segments:
            children = node["children"]
            if segment not in children:
                children[segment] = _new_group_node(segment)
            node = children[segment]
        node["object"] = {
            "kind": "object",
            "object_id": object_id,
            "label": str(row["title"]),
            "current": object_id == current_object_id,
        }

    nodes = sorted(
        [
            _finalize_node(child, path_segments=(segment,))
            for segment, child in dict(root.get("children") or {}).items()
        ],
        key=_payload_sort_key,
    )
    return {
        "label": "Browse objects",
        "nodes": nodes,
    }
