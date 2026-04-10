from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from papyrus.application.policy_authority import PolicyDecision, policy_decision_payload
from papyrus.domain.lifecycle import TransitionSemantics


class ActionAvailability(StrEnum):
    ALLOWED = "allowed"
    NO_OP = "no_op"
    ILLEGAL = "illegal"


@dataclass(frozen=True)
class ActionDescriptor:
    action_id: str
    label: str
    availability: ActionAvailability
    summary: str
    detail: str
    policy: PolicyDecision | None = None

    @property
    def available(self) -> bool:
        return self.availability in {ActionAvailability.ALLOWED, ActionAvailability.NO_OP}


def action_descriptor_payload(descriptor: ActionDescriptor) -> dict[str, Any]:
    return {
        "action_id": descriptor.action_id,
        "label": descriptor.label,
        "availability": descriptor.availability.value,
        "available": descriptor.available,
        "summary": descriptor.summary,
        "detail": descriptor.detail,
        "policy": policy_decision_payload(descriptor.policy),
    }


def action_from_policy(
    *,
    action_id: str,
    label: str,
    decision: PolicyDecision,
    summary: str | None = None,
    detail: str | None = None,
) -> ActionDescriptor:
    availability = ActionAvailability.ALLOWED
    if decision.transition.semantics == TransitionSemantics.NO_OP:
        availability = ActionAvailability.NO_OP
    elif not decision.allowed:
        availability = ActionAvailability.ILLEGAL
    return ActionDescriptor(
        action_id=action_id,
        label=label,
        availability=availability,
        summary=summary or label,
        detail=detail or decision.operator_message,
        policy=decision,
    )


def action_from_gate(
    *,
    action_id: str,
    label: str,
    available: bool,
    detail: str,
    summary: str | None = None,
    noop: bool = False,
) -> ActionDescriptor:
    availability = ActionAvailability.NO_OP if noop else ActionAvailability.ALLOWED
    if not available:
        availability = ActionAvailability.ILLEGAL
    return ActionDescriptor(
        action_id=action_id,
        label=label,
        availability=availability,
        summary=summary or label,
        detail=detail,
    )
