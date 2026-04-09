from __future__ import annotations

from papyrus.domain.blueprints import Blueprint
from papyrus.domain.blueprints_seed import BLUEPRINTS


_BLUEPRINTS_BY_ID = {blueprint.blueprint_id: blueprint for blueprint in BLUEPRINTS}


def list_blueprints() -> list[Blueprint]:
    return list(BLUEPRINTS)


def get_blueprint(blueprint_id: str) -> Blueprint:
    try:
        return _BLUEPRINTS_BY_ID[str(blueprint_id).strip()]
    except KeyError as exc:
        raise ValueError(f"unsupported blueprint: {blueprint_id}") from exc
