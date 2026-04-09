from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from papyrus.application.blueprint_registry import list_blueprints
from papyrus.interfaces.web.view_helpers import OBJECT_ID_PATTERN, parse_csvish


@dataclass(frozen=True)
class ObjectFormResult:
    values: dict[str, str]
    errors: dict[str, list[str]]
    cleaned_data: dict[str, Any]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def default_object_values() -> dict[str, str]:
    return {
        "object_id": "",
        "object_type": "runbook",
        "title": "",
        "summary": "",
        "owner": "",
        "team": "",
        "canonical_path": "",
        "review_cadence": "quarterly",
        "status": "draft",
        "systems": "",
        "tags": "",
    }


def validate_object_form(
    values: dict[str, str],
    *,
    taxonomies: dict[str, dict[str, Any]],
) -> ObjectFormResult:
    errors: dict[str, list[str]] = {}

    def add_error(field: str, message: str) -> None:
        errors.setdefault(field, []).append(message)

    object_id = values["object_id"].strip()
    canonical_path = values["canonical_path"].strip()
    object_type = values["object_type"].strip()
    title = values["title"].strip()
    summary = values["summary"].strip()
    owner = values["owner"].strip()
    team = values["team"].strip()
    review_cadence = values["review_cadence"].strip()
    status = values["status"].strip()

    if not object_id:
        add_error("object_id", "Object ID is required.")
    elif not OBJECT_ID_PATTERN.fullmatch(object_id):
        add_error("object_id", "Object ID must match kb-slug format.")

    supported_blueprints = {blueprint.blueprint_id for blueprint in list_blueprints()}
    if object_type not in supported_blueprints:
        add_error("object_type", "Choose a supported object type.")
    if not title:
        add_error("title", "Title is required.")
    if not summary:
        add_error("summary", "Summary is required.")
    if not owner:
        add_error("owner", "Owner is required.")
    if team not in taxonomies["teams"]["allowed_values"]:
        add_error("team", "Choose a valid team.")
    if review_cadence not in taxonomies["review_cadences"]["allowed_values"]:
        add_error("review_cadence", "Choose a valid review cadence.")
    if status not in taxonomies["statuses"]["allowed_values"]:
        add_error("status", "Choose a valid lifecycle status.")
    if not canonical_path:
        add_error("canonical_path", "Canonical path is required.")
    elif not canonical_path.startswith("knowledge/") or not canonical_path.endswith(".md"):
        add_error("canonical_path", "Canonical path must stay under knowledge/ and end in .md.")

    cleaned_data = {
        "object_id": object_id,
        "object_type": object_type,
        "title": title,
        "summary": summary,
        "owner": owner,
        "team": team,
        "canonical_path": canonical_path,
        "review_cadence": review_cadence,
        "status": status,
        "systems": parse_csvish(values["systems"]),
        "tags": parse_csvish(values["tags"]),
    }
    return ObjectFormResult(values=values, errors=errors, cleaned_data=cleaned_data)
