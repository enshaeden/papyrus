from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewActionResult:
    values: dict[str, str]
    errors: dict[str, list[str]]
    cleaned_data: dict[str, object]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _result(values: dict[str, str], errors: dict[str, list[str]], cleaned_data: dict[str, object]) -> ReviewActionResult:
    return ReviewActionResult(values=values, errors=errors, cleaned_data=cleaned_data)


def validate_submit_form(values: dict[str, str]) -> ReviewActionResult:
    return _result(values, {}, {"notes": values.get("notes", "").strip() or None})


def validate_assignment_form(values: dict[str, str]) -> ReviewActionResult:
    errors: dict[str, list[str]] = {}
    reviewer = values.get("reviewer", "").strip()
    if not reviewer:
        errors.setdefault("reviewer", []).append("Reviewer is required.")
    due_at_raw = values.get("due_at", "").strip()
    due_at = None
    if due_at_raw:
        try:
            due_at = dt.datetime.fromisoformat(f"{due_at_raw}T00:00:00+00:00")
        except ValueError:
            errors.setdefault("due_at", []).append("Due date must be ISO formatted.")
    return _result(
        values,
        errors,
        {
            "reviewer": reviewer,
            "notes": values.get("notes", "").strip() or None,
            "due_at": due_at,
        },
    )


def validate_decision_form(values: dict[str, str], *, require_notes: bool) -> ReviewActionResult:
    errors: dict[str, list[str]] = {}
    reviewer = values.get("reviewer", "").strip()
    notes = values.get("notes", "").strip()
    if not reviewer:
        errors.setdefault("reviewer", []).append("Reviewer is required.")
    if require_notes and not notes:
        errors.setdefault("notes", []).append("A rejection rationale is required.")
    return _result(values, errors, {"reviewer": reviewer, "notes": notes or None})


def validate_supersede_form(values: dict[str, str]) -> ReviewActionResult:
    errors: dict[str, list[str]] = {}
    replacement_object_id = values.get("replacement_object_id", "").strip()
    notes = values.get("notes", "").strip()
    if not replacement_object_id:
        errors.setdefault("replacement_object_id", []).append("Replacement object ID is required.")
    if not notes:
        errors.setdefault("notes", []).append("A supersession rationale is required.")
    return _result(
        values,
        errors,
        {
            "replacement_object_id": replacement_object_id,
            "notes": notes,
        },
    )


def validate_suspect_form(values: dict[str, str]) -> ReviewActionResult:
    errors: dict[str, list[str]] = {}
    reason = values.get("reason", "").strip()
    changed_entity_type = values.get("changed_entity_type", "").strip()
    changed_entity_id = values.get("changed_entity_id", "").strip()
    if not reason:
        errors.setdefault("reason", []).append("A suspect rationale is required.")
    if not changed_entity_type:
        errors.setdefault("changed_entity_type", []).append("Changed entity type is required.")
    return _result(
        values,
        errors,
        {
            "reason": reason,
            "changed_entity_type": changed_entity_type,
            "changed_entity_id": changed_entity_id or None,
        },
    )


def validate_validation_run_form(values: dict[str, str]) -> ReviewActionResult:
    errors: dict[str, list[str]] = {}
    run_id = values.get("run_id", "").strip()
    run_type = values.get("run_type", "").strip()
    status = values.get("status", "").strip()
    finding_count_raw = values.get("finding_count", "").strip()
    details = values.get("details", "").strip()
    if not run_id:
        errors.setdefault("run_id", []).append("Run ID is required.")
    if not run_type:
        errors.setdefault("run_type", []).append("Run type is required.")
    if not status:
        errors.setdefault("status", []).append("Status is required.")
    try:
        finding_count = int(finding_count_raw or "0")
        if finding_count < 0:
            raise ValueError
    except ValueError:
        errors.setdefault("finding_count", []).append("Finding count must be zero or greater.")
        finding_count = 0
    return _result(
        values,
        errors,
        {
            "run_id": run_id,
            "run_type": run_type,
            "status": status,
            "finding_count": finding_count,
            "details": details or None,
        },
    )
