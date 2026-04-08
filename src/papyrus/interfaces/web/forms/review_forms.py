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
