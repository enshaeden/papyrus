from __future__ import annotations

from urllib.parse import urlencode

from papyrus.application.role_visibility import (
    ADMIN_ROLE,
    READER_ROLE,
    normalize_role,
)
from papyrus.interfaces.web.view_helpers import quoted_path


def home_url(role: str | None = None) -> str:
    normalized_role = normalize_role(role)
    if normalized_role == READER_ROLE:
        return "/read"
    if normalized_role == ADMIN_ROLE:
        return "/admin/overview"
    return "/review"


def search_url(role: str | None = None) -> str:
    del role
    return "/read"


def object_url(object_id: str) -> str:
    encoded_object_id = quoted_path(object_id)
    return f"/read/object/{encoded_object_id}"


def object_history_url(object_id: str) -> str:
    encoded_object_id = quoted_path(object_id)
    return f"/read/object/{encoded_object_id}/revisions"


def write_new_url() -> str:
    return "/write/new"


def write_object_start_url(object_id: str) -> str:
    return f"/write/object/{quoted_path(object_id)}/start"


def write_object_url(
    object_id: str, *, revision_id: str | None = None, section_id: str | None = None
) -> str:
    location = f"/write/object/{quoted_path(object_id)}"
    params = {
        key: value
        for key, value in {
            "revision_id": revision_id,
            "section": section_id,
        }.items()
        if str(value or "").strip()
    }
    if not params:
        return location
    return f"{location}?{urlencode(params)}"


def write_submit_url(object_id: str, revision_id: str) -> str:
    return f"/write/object/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision_id)}"


def import_list_url() -> str:
    return "/import"


def import_detail_url(ingestion_id: str) -> str:
    return f"/import/{quoted_path(ingestion_id)}"


def import_review_url(ingestion_id: str) -> str:
    return f"/import/{quoted_path(ingestion_id)}/review"


def review_queue_url() -> str:
    return "/review"


def review_decision_url(object_id: str, revision_id: str) -> str:
    return f"/review/object/{quoted_path(object_id)}/{quoted_path(revision_id)}"


def review_assignment_url(object_id: str, revision_id: str) -> str:
    return review_decision_url(object_id, revision_id) + "/assign"


def supersede_url(object_id: str) -> str:
    return f"/review/object/{quoted_path(object_id)}/supersede"


def archive_url(object_id: str) -> str:
    return f"/review/object/{quoted_path(object_id)}/archive"


def suspect_url(object_id: str) -> str:
    return f"/review/object/{quoted_path(object_id)}/suspect"


def evidence_revalidation_url(object_id: str) -> str:
    return f"/review/object/{quoted_path(object_id)}/evidence/revalidate"


def oversight_url() -> str:
    return "/governance"


def activity_url() -> str:
    return "/review/activity"


def validation_runs_url() -> str:
    return "/review/validation-runs"


def validation_run_new_url() -> str:
    return validation_runs_url() + "/new"


def service_catalog_url() -> str:
    return "/governance/services"


def service_url(service_id: str) -> str:
    return f"{service_catalog_url()}/{quoted_path(service_id)}"


def impact_object_url(object_id: str) -> str:
    return f"/review/impact/object/{quoted_path(object_id)}"


def impact_service_url(service_id: str) -> str:
    return f"/review/impact/service/{quoted_path(service_id)}"
