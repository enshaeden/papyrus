from __future__ import annotations

from collections.abc import Iterable

from papyrus.domain.blueprints import Blueprint
from papyrus.domain.blueprints_seed import BLUEPRINTS

PRIMARY_AUTHORING_SCOPE = "primary"
ADVANCED_AUTHORING_SCOPE = "advanced"


def _blueprint_sort_key(blueprint: Blueprint) -> tuple[int, str, str]:
    return (
        int(blueprint.visible_order),
        str(blueprint.display_name).lower(),
        str(blueprint.blueprint_id),
    )


_ORDERED_BLUEPRINTS = tuple(sorted(BLUEPRINTS, key=_blueprint_sort_key))
_BLUEPRINTS_BY_ID = {blueprint.blueprint_id: blueprint for blueprint in _ORDERED_BLUEPRINTS}


def list_blueprints() -> list[Blueprint]:
    return list(_ORDERED_BLUEPRINTS)


def get_blueprint(blueprint_id: str) -> Blueprint:
    try:
        return _BLUEPRINTS_BY_ID[str(blueprint_id).strip()]
    except KeyError as exc:
        raise ValueError(f"unsupported blueprint: {blueprint_id}") from exc


def list_primary_authoring_blueprints() -> list[Blueprint]:
    return [
        blueprint
        for blueprint in _ORDERED_BLUEPRINTS
        if blueprint.authoring_scope == PRIMARY_AUTHORING_SCOPE
    ]


def list_advanced_authoring_blueprints() -> list[Blueprint]:
    return [
        blueprint
        for blueprint in _ORDERED_BLUEPRINTS
        if blueprint.authoring_scope == ADVANCED_AUTHORING_SCOPE
    ]


def list_import_target_blueprints() -> list[Blueprint]:
    return [blueprint for blueprint in _ORDERED_BLUEPRINTS if blueprint.import_target]


def is_primary_authoring_blueprint(blueprint_id: str) -> bool:
    return get_blueprint(blueprint_id).authoring_scope == PRIMARY_AUTHORING_SCOPE


def is_advanced_authoring_blueprint(blueprint_id: str) -> bool:
    return get_blueprint(blueprint_id).authoring_scope == ADVANCED_AUTHORING_SCOPE


def blueprint_label(blueprint_id: str, *, include_scope_note: bool = False) -> str:
    blueprint = get_blueprint(blueprint_id)
    label = blueprint.display_name
    if include_scope_note and blueprint.authoring_scope == ADVANCED_AUTHORING_SCOPE:
        return f"{label} (advanced)"
    return label


def ordered_blueprint_ids(
    blueprint_ids: Iterable[str] | None = None,
    *,
    include_advanced: bool = True,
) -> list[str]:
    selected = None
    if blueprint_ids is not None:
        selected = {str(item).strip() for item in blueprint_ids if str(item).strip()}
    ordered: list[str] = []
    for blueprint in _ORDERED_BLUEPRINTS:
        if not include_advanced and blueprint.authoring_scope != PRIMARY_AUTHORING_SCOPE:
            continue
        if selected is not None and blueprint.blueprint_id not in selected:
            continue
        ordered.append(blueprint.blueprint_id)
    if selected is None:
        return ordered
    ordered_set = set(ordered)
    ordered.extend(sorted(item for item in selected if item not in ordered_set))
    return ordered
