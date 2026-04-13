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
        return "/reader/browse"
    if normalized_role == ADMIN_ROLE:
        return "/admin/overview"
    return "/operator"


def search_url(role: str | None = None) -> str:
    normalized_role = normalize_role(role)
    if normalized_role == READER_ROLE:
        return "/reader/browse"
    if normalized_role == ADMIN_ROLE:
        return "/admin/inspect"
    return "/operator/read"


def object_url(role: str | None, object_id: str) -> str:
    normalized_role = normalize_role(role)
    encoded_object_id = quoted_path(object_id)
    if normalized_role == READER_ROLE:
        return f"/reader/object/{encoded_object_id}"
    if normalized_role == ADMIN_ROLE:
        return f"/admin/inspect/object/{encoded_object_id}"
    return f"/operator/read/object/{encoded_object_id}"


def object_history_url(role: str | None, object_id: str) -> str:
    normalized_role = normalize_role(role)
    encoded_object_id = quoted_path(object_id)
    if normalized_role == ADMIN_ROLE:
        return f"/admin/inspect/object/{encoded_object_id}/revisions"
    return f"/operator/read/object/{encoded_object_id}/revisions"


def write_new_url() -> str:
    return "/operator/write/new"


def write_object_start_url(object_id: str) -> str:
    return f"/operator/write/object/{quoted_path(object_id)}/start"


def write_object_url(
    object_id: str, *, revision_id: str | None = None, section_id: str | None = None
) -> str:
    location = f"/operator/write/object/{quoted_path(object_id)}"
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
    return f"/operator/write/object/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision_id)}"


def import_list_url() -> str:
    return "/operator/import"


def import_detail_url(ingestion_id: str) -> str:
    return f"/operator/import/{quoted_path(ingestion_id)}"


def import_review_url(ingestion_id: str) -> str:
    return f"/operator/import/{quoted_path(ingestion_id)}/review"


def review_queue_url(role: str | None = None) -> str:
    if normalize_role(role) == ADMIN_ROLE:
        return "/admin/review"
    return "/operator/review"


def review_decision_url(role: str | None, object_id: str, revision_id: str) -> str:
    prefix = (
        "/admin/review/object" if normalize_role(role) == ADMIN_ROLE else "/operator/review/object"
    )
    return f"{prefix}/{quoted_path(object_id)}/{quoted_path(revision_id)}"


def review_assignment_url(role: str | None, object_id: str, revision_id: str) -> str:
    return review_decision_url(role, object_id, revision_id) + "/assign"


def supersede_url(role: str | None, object_id: str) -> str:
    prefix = (
        "/admin/review/object" if normalize_role(role) == ADMIN_ROLE else "/operator/review/object"
    )
    return f"{prefix}/{quoted_path(object_id)}/supersede"


def archive_url(role: str | None, object_id: str) -> str:
    prefix = (
        "/admin/review/object" if normalize_role(role) == ADMIN_ROLE else "/operator/review/object"
    )
    return f"{prefix}/{quoted_path(object_id)}/archive"


def suspect_url(role: str | None, object_id: str) -> str:
    prefix = (
        "/admin/review/object" if normalize_role(role) == ADMIN_ROLE else "/operator/review/object"
    )
    return f"{prefix}/{quoted_path(object_id)}/suspect"


def evidence_revalidation_url(role: str | None, object_id: str) -> str:
    prefix = (
        "/admin/review/object" if normalize_role(role) == ADMIN_ROLE else "/operator/review/object"
    )
    return f"{prefix}/{quoted_path(object_id)}/evidence/revalidate"


def governance_url(role: str | None = None) -> str:
    if normalize_role(role) == ADMIN_ROLE:
        return "/admin/governance"
    return "/operator/review/governance"


def activity_url(role: str | None = None) -> str:
    if normalize_role(role) == ADMIN_ROLE:
        return "/admin/audit"
    return "/operator/review/activity"


def validation_runs_url(role: str | None = None) -> str:
    if normalize_role(role) == ADMIN_ROLE:
        return "/admin/validation-runs"
    return "/operator/review/validation-runs"


def validation_run_new_url(role: str | None = None) -> str:
    return validation_runs_url(role) + "/new"


def service_catalog_url(role: str | None = None) -> str:
    if normalize_role(role) == ADMIN_ROLE:
        return "/admin/services"
    return "/operator/read/services"


def service_url(role: str | None, service_id: str) -> str:
    return f"{service_catalog_url(role)}/{quoted_path(service_id)}"


def impact_object_url(role: str | None, object_id: str) -> str:
    prefix = (
        "/admin/impact/object"
        if normalize_role(role) == ADMIN_ROLE
        else "/operator/review/impact/object"
    )
    return f"{prefix}/{quoted_path(object_id)}"


def impact_service_url(role: str | None, service_id: str) -> str:
    prefix = (
        "/admin/impact/service"
        if normalize_role(role) == ADMIN_ROLE
        else "/operator/review/impact/service"
    )
    return f"{prefix}/{quoted_path(service_id)}"
