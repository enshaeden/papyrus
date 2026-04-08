from __future__ import annotations

from typing import Any

from papyrus.domain.policies import citation_health_label


def _reason(
    *,
    code: str,
    severity: str,
    summary: str,
    detail: str,
    action: str,
) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "summary": summary,
        "detail": detail,
        "action": action,
    }


def _approval_summary(approval_state: str | None) -> dict[str, str]:
    state = str(approval_state or "unknown")
    if state == "approved":
        return {
            "state": state,
            "summary": "Approved for operator use",
            "detail": "The current revision is approved and can be used if the trust posture is acceptable.",
            "action": "Review trust and evidence signals before acting on high-impact procedures.",
        }
    if state == "in_review":
        return {
            "state": state,
            "summary": "Review in progress",
            "detail": "The current revision is awaiting reviewer decision and should not be treated as approved guidance yet.",
            "action": "Use the last approved guidance or route the item through governance review.",
        }
    if state == "rejected":
        return {
            "state": state,
            "summary": "Revision rejected",
            "detail": "The current revision was rejected and requires author follow-up before it can be trusted or approved.",
            "action": "Inspect the rejection rationale and update the revision before resubmission.",
        }
    if state == "draft":
        return {
            "state": state,
            "summary": "Draft only",
            "detail": "The current revision is still a draft and is not approved for production operator use.",
            "action": "Complete validation and submit the revision for review.",
        }
    if state == "superseded":
        return {
            "state": state,
            "summary": "Superseded revision",
            "detail": "The current revision has been superseded by a later governed state.",
            "action": "Follow the replacement object or newer approved revision.",
        }
    return {
        "state": state,
        "summary": "Approval state unknown",
        "detail": "Papyrus cannot confirm the approval state for the current runtime projection.",
        "action": "Rebuild the runtime and inspect audit history before relying on this object.",
    }


def _suspect_detail(event: dict[str, Any] | None) -> str:
    if not event:
        return "Papyrus marked this object suspect and it needs explicit operator review."
    details = event.get("details") or {}
    reason = str(details.get("reason") or "").strip()
    entity_type = str(details.get("changed_entity_type") or "").strip()
    entity_id = str(details.get("changed_entity_id") or "").strip()
    changed = "Related change detected"
    if entity_type and entity_id:
        changed = f"{entity_type.replace('_', ' ')} '{entity_id}' changed"
    elif entity_type:
        changed = f"{entity_type.replace('_', ' ')} changed"
    if reason:
        return f"{changed}: {reason}"
    return f"{changed}. Papyrus kept the object in suspect posture until it is reviewed."


def build_posture_summary(
    *,
    trust_state: str,
    approval_state: str | None,
    freshness_rank: int,
    citation_health_rank: int,
    ownership_rank: int,
    owner: str,
    current_revision_id: str | None,
    latest_suspect_event: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blocking_failures: list[dict[str, str]] = []
    serious_warnings: list[dict[str, str]] = []
    informational_warnings: list[dict[str, str]] = []

    if not current_revision_id:
        blocking_failures.append(
            _reason(
                code="missing_revision",
                severity="blocking",
                summary="No revision is attached",
                detail="This object shell does not have a current revision, so there is no governed content to read or approve.",
                action="Create a revision before routing the object into operator use.",
            )
        )

    if freshness_rank > 0:
        serious_warnings.append(
            _reason(
                code="review_due",
                severity="serious",
                summary="Review cadence is overdue",
                detail="The object has passed its review cadence and may no longer reflect the current operating environment.",
                action="Refresh the content, validate it, and send it back through review if needed.",
            )
        )

    if citation_health_rank >= 3:
        blocking_failures.append(
            _reason(
                code="citation_broken",
                severity="blocking",
                summary="Evidence target is broken",
                detail="At least one citation target can no longer be resolved, so the supporting evidence is not dependable.",
                action="Repair or replace the broken citation before relying on the guidance.",
            )
        )
    elif citation_health_rank == 2:
        serious_warnings.append(
            _reason(
                code="citation_stale",
                severity="serious",
                summary="Evidence is stale",
                detail="Supporting evidence exists but is marked stale, so the claims need re-verification.",
                action="Re-check the cited source and capture a refreshed citation.",
            )
        )
    elif citation_health_rank == 1:
        serious_warnings.append(
            _reason(
                code="citation_unverified",
                severity="serious",
                summary="Evidence is weak or unverified",
                detail="The current revision depends on missing or unverified citation capture, so the operator should treat it as lower-confidence guidance.",
                action="Prefer verified evidence before using this for escalation-heavy or irreversible work.",
            )
        )

    if latest_suspect_event is not None or trust_state == "suspect":
        serious_warnings.append(
            _reason(
                code="manual_suspect" if latest_suspect_event is not None else "suspect_posture",
                severity="serious",
                summary="Marked suspect",
                detail=_suspect_detail(latest_suspect_event),
                action="Inspect the audit trail and related dependencies before using the guidance.",
            )
        )

    if ownership_rank > 0 or not owner.strip():
        informational_warnings.append(
            _reason(
                code="ownership_unclear",
                severity="informational",
                summary="Owner is still generic",
                detail="Ownership uses a placeholder or missing value, so escalation routing may be ambiguous even if the content is otherwise usable.",
                action="Replace the placeholder owner with an accountable team or person.",
            )
        )

    approval = _approval_summary(approval_state)
    trust_summary = (
        blocking_failures[0]["summary"]
        if blocking_failures
        else serious_warnings[0]["summary"]
        if serious_warnings
        else informational_warnings[0]["summary"]
        if informational_warnings
        else "No active trust warnings"
    )
    trust_detail = (
        blocking_failures[0]["detail"]
        if blocking_failures
        else serious_warnings[0]["detail"]
        if serious_warnings
        else informational_warnings[0]["detail"]
        if informational_warnings
        else "Freshness, evidence, and governance checks are currently within expected bounds."
    )
    return {
        "trust_state": trust_state,
        "approval": approval,
        "blocking_failures": blocking_failures,
        "serious_warnings": serious_warnings,
        "informational_warnings": informational_warnings,
        "trust_summary": trust_summary,
        "trust_detail": trust_detail,
        "citation_health_label": citation_health_label(citation_health_rank),
    }
